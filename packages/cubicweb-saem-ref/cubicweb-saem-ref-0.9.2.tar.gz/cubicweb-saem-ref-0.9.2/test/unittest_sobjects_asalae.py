"""cubicweb-saem_ref unit tests for sobjects"""

import os
from contextlib import contextmanager
import datetime
import functools

from logilab.database import get_db_helper, get_connection

from cubicweb.devtools.testlib import CubicWebTC

from cubes.saem_ref.lib import asalae

import testutils


class AsalaeMock(testutils.Mock):

    def __init__(self, *args, **kwargs):
        for name in ('login', 'update_profile'):
            meth = functools.partial(self._record, name)
            setattr(self, name, meth)
        assert args[0].cw_etype == 'AsalaeConnector'
        super(AsalaeMock, self).__init__('AsalaeConnector')

    def add_profile(self, **kwargs):
        self._record('add_profile', **kwargs)
        return self._create_ref()


@contextmanager
def get_dbcnx(*args, **kwargs):
    """Context manager arround get_connection"""
    yield get_connection(*args, **kwargs)


def createdb(dbname, cursor, owner, password, sqlfile=None, drop=True, **kwargs):
    """Create a new postgres database initialized using sqlfile"""
    helper = get_db_helper('postgres')
    if dbname in helper.list_databases(cursor):
        if drop:
            cursor.execute('DROP DATABASE "%s"' % dbname)
        else:
            print 'database %s exists, not dropping as requested.' % dbname
            return
    helper.create_database(cursor, dbname, owner=owner, **kwargs)
    print 'database %s created' % dbname
    cmdline = ('psql -h localhost %(dbname)s -U %(dbuser)s -f %(fname)s' %
               {'dbname': dbname, 'dbuser': owner, 'fname': sqlfile})
    if os.system(
            ('PGPASSWORD=%s ' % password) + cmdline + ' > /dev/null 2>&1'):
        raise Exception(
            'failed to initialize postgres database with command:\n' + cmdline)
    print 'database initialized'

class AsalaeSyncTC(CubicWebTC):
    """abstract base class for asalae test cases"""

    # Parameters for As@lae connector overridding default when needed.
    asalae_connector = {
        'database': u'test_cubicweb-saem_ref',
        'dbuser': u'cw_asalae',
        'dbpassword': u'cw_asalae',
        'url': u'http://nonexistant.logilab.org:1111/asalae',
        'user': u'admin',
        'password': u'admin',
    }

    @classmethod
    def setUpClass(cls):
        sqlfile = cls.datapath('asalae_postgres_1.5.sql')
        dbname = cls.asalae_connector['database']
        dbuser = cls.asalae_connector['dbuser']
        dbpassword = cls.asalae_connector['dbpassword']
        try:
            helper = get_db_helper('postgres')
            system_db = helper.system_database()
            with get_dbcnx(database=system_db) as cnx:
                # CREATE DATABASE can't be executed in a transaction
                cnx.set_isolation_level(0)
                cursor = cnx.cursor()
                if not helper.user_exists(cursor, dbuser):
                    helper.create_user(cursor, dbuser, dbpassword)
                    print 'created postgres user', dbuser
                createdb(dbname, cursor, dbuser, dbpassword,
                         sqlfile=sqlfile)
                cnx.commit()
        except:
            cls.__unittest_skip__ = True
            cls.__unittest_skip_why__ = 'fail to create postgres db'

    def setup_database(self):
        with self.admin_access.repo_cnx() as cnx:
            self.connector_eid = cnx.create_entity(
                'AsalaeConnector', **self.asalae_connector).eid
            cnx.commit()


class AsalaeSyncProfileServiceTC(AsalaeSyncTC):
    """Test case for As@lae  profiles synchronization service (HTTP)."""

    def setup_database(self):
        super(AsalaeSyncProfileServiceTC, self).setup_database()
        with self.admin_access.repo_cnx() as cnx:
            def create_entity(etype, **kwargs):
                return cnx.create_entity(etype, **kwargs)
            profile = testutils.setup_seda_profile(cnx, ark=u'1234')
            cnx.commit()
        self.profile_eid = profile.eid

    def call_sync(self, cnx):
        AsalaeMock.reset_events()
        cnx.call_service('saem_ref.asalae.sync-sedaprofile',
                         connector_eid=self.connector_eid,
                         eid=self.profile_eid)

    def test_sync_profile(self):
        # substitute the REST helper by a mock to test interaction of the service with the helper
        with AsalaeMock.mock_applied(asalae, 'AsalaeHelper'):
            with self.admin_access.repo_cnx() as cnx:
                self._test_sync_scheme(cnx)

    def _test_sync_scheme(self, cnx):
        self.call_sync(cnx)
        self.assertEqual(AsalaeMock.events[2][0], 'add_profile')
        self.assertTrue(AsalaeMock.events[2][1]['schema_file'] != '')
        # make sure there is some xml file content, and then remove it because it is huge and it
        # doesn't make sense to check it here
        self.assertTrue(AsalaeMock.events[2][1]['schema_file'] != '')
        AsalaeMock.events[2][1]['schema_file'] = 'xml file content'
        self.assertEqual(AsalaeMock.events,
                         [('__init__', 'AsalaeConnector'),
                          ('login', u'admin', u'admin'),
                          ('add_profile', {'identifier': u'1234',
                                           'name': None,
                                           'description': None,
                                           'file_name': u'1234.xsd',
                                           'schema_file': 'xml file content'})])
        profile = cnx.entity_from_eid(self.profile_eid)
        profile.cw_set(title=u'bob')
        profile.cw_set(description=u'eponge')
        cnx.commit()
        self.call_sync(cnx)
        # same thing for this xml file content
        self.assertTrue(AsalaeMock.events[2][2]['schema_file'] != '')
        AsalaeMock.events[2][2]['schema_file'] = 'xml file content'
        self.assertEqual(AsalaeMock.events,
                         [('__init__', u'AsalaeConnector'),
                          ('login', u'admin', u'admin'),
                          ('update_profile', 1, {'identifier': u'1234',
                                                 'name': u'bob',
                                                 'description': u'eponge',
                                                 'file_name': u'bob.xsd',
                                                 'schema_file': 'xml file content'})])

    def test_error_bad_host(self):
        with self.admin_access.repo_cnx() as cnx:
            with self.assertRaises(asalae.AsalaeConnectionError):
                self.call_sync(cnx)


class AsalaeSyncOrganizationServiceTC(AsalaeSyncTC):
    """Test case for As@lae organizations synchronization service."""

    def test_database_connect_error(self):
        with self.admin_access.repo_cnx() as cnx:
            connector = cnx.entity_from_eid(self.connector_eid)
            connector.cw_set(database=u'invalid')
            cnx.commit()
            kind = cnx.find('AgentKind', name=u'person').one()
            agent = cnx.create_entity('Agent', name=u'bob the archivist',
                                      agent_kind=kind)
            cnx.commit()
            with self.assertRaises(asalae.DatabaseConnectionError) as cm:
                cnx.call_service('saem_ref.asalae.sync-agent',
                                 connector_eid=self.connector_eid, eid=agent.eid)
            self.assertIn('invalid', str(cm.exception))

    def test_database_query_error(self):
        def invalid_entity_type_id(cur, agent_kind):
            cur.execute('vive les schtroumps', {'gargamel': 'pas gentil'})
        orig_entity_type_id = asalae.entity_type_id
        try:
            asalae.entity_type_id = invalid_entity_type_id
            with self.admin_access.repo_cnx() as cnx:
                kind = cnx.find('AgentKind', name=u'person').one()
                agent = cnx.create_entity('Agent', name=u'bob the archivist',
                                          agent_kind=kind)
                cnx.commit()
                with self.assertRaises(asalae.DatabaseQueryError) as cm:
                    cnx.call_service('saem_ref.asalae.sync-agent',
                                     connector_eid=self.connector_eid, eid=agent.eid)
                self.assertIn('syntax', str(cm.exception))
        finally:
            asalae.entity_type_id = orig_entity_type_id

    def test_duplicate_organization(self):
        """Try to create an Agent in Asalae with the same name as another"""
        with self.admin_access.repo_cnx() as cnx:
            kind = cnx.find('AgentKind', name=u'person').one()
            agent = cnx.create_entity('Agent', name=u'Service d\'archives',
                                      agent_kind=kind)
            cnx.commit()
            with self.assertRaises(asalae.DatabaseQueryError) as cm:
                cnx.call_service('saem_ref.asalae.sync-agent',
                                 connector_eid=self.connector_eid, eid=agent.eid)
            self.assertIn('arc-organizations_nom_key', str(cm.exception))

    def test_sync_agent(self):
        self.set_description('agent creation')
        with self.admin_access.repo_cnx() as cnx:
            connector = cnx.entity_from_eid(self.connector_eid)
            roles = [cnx.find('ArchivalRole', name=u'control').one(),
                     cnx.find('ArchivalRole', name=u'deposit').one()]
            kind = cnx.find('AgentKind', name=u'person').one()
            archivist = cnx.create_entity(
                'Agent', name=u'archivist', agent_kind=kind,
                archival_role=cnx.find('ArchivalRole', name=u'archival').one())
            agent = cnx.create_entity('Agent', name=u'bob the archivist',
                                      isni=u'bobIsbob',
                                      archival_role=roles,
                                      archival_agent=archivist,
                                      agent_kind=kind,
                                      start_date=datetime.date(2012, 3, 1),
                                      end_date=datetime.date(2017, 9, 8))
            cnx.commit()
            cnx.call_service('saem_ref.asalae.sync-agent',
                             connector_eid=self.connector_eid, eid=agent.eid)
            cnx.commit()
            agent.cw_clear_all_caches()
            with cnx.security_enabled(read=False):
                rset = cnx.execute('Any I,MD WHERE M mirror_of X, M extid I,'
                                   ' M modification_date MD')
                self.assertEqual(len(rset), 1)
                extid = rset[0][0]
                etype, organization_id = extid.split()
                self.assertEqual(etype, 'Agent')
                modification_date = rset[0][1]
            yield self._check_organization, connector, agent, organization_id
            self.set_description('agent update')
            kind_ = cnx.find('AgentKind', name=u'authority').one()
            agent.cw_set(isni=u'bobIsNotbob',
                         agent_kind=kind_,
                         end_date=datetime.date(2015, 9, 8))
            cnx.commit()
            agent.cw_clear_all_caches()
            cnx.call_service('saem_ref.asalae.sync-agent',
                             connector_eid=self.connector_eid, eid=agent.eid)
            cnx.commit()
            yield self._check_organization, connector, agent, organization_id
            yield (self._check_operator_type, connector, agent, ('control', 'deposit'),
                   organization_id)
            self.set_description('agent update archival role')
            cnx.execute('DELETE X archival_role R WHERE R name "control"')
            cnx.execute('SET X archival_role R WHERE R name "archival", '
                        'NOT X eid %s' % archivist.eid)
            cnx.commit()
            agent.cw_clear_all_caches()
            cnx.call_service('saem_ref.asalae.sync-agent',
                             connector_eid=self.connector_eid, eid=agent.eid)
            cnx.commit()
            yield self._check_organization, connector, agent, organization_id
            yield (self._check_operator_type, connector, agent,
                   ('archival', 'deposit'), organization_id)
            with cnx.security_enabled(read=False):
                mirror = cnx.find('MirrorEntity', extid=extid).one()
                self.assertGreater(mirror.modification_date, modification_date)
            self.set_description('agent deletion')
            cnx.call_service('saem_ref.asalae.delete-agent',
                             connector_eid=self.connector_eid, eid=agent.eid)
            cnx.commit()
            agent.cw_clear_all_caches()
            yield (self._check_organization_deleted, connector, agent,
                   organization_id)
            cnx.commit()
            with cnx.security_enabled(read=False):
                self.assertEqual(agent.reverse_mirror_of, ())

    def _check_organization(self, connector, agent, organization_id):
        sql = '''SELECT identification, nom, typeentite_id,
        date_existence_debut, date_existence_fin, created, created_user_id,
        modified, modified_user_id, seda02, seda10 FROM "arc-organizations"
        WHERE id = %(id)s'''
        with asalae.db_connect(connector) as cnx:
            cur = cnx.cursor()
            cur.execute(sql, {'id': organization_id})
            rows = cur.fetchall()
            asalae_type_id = asalae.entity_type_id(cur, agent.kind)
            user_id = asalae.user_id(cur, connector.user)
        # Check organization.
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0],
                         (agent.isni, agent.name,
                          asalae_type_id,
                          agent.start_date, agent.end_date,
                          agent.creation_date, user_id,
                          agent.modification_date,
                          user_id,
                          None, None))

    def _check_operator_type(self, connector, agent, arch_roles, organization_id):
        sql = '''SELECT typeacteur_id FROM "organizations_typeacteurs"
                 WHERE organization_id = %(id)s'''
        with asalae.db_connect(connector) as cnx:
            cur = cnx.cursor()
            cur.execute(sql, {'id': organization_id})
            rows = [x[0] for x in cur.fetchall()]
        operator_type_ids = {'archival': 1,
                             'control': 2,
                             'deposit': 3,}
        expected_operator_ids = [operator_type_ids[x] for x in arch_roles]
        self.assertCountEqual(rows,
                              expected_operator_ids)

    def _check_organization_deleted(self, connector, agent, organization_id):
        with asalae.db_connect(connector) as cnx:
            cur = cnx.cursor()
            cur.execute('''SELECT COUNT(*) FROM "arc-organizations"
                           WHERE id = %(id)s''', {'id': organization_id})
            org_count, = cur.fetchone()
            cur.execute('''SELECT COUNT(*) FROM "organizations_typeacteurs"
                           WHERE organization_id = %(id)s''',
                        {'id': organization_id})
            role_type_count, = cur.fetchone()
        self.assertEqual(org_count, 0)
        self.assertEqual(role_type_count, 0)


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
