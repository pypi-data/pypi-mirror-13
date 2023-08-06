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
"""cubicweb-saem_ref unit tests for sobjects.alfresco"""

import functools
from datetime import datetime, timedelta

from logilab.common import tempattr

from cubicweb.devtools.testlib import CubicWebTC

from cubes.saem_ref.lib import alfresco

import testutils


YESTERDAY = datetime.utcnow() - timedelta(days=1)


class AlfrescoMock(testutils.Mock):

    @classmethod
    def _create_ref(cls):
        super(AlfrescoMock, cls)._create_ref()
        return 'workspace://SpacesStore/%s' % cls._counter

    def __init__(self, *args, **kwargs):
        for name in ('login', 'update_category', 'delete_category', 'update_sedaprofile'):
            meth = functools.partial(self._record, name)
            setattr(self, name, meth)
        assert args[0].cw_etype == 'AlfrescoConnector'
        args = (args[0].url, ) + args[1:]
        super(AlfrescoMock, self).__init__(*args, **kwargs)

    def add_root_category(self, name):
        self._record('add_root_category', name)
        return self._create_ref()

    def add_sub_category(self, store_ref, name):
        self._record('add_sub_category', store_ref, name)
        return self._create_ref()

    def add_sedaprofile(self, fname, file_content):
        self._record('add_sedaprofile', fname, file_content)
        return self._create_ref()


class AlfrescoSyncServiceTC(CubicWebTC):
    """Test case for Alfresco synchronization service."""

    def setup_database(self):
        with self.admin_access.repo_cnx() as cnx:
            connector = cnx.create_entity('AlfrescoConnector',
                                          url=u'http://nonexistant.logilab.org:8080/',
                                          user=u'alf', password=u'des chats !!!!',
                                          sedaprofiles_node=u'123')
            def create_entity(etype, **kwargs):
                return cnx.create_entity(etype, modification_date=YESTERDAY, **kwargs)
            # Create concept scheme
            scheme = create_entity('ConceptScheme', title=u'my thesaurus')
            c1 = create_entity('Concept', in_scheme=scheme)
            create_entity('Label', label=u'concept 1', language_code=u'fr', label_of=c1)
            c11 = create_entity('Concept', in_scheme=scheme, broader_concept=c1)
            create_entity('Label', label=u'concept 1.1', language_code=u'fr', label_of=c11)
            c111 = create_entity('Concept', in_scheme=scheme, broader_concept=c11)
            create_entity('Label', label=u'concept 1.1.1', language_code=u'fr', label_of=c111)
            c12 = create_entity('Concept', in_scheme=scheme, broader_concept=c1)
            create_entity('Label', label=u'concept 1.2', language_code=u'fr', label_of=c12)
            # Create SEDA profile
            profile = testutils.setup_seda_profile(cnx, ark=u'1234')
            cnx.commit()
        self.connector_eid = connector.eid
        self.scheme_eid = scheme.eid
        self.c11_eid = c11.eid
        self.profile_eid = profile.eid

    def call_sync_scheme(self, cnx):
        AlfrescoMock.reset_events()
        cnx.call_service('saem_ref.alfresco.sync',
                         connector_eid=self.connector_eid,
                         eid=self.scheme_eid)

    def test_sync_scheme(self):
        # substitute the REST helper by a mock to test interaction of the service with the helper
        with AlfrescoMock.mock_applied(alfresco, 'AlfrescoRESTHelper'):
            with self.admin_access.repo_cnx() as cnx:
                self._test_sync_scheme(cnx)

    def _test_sync_scheme(self, cnx):
        self.call_sync_scheme(cnx)
        self.assertEqual(AlfrescoMock.events,
                         [('__init__', u'http://nonexistant.logilab.org:8080/'),
                          ('login', u'alf', u'des chats !!!!'),
                          ('add_root_category', u'my thesaurus'),
                          ('add_sub_category', u'workspace://SpacesStore/1', u'concept 1'),
                          ('add_sub_category', u'workspace://SpacesStore/2', u'concept 1.1'),
                          ('add_sub_category', u'workspace://SpacesStore/3', u'concept 1.1.1'),
                          ('add_sub_category', u'workspace://SpacesStore/2', u'concept 1.2')])
        c11 = cnx.entity_from_eid(self.c11_eid)
        c11.preferred_label[0].cw_set(label=u'modified concept 1.1')
        cnx.commit()
        self.call_sync_scheme(cnx)
        self.assertEqual(AlfrescoMock.events,
                         [('__init__', u'http://nonexistant.logilab.org:8080/'),
                          ('login', u'alf', u'des chats !!!!'),
                          ('update_category', u'workspace://SpacesStore/1', u'my thesaurus'),
                          ('update_category', u'workspace://SpacesStore/2', u'concept 1'),
                          ('update_category', u'workspace://SpacesStore/3', u'modified concept 1.1')])

    def call_sync_profile(self, cnx):
        AlfrescoMock.reset_events()
        cnx.call_service('saem_ref.alfresco.sync',
                         connector_eid=self.connector_eid,
                         eid=self.profile_eid)

    def test_sync_profile(self):
        # substitute the REST helper by a mock to test interaction of the service with the helper
         with AlfrescoMock.mock_applied(alfresco, 'AlfrescoRESTHelper'):
             with self.admin_access.repo_cnx() as cnx:
                 self._test_sync_profile(cnx)

    def _test_sync_profile(self, cnx):
        self.call_sync_profile(cnx)
        # __init__, login, add_sedaprofile
        self.assertEqual(len(AlfrescoMock.events), 3)
        event, fname, fcontent = AlfrescoMock.events[2]
        self.assertEqual(event, 'add_sedaprofile')
        self.assertEqual(fname, '1234.xsd')
        # no need to check file content here, just ensure it does exist
        self.assertGreater(len(fcontent), 0)
        self.assertEqual(AlfrescoMock.events[:2],
                         [('__init__', u'http://nonexistant.logilab.org:8080/'),
                          ('login', u'alf', u'des chats !!!!')])
        self.call_sync_profile(cnx)
        # __init__, login, update_sedaprofile
        self.assertEqual(len(AlfrescoMock.events), 3)
        event, fname, fcontent, node = AlfrescoMock.events[2]
        self.assertEqual(event, 'update_sedaprofile')
        self.assertEqual(fname, '1234.xsd')
        # no need to check file content here, just ensure it does exist
        self.assertGreater(len(fcontent), 0)
        self.assertEqual(node, u'workspace://SpacesStore/1')

    def test_error_bad_host(self):
        with self.admin_access.repo_cnx() as cnx:
            with self.assertRaises(alfresco.AlfrescoException) as cm:
                self.call_sync_scheme(cnx)
        self.assertEqual(str(cm.exception), "can't connect to remote host.")

    def test_unexpected_error(self):
        with AlfrescoMock.mock_applied(alfresco, 'AlfrescoRESTHelper'):
            def raise_add_sub_category(self, store_ref, name):
                self._record('add_sub_category', store_ref, name)
                ref = self._create_ref()
                if ref == 'workspace://SpacesStore/3':
                    raise alfresco.AlfrescoException('unexpected', 500)
                return ref
            with self.admin_access.repo_cnx() as cnx:
                # an error is raised during the synchronisation, ensure error flag is set
                with tempattr(AlfrescoMock, 'add_sub_category', raise_add_sub_category):
                    with self.assertRaises(alfresco.AlfrescoException) as cm:
                        self.call_sync_scheme(cnx)
                self.assertEqual(str(cm.exception), '500: unexpected')
                self.assertEqual(AlfrescoMock.events,
                                 [('__init__', u'http://nonexistant.logilab.org:8080/'),
                                  ('login', u'alf', u'des chats !!!!'),
                                  ('add_root_category', u'my thesaurus'),
                                  ('add_sub_category', u'workspace://SpacesStore/1', u'concept 1'),
                                  ('add_sub_category', u'workspace://SpacesStore/2', u'concept 1.1')])
                scheme = cnx.entity_from_eid(self.scheme_eid)
                mirror = scheme.reverse_mirror_of[0]
                self.assertEqual(mirror.error_flag, True)
                # ensure that if we sync again, the whole tree is correctly synchronized
                self.call_sync_scheme(cnx)
                self.assertEqual(AlfrescoMock.events,
                                 [('__init__', u'http://nonexistant.logilab.org:8080/'),
                                  ('login', u'alf', u'des chats !!!!'),
                                  ('update_category', u'workspace://SpacesStore/1', u'my thesaurus'),
                                  ('update_category', u'workspace://SpacesStore/2', u'concept 1'),
                                  ('add_sub_category', u'workspace://SpacesStore/2', u'concept 1.1'),
                                  ('add_sub_category', u'workspace://SpacesStore/4', u'concept 1.1.1'),
                                  ('add_sub_category', u'workspace://SpacesStore/2', u'concept 1.2')])


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
