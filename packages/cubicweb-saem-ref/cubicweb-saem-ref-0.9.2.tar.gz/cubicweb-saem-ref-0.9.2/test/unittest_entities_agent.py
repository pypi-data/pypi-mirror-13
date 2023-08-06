# coding: utf-8
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

"""Tests for agent entities"""

from cubicweb.devtools.testlib import CubicWebTC

from cubes.skos.rdfio import RDFLibRDFGraph

import testutils


class AgentExportTC(CubicWebTC):
    """Test case for agent exports"""

    def setup_database(self):
        with self.admin_access.client_cnx() as cnx:
            org = cnx.find('AgentKind', name=u'authority').one()
            person = cnx.find('AgentKind', name=u'person').one()
            archival_role = cnx.find('ArchivalRole', name=u'archival').one()
            control_role = cnx.find('ArchivalRole', name=u'control').one()
            deposit_role = cnx.find('ArchivalRole', name=u'deposit').one()
            work_address2 = cnx.create_entity('PostalAddress', street=u"1 av. de l'europe",
                                              postalcode=u'31400', city=u'Toulouse')
            work_address3 = cnx.create_entity('PostalAddress', street=u'104 bd L.-A. Blanqui',
                                              postalcode=u'75013', city=u'Paris')
            home_address = cnx.create_entity('PostalAddress', street=u'Place du Capitole',
                                             postalcode=u'31000', city=u'Toulouse')
            agent1 = cnx.create_entity('Agent', name=u'Alice', agent_kind=person,
                                       archival_role=[deposit_role])
            agent2 = cnx.create_entity('Agent', name=u'Super Service', agent_kind=org,
                                       contact_point=agent1,
                                       archival_role=[archival_role],
                                       reverse_archival_agent=agent1)
            cnx.create_entity('AgentPlace', role=u'work', place_agent=agent2,
                              place_address=work_address2)
            agent3 = cnx.create_entity('Agent', name=u'Charlie', agent_kind=person,
                                       archival_role=[archival_role, control_role])
            cnx.create_entity('AgentPlace', role=u'work', place_agent=agent3,
                              place_address=work_address3)
            cnx.create_entity('AgentPlace', role=u'home', place_agent=agent3,
                              place_address=home_address)
            profile = testutils.publishable_profile(cnx)
            profile.cw_set(seda_transferring_agent=agent1)
            cnx.commit()
            self.agent1_eid = agent1.eid
            self.agent2_eid = agent2.eid
            self.agent3_eid = agent3.eid
            self.work_address2_eid = work_address2.eid
            self.work_address3_eid = work_address3.eid
            self.home_address_eid = home_address.eid
            self.profile_uri = profile.absolute_url()

    def assertItemsIn(self, items, container):
        """Check that elements of `items` are in `container`."""
        for item in items:
            self.assertIn(item, container)

    def assertItemsNotIn(self, items, container):
        """Check that elements of `items` are not in `container`."""
        for item in items:
            self.assertNotIn(item, container)

    def test_agent_rdf_primary_adapter(self):
        role_uri = u'http://www.w3.org/2006/vcard/ns#role'
        type_uri = u'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
        person_uri = u'http://xmlns.com/foaf/0.1/Person'
        org_uri = u'http://xmlns.com/foaf/0.1/Organization'
        contact_uri = u'http://schema.org/contactPoint'
        name_uri = u'http://xmlns.com/foaf/0.1/name'
        address_uri = u'http://www.w3.org/2006/vcard/ns#hasAddress'
        archival_agent_uri = u'http://www.logilab.org/saem/0#archivalAgent'
        use_profile_uri = u'http://www.logilab.org/saem/0#useProfile'
        with self.admin_access.client_cnx() as cnx:
            agent1 = cnx.entity_from_eid(self.agent1_eid)
            agent2 = cnx.entity_from_eid(self.agent2_eid)
            agent3 = cnx.entity_from_eid(self.agent3_eid)
            work_address2 = cnx.entity_from_eid(self.work_address2_eid)
            work_address3 = cnx.entity_from_eid(self.work_address3_eid)
            home_address = cnx.entity_from_eid(self.home_address_eid)
            # No archival role / no address
            graph = RDFLibRDFGraph()
            agent1.cw_adapt_to('RDFPrimary').fill(graph)
            triples = list(graph.triples())
            self.assertItemsIn([(agent1.absolute_url(), type_uri, person_uri),
                                (agent1.absolute_url(), name_uri, u'Alice')],
                               triples)
            self.assertItemsIn([(agent1.absolute_url(), archival_agent_uri, agent2.absolute_url()),
                                (agent1.absolute_url(), use_profile_uri, self.profile_uri)],
                               triples)
            self.assertItemsNotIn(
                [(agent1.absolute_url(), role_uri, u'archival'),
                 (agent1.absolute_url(), role_uri, u'control'),
                 (agent1.absolute_url(), address_uri, work_address2.absolute_url()),
                 (agent1.absolute_url(), address_uri, work_address3.absolute_url()),
                 (agent1.absolute_url(), address_uri, home_address.absolute_url()),
                 (agent2.absolute_url(), name_uri, u'Super Service'),
                 ], triples)
            # One archival role / one address
            graph = RDFLibRDFGraph()
            agent2.cw_adapt_to('RDFPrimary').fill(graph)
            triples = list(graph.triples())
            self.assertItemsIn([(agent2.absolute_url(), type_uri, org_uri),
                                (agent2.absolute_url(), name_uri, u'Super Service'),
                                (agent2.absolute_url(), role_uri, u'archival'),
                                (agent2.absolute_url(), address_uri,
                                 work_address2.absolute_url()),
                                (work_address2.absolute_url(), role_uri, 'work')],
                               triples)
            # agent1 in the graph as contact point of agent2
            self.assertItemsIn([(agent2.absolute_url(), contact_uri, agent1.absolute_url()),
                                (agent1.absolute_url(), type_uri, person_uri),
                                (agent1.absolute_url(), name_uri, u'Alice')],
                               triples)
            self.assertItemsNotIn(
                [(agent2.absolute_url(), role_uri, u'control'),
                 (agent2.absolute_url(), address_uri, work_address3.absolute_url()),
                 (work_address3.absolute_url(), role_uri, 'work'),
                 (agent2.absolute_url(), address_uri, home_address.absolute_url())],
                triples)
            # Two archival roles
            graph = RDFLibRDFGraph()
            agent3.cw_adapt_to('RDFPrimary').fill(graph)
            triples = list(graph.triples())
            self.assertItemsIn(
                [(agent3.absolute_url(), type_uri, person_uri),
                 (agent3.absolute_url(), name_uri, u'Charlie'),
                 (agent3.absolute_url(), role_uri, u'archival'),
                 (agent3.absolute_url(), role_uri, u'control'),
                 (agent3.absolute_url(), address_uri, work_address3.absolute_url()),
                 (work_address3.absolute_url(), role_uri, 'work'),
                 (agent3.absolute_url(), address_uri, home_address.absolute_url()),
                 (home_address.absolute_url(), role_uri, 'home')],
                triples)
            self.assertNotIn(
                (agent3.absolute_url(), address_uri, work_address2.absolute_url()),
                triples)


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
