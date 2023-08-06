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
"""cubicweb-saem-ref server objects for Asalae interactions"""

from datetime import datetime

from cubicweb.predicates import match_kwargs
from cubicweb.server import Service

from cubes.saem_ref.predicates import is_connector, eid_is_etype, eid_has_mirror
from cubes.saem_ref.lib import asalae


def asalae_id(cnx, eid, etype):
    """Retrieve the extid of the mirror of the entity if it is already mirrored, else None.

    This extid corresponds to the primary key of the object in As@lae database.
    """
    with cnx.security_enabled(read=False):
        rset = cnx.execute('String I WHERE M mirror_of X, M extid I, M using_connector C, '
                           'C is AsalaeConnector, X eid %(x)s',
                           {'x': eid})
        if rset:
            etype_, extid = rset[0][0].split()
            assert etype == etype_
            return int(extid)
    return None


class AsalaeSyncEntityService(Service):
    """Synchronize an entity into its corresponding As@lae table."""
    __abstract__ = True

    def call(self, connector_eid, eid):
        connector = self._cw.entity_from_eid(connector_eid)
        entity = self._cw.entity_from_eid(eid)
        mirror_extid = asalae_id(self._cw, eid, entity.cw_etype)
        if mirror_extid is None:
            # Creation.
            id_ = self.create_asalae_entity(connector, entity)
            with self._cw.security_enabled(write=False):
                self._cw.create_entity('MirrorEntity', extid=entity.cw_etype + ' ' + unicode(id_),
                                       mirror_of=eid, using_connector=connector)
        else:
            # Update.
            self.update_asalae_entity(connector, entity, mirror_extid)
            with self._cw.security_enabled(read=False, write=False):
                mirror = entity.reverse_mirror_of[0]
                mirror.cw_set(modification_date=datetime.utcnow())

    def create_asalae_entity(self, connector, entity):
        raise NotImplementedError()

    def update_asalae_entity(self, connector, entity, asalae_id):
        raise NotImplementedError()


class AsalaeSyncAgentService(AsalaeSyncEntityService):
    """Synchronize Agent entity into As@lae organizations table."""
    __regid__ = 'saem_ref.asalae.sync-agent'
    __select__ = is_connector('AsalaeConnector') & eid_is_etype('Agent')

    def create_asalae_entity(self, connector, entity):
        return asalae.create_organization(connector, entity)

    def update_asalae_entity(self, connector, entity, asalae_id):
        asalae.update_organization(connector, entity, asalae_id)


class AsalaeSyncSEDAProfileService(AsalaeSyncEntityService):
    """Synchronize SEDAProfile entity into As@lae adm-profils table."""
    __regid__ = 'saem_ref.asalae.sync-sedaprofile'
    __select__ = (match_kwargs('connector_eid', 'eid') & is_connector('AsalaeConnector') &
                  eid_is_etype('SEDAProfile'))

    def create_asalae_entity(self, connector, entity):
        helper = self._connect(connector)
        data = self._profile2dict(entity)
        return helper.add_profile(**data)

    def update_asalae_entity(self, connector, entity, asalae_id):
        helper = self._connect(connector)
        data = self._profile2dict(entity)
        helper.update_profile(asalae_id, **data)

    def _profile2dict(self, profile):
        adapter = profile.cw_adapt_to('SEDA-0.2.xsd')
        xsd_content = adapter.dump()
        return {'name': profile.title, 'description': profile.description,
                'identifier': profile.ark, 'file_name': adapter.file_name,
                'schema_file': xsd_content}

    def _connect(self, connector):
        helper = asalae.AsalaeHelper(connector)
        helper.login(connector.user, connector.password)
        return helper


class AsalaeDeleteAgentService(Service):
    """Delete an organization in As@lae corresponding to an Agent entity."""
    __regid__ = 'saem_ref.asalae.delete-agent'
    __select__ = is_connector('AsalaeConnector') & eid_is_etype('Agent') & eid_has_mirror()

    def call(self, connector_eid, eid):
        connector = self._cw.entity_from_eid(connector_eid)
        organization_id = asalae_id(self._cw, eid, 'Agent')
        asalae.delete_asalae_organization(connector, organization_id)
        with self._cw.security_enabled(read=False, write=False):
            self._cw.execute('DELETE MirrorEntity M '
                             'WHERE M mirror_of X, M using_connector C,'
                             '      X eid %(x)s, C eid %(c)s',
                             {'x': eid, 'c': connector_eid})
