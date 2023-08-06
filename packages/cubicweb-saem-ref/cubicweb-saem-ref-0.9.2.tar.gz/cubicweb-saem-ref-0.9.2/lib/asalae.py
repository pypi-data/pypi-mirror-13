# copyright 2015 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

"""cubicweb-saem-ref library for As@lae connector."""

from contextlib import contextmanager

import psycopg2
import requests

from logilab.database import get_connection


ASALAE_AGENT_KIND_MAP = {'person': 'Personne',
                         'authority': 'Collectivite',
                         'family': 'Famille'}


class DatabaseError(Exception):
    """Generic error to the Asalae database"""


class DatabaseConnectionError(DatabaseError):
    """Connection error to the Asalae database"""


class DatabaseQueryError(DatabaseError):
    """Connection error to the Asalae database"""


class AsalaeError(Exception):
    """Generic error regarding Asalae instance"""


class SynchronizationError(AsalaeError):
    """Error regarding entities creation/update on Asalae instance"""


class AsalaeConnectionError(AsalaeError):
    """Generic error regarding HTTP connection to the Asalae instance"""


class UnknownHostError(AsalaeConnectionError):
    """The specified Asalae instance url doesn't exist (404 not found)"""


class HostLoginError(AsalaeConnectionError):
    """Wrong login or password"""


class AsalaeHelper(object):
    """Helper class to acess Asalae API (for now just takes into account profiles stuff)"""

    def __init__(self, connector):
        self.connector = connector
        self._url = connector.url
        if not self._url.endswith('/'):
            self._url += '/'
        self._cookies = None

    def login(self, user, psswd):
        """Connect to asal@e instance with (`user`, `psswd`) account."""
        login_params = {'data[User][username]': user, 'data[User][password]': psswd}
        try:
            res = self._post('users/login', data=login_params)
        except Exception as exc:
            raise AsalaeConnectionError(str(exc))
        if res.status_code == 404:
            raise UnknownHostError()
        elif 'Identifiant ou mot de passe incorrect.' in res.text:
            raise HostLoginError()
        self._cookies = res.cookies

    def add_profile(self, identifier, name=None, description=None, schema_file=None,
                    file_name=None):
        """Add the profile described in `schema_file` file content string"""
        data = self._profile_values(identifier, name, description)
        if schema_file:
            schema_file = {'data[Profil][schema_file]': (file_name, schema_file)}
            # upload schema file
            self._post('profils/docUpload', data=data, files=schema_file)
        # create profile
        self._post('profils/add', data=data, files=schema_file)
        with db_connect(self.connector) as conn:
            try:
                cur = conn.cursor()
                cur.execute('SELECT id from "adm-profils" WHERE identifiant = %(ident)s;',
                            {'ident': identifier})
                res = cur.fetchone()
                if not res:
                    raise SynchronizationError()
                return res[0]
            except psycopg2.Error as exc:
                raise DatabaseQueryError(str(exc))

    def update_profile(self, profile_id, identifier, name=None, description=None, schema_file=None,
                       file_name=None):
        """Update profile of id `profile_id`"""
        data = self._profile_values(identifier, name, description)
        data['data[Profil][id]'] = str(profile_id)
        if schema_file:
            schema_file = {'data[Profil][schema_file]': (file_name, schema_file)}
            # This get is necessary so that the docUpload applies on the profile we want to update
            self._get('profils/edit/%d' % profile_id)
            # upload schema file
            self._post('profils/docUpload', data=data, files=schema_file)
        self._post('profils/edit/%d' % profile_id, data=data, files=schema_file)

    def _profile_values(self, identifier, name=None, description=None):
        """Return a dict with http post parameters for profile creation/update"""
        values = {'data[Profil][identifiant]': identifier,
                  'data[Profil][nom]': name or identifier,
                  'data[Profil][schema_xml]': ''}
        if description:
            values['data[Profil][description]'] = description
        return values

    def _post(self, method, data, files=None):
        res = requests.post(self._url + method, data=data, files=files, cookies=self._cookies)
        if not self._cookies:
            self._cookies = res.cookies
        return res

    def _get(self, method):
        return requests.get(self._url + method, cookies=self._cookies)


@contextmanager
def db_connect(connector):
    """Yield a connection to As@lae database using given AsalaeConnector."""
    try:
        yield get_connection(database=connector.database, user=connector.dbuser,
                             password=connector.dbpassword, host=connector.dbhost,
                             port=connector.dbport)
    except psycopg2.Error as exc:
        raise DatabaseConnectionError(str(exc))


def user_id(cur, username):
    """Return the `id` a user in As@lae database from specified username."""
    cur.execute('SELECT id FROM "adm-users" WHERE username = %(value)s;',
                {'value': username})
    return cur.fetchone()[0]


def entity_type_id(cur, agent_kind):
    """Return the `id` of *typeentite* corresponding to specified
    `agent_kind`.
    """
    sql = 'SELECT id FROM "adm-typeentites" WHERE libelle = %(value)s;'
    value = ASALAE_AGENT_KIND_MAP[agent_kind]
    cur.execute(sql, {'value': value})
    return cur.fetchone()[0]


def operator_type_id(cur, archival_role):
    """Return the `id` of *typeacteur* corresponding to specified
    `archival_role`.
    """
    code_type = {'archival': 'A',
                 'control': 'C',
                 'deposit': 'V',
                 'producer': 'P',
                 'enquirer': 'D'}[archival_role]
    sql = 'SELECT id FROM "adm-typeacteurs" WHERE code_type = %(value)s;'
    cur.execute(sql, {'value': code_type})
    return cur.fetchone()[0]


def set_operator_type(cur, organization_id, roles):
    """Set the operator types *typeacteurs* from given `roles` names for an
    organization with id `organization_id`.
    """
    # First fetch current operator types for this organization,
    cur.execute('''SELECT typeacteur_id FROM "organizations_typeacteurs"
                WHERE organization_id = %(id)s''',
                {'id': organization_id})
    current_operator_types = set([x[0] for x in cur.fetchall()])
    operator_types = set([operator_type_id(cur, r) for r in roles])
    # and delete operator types not present anymore.
    removed_operator_types = tuple(current_operator_types - operator_types)
    if removed_operator_types:
        cur.execute('''DELETE FROM "organizations_typeacteurs"
                    WHERE organization_id = %(id)s
                          AND typeacteur_id in %(roles)s;''',
                    {'id': organization_id,
                     'roles': removed_operator_types})
    sql = '''INSERT INTO "organizations_typeacteurs" (organization_id, typeacteur_id)
             VALUES (%(organization_id)s, %(typeacteur_id)s);
          '''
    # Then insert new operator types.
    for role_id in (operator_types - current_operator_types):
        cur.execute(sql, {'organization_id': organization_id,
                          'typeacteur_id': role_id})


def asalae_table_values(agent):
    """Return a dict with As@lae database table colums information coming
    entity.
    """
    return dict(
        identification=agent.isni,
        nom=agent.name,
        date_existence_debut=agent.start_date,
        date_existence_fin=agent.end_date,
        created=agent.creation_date,
        modified=agent.modification_date,
    )


def create_organization(connector, agent):
    """Create an organization ("acteur SEDA") in As@lae database from an Agent
    entity and return the `id` of the Asalae organization.
    """
    asalaeuser = connector.user
    values = asalae_table_values(agent)
    with db_connect(connector) as conn:
        try:
            cur = conn.cursor()
            asalaeuser_id = user_id(cur, asalaeuser)
            values['created_user_id'] = asalaeuser_id
            values['modified_user_id'] = asalaeuser_id
            values['typeentite_id'] = entity_type_id(cur, agent.kind)
            sql = '''INSERT INTO "arc-organizations" (
                identification, nom, parent_id,
                typeentite_id, date_existence_debut, date_existence_fin,
                created, created_user_id, modified, modified_user_id)
                VALUES (%(identification)s, %(nom)s, DEFAULT,
                        %(typeentite_id)s, %(date_existence_debut)s,
                        %(date_existence_fin)s, %(created)s,
                        %(created_user_id)s, %(modified)s,
                        %(modified_user_id)s)
                RETURNING id;
                '''
            cur.execute(sql, values)
            organization_id, = cur.fetchone()
            # Set the operator type ('control', 'archival', etc.)
            set_operator_type(cur, organization_id,
                              [r.name for r in agent.archival_role])
            conn.commit()
            return organization_id
        except psycopg2.Error as exc:
            raise DatabaseQueryError(str(exc))


def update_organization(connector, agent, organization_id):
    """Update an organization ("acteur SEDA") in As@lae database from an Agent
    entity.
    """
    asalaeuser = connector.user
    values = asalae_table_values(agent)
    with db_connect(connector) as conn:
        try:
            cur = conn.cursor()
            asalaeuser_id = user_id(cur, asalaeuser)
            values['modified_user_id'] = asalaeuser_id
            sql = '''UPDATE "arc-organizations"
                SET identification=%(identification)s,
                    nom=%(nom)s,
                    typeentite_id=%(typeentite_id)s,
                    date_existence_debut=%(date_existence_debut)s,
                    date_existence_fin=%(date_existence_fin)s,
                    modified=%(modified)s,
                    modified_user_id=%(modified_user_id)s
                WHERE id=%(id)s;'''
            values['id'] = organization_id
            values['typeentite_id'] = entity_type_id(cur, agent.kind)
            cur.execute(sql, values)
            # Set the operator type ('control', 'archival', etc.)
            set_operator_type(cur, organization_id,
                              [r.name for r in agent.archival_role])
            conn.commit()
        except psycopg2.Error as exc:
            raise DatabaseQueryError(str(exc))


def delete_asalae_organization(connector, organization_id):
    """Delete an organization ("acteur") in As@lae database given its id."""
    with db_connect(connector) as conn:
        cur = conn.cursor()
        cur.execute('DELETE FROM "arc-organizations" WHERE id=%(id)s;'
                    'DELETE FROM "organizations_typeacteurs" '
                    'WHERE organization_id=%(id)s;',
                    {'id': organization_id})
        conn.commit()
