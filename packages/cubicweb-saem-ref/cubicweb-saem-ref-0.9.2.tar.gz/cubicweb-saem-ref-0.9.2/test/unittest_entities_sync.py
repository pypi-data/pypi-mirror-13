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
"""cubicweb-saem_ref unit tests for entities.sync"""

from cubicweb.devtools.testlib import CubicWebTC

from cubes.saem_ref.entities.sync import SynchronizationError

import testutils

class AsalaeConnectorTC(CubicWebTC):

    def test_agent_synchronize_blockers(self):
        with self.admin_access.client_cnx() as cnx:
            connector = cnx.create_entity('AsalaeConnector', dbhost=u'asalae',
                                          database=u'asalae', dbuser=u'asalae',
                                          url=u'http://nowhere.land.com:111/asalae/',
                                          user=u'admin', password=u'admin')
            cnx.commit()
            akind = cnx.find('AgentKind', name=u'unknown-agent-kind').one()
            agent = cnx.create_entity('Agent', name=u'bob', agent_kind=akind)
            cnx.commit()
            self.assertEqual(connector.synchronize_blockers(agent.eid),
                            ['Agent kind "unknown-agent-kind" is not known by As@lae'])

    def test_profile_synchronize_blockers(self):
        with self.admin_access.client_cnx() as cnx:
            connector = cnx.create_entity('AsalaeConnector', dbhost=u'asalae',
                                          database=u'asalae', dbuser=u'asalae',
                                          url=u'http://nowhere.land.com:111/asalae/',
                                          user=u'admin', password=u'admin')
            cnx.commit()
            profile = testutils.setup_seda_profile(cnx)
            cnx.commit()
            self.assertEqual(connector.synchronize_blockers(profile.eid),
                             ['profile attribute "title" unspecified',
                              'profile attribute "description" unspecified'])
            profile.cw_set(title=u'title', description=u'description')
            cnx.commit()
            self.assertEqual(connector.synchronize_blockers(profile.eid),
                            [])


class AlfrescoConnectorTC(CubicWebTC):

    def test_profile_synchronize_blockers(self):
        with self.admin_access.client_cnx() as cnx:
            connector = cnx.create_entity('AlfrescoConnector', url=u'http://nonexistant.logilab.org',
                                          user=u'alf', password=u'des chats !!!!',)
            cnx.commit()
            profile = testutils.setup_seda_profile(cnx)
            cnx.commit()
            self.assertEqual(connector.synchronize_blockers(profile.eid),
                            [u'connector has no "sedaprofiles_node" attribute set'])
            connector.cw_set(sedaprofiles_node=u'1234')
            cnx.commit()
            self.assertEqual(connector.synchronize_blockers(profile.eid),
                            [])

    def test_scheme_synchronize_error(self):
        with self.admin_access.repo_cnx() as cnx:
            connector = cnx.create_entity('AlfrescoConnector', url=u'http://nonexistant.logilab.org',
                                          user=u'alf', password=u'des chats !!!!',)
            scheme = cnx.create_entity('ConceptScheme', title=u'my thesaurus')
            cnx.commit()
            with self.assertRaises(SynchronizationError) as cm:
                connector.synchronize(scheme.eid)
        self.assertEqual(str(cm.exception), "can't connect to remote host.")


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
