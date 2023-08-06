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

import datetime

from mock import MagicMock, patch

from cubicweb.devtools.testlib import CubicWebTC

from cubes.skos.rdfio import RDFLibRDFGraph

import testutils


class AgentExportTC(CubicWebTC, testutils.XmlTestMixin):
    """Test case for agent exports"""

    @patch('cubes.saem_ref.hooks.datetime')
    def setup_database(self, mock_dt):
        mock_dt.utcnow.return_value = datetime.datetime(2016, 2, 1)
        with self.admin_access.client_cnx() as cnx:
            org = cnx.find('AgentKind', name=u'authority').one()
            person = cnx.find('AgentKind', name=u'person').one()
            unknown = cnx.find('AgentKind', name=u'unknown-agent-kind').one()
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
            agent3 = cnx.create_entity('Agent', name=u'Charlie', agent_kind=person, ark=u'1234',
                                       archival_role=[archival_role, control_role])
            cnx.create_entity('AgentPlace', role=u'work', place_agent=agent3,
                              place_address=work_address3)
            cnx.create_entity('AgentPlace', role=u'home', place_agent=agent3,
                              place_address=home_address)
            cnx.create_entity('ChronologicalRelation', chronological_predecessor=agent2,
                              chronological_successor=agent3)
            gironde = cnx.create_entity('Agent', name=u'Gironde. Conseil général', agent_kind=org,
                                        ark=u'FRAD033_EAC_00001',
                                        start_date=datetime.date(1800, 1, 1),
                                        end_date=datetime.date(2099, 1, 1),
                                        isni=u'22330001300016',
                                        archival_role=[archival_role, control_role])
            delphine = cnx.create_entity('Agent', name=u'Delphine Jamet', agent_kind=person)
            adm_dir = cnx.create_entity('Agent', name=u"Gironde. Conseil général. Direction de "
                                        u"l'administration et de la sécurité juridique",
                                        agent_kind=unknown)
            cg32 = cnx.create_entity('Agent', name=u'CG32', agent_kind=unknown)
            place_uri = cnx.create_entity('ExternalUri',
                                          uri=u'http://catalogue.bnf.fr/ark:/12148/cb152418385',
                                          cwuri=u'http://catalogue.bnf.fr/ark:/12148/cb152418385')
            agent_x = cnx.create_entity('ExternalUri', uri=u'agent-x', cwuri=u'agent-x')
            social_action_uri = cnx.create_entity(
                'ExternalUri', uri=u'http://data.culture.fr/thesaurus/page/ark:/67717/T1-200',
                cwuri=u'http://data.culture.fr/thesaurus/page/ark:/67717/T1-200')
            environment_uri = cnx.create_entity(
                'ExternalUri', uri=u'http://data.culture.fr/thesaurus/page/ark:/67717/T1-1074',
                cwuri=u'http://data.culture.fr/thesaurus/page/ark:/67717/T1-1074')
            resource_uri = cnx.create_entity(
                'ExternalUri', uri=u'http://gael.gironde.fr/ead.html?id=FRAD033_IR_N',
                cwuri=u'http://gael.gironde.fr/ead.html?id=FRAD033_IR_N')
            meeting_uri = cnx.create_entity(
                'ExternalUri', uri=u'http://example.org/meeting',
                cwuri=u'http://example.org/meeting')
            cnx.create_entity('EACSource', title=u'1. Ouvrages imprimés...',
                              description=u'des bouquins', source_agent=gironde)
            cnx.create_entity('EACSource', title=u'Site des Archives départementales de la Gironde',
                              url=u'http://archives.gironde.fr', source_agent=gironde)
            cnx.create_entity('Activity', type=u'create',
                              start=datetime.datetime(2013, 4, 24, 5, 34, 41),
                              end=datetime.datetime(2013, 4, 24, 5, 34, 41),
                              description=u'bla bla bla', generated=gironde)
            cnx.create_entity('Activity', type=u'modify', associated_with=delphine,
                              start=datetime.datetime(2015, 1, 15, 7, 16, 33),
                              end=datetime.datetime(2015, 1, 15, 7, 16, 33),
                              generated=gironde)
            gironde_address = cnx.create_entity('PostalAddress',
                                                street=u'1 Esplanade Charles de Gaulle',
                                                postalcode=u'33074', city=u'Bordeaux Cedex')
            cnx.create_entity('AgentPlace', role=u'siege', name=u'Bordeaux (Gironde, France)',
                              place_agent=gironde, place_address=gironde_address,
                              equivalent_concept=place_uri)
            cnx.create_entity('AgentPlace', role=u'domicile', name=u'Toulouse (France)',
                              place_agent=gironde)
            cnx.create_entity('AgentPlace', role=u'dodo', name=u'Lit',
                              place_agent=gironde)
            cnx.create_entity('LegalStatus', term=u'Collectivité territoriale',
                              start_date=datetime.date(1234, 1, 1),
                              end_date=datetime.date(3000, 1, 1),
                              description=u'Description du statut',
                              legal_status_agent=gironde)
            cnx.create_entity('Mandate', term=u'1. Constitutions françaises',
                              description=u'Description du mandat',
                              mandate_agent=gironde)
            cnx.create_entity('History',
                              text=u'La loi du 22 décembre 1789, en divisant ...',
                              history_agent=gironde)
            cnx.create_entity('Structure',
                              description=u'Pour accomplir ses missions ...',
                              structure_agent=gironde)
            cnx.create_entity('AgentFunction',
                              description=u'Quatre grands domaines de compétence...',
                              function_agent=gironde)
            cnx.create_entity('AgentFunction', name=u'action sociale',
                              description=u'1. Solidarité\nblablabla.',
                              function_agent=gironde, equivalent_concept=social_action_uri)
            cnx.create_entity('AgentFunction', name=u'environnement',
                              function_agent=gironde, equivalent_concept=environment_uri)
            cnx.create_entity('Occupation', term=u'Réunioniste',
                              description=u'Organisation des réunions ...',
                              start_date=datetime.date(1987, 1, 1),
                              end_date=datetime.date(2099, 1, 1),
                              occupation_agent=gironde, equivalent_concept=meeting_uri)
            cnx.create_entity('HierarchicalRelation', hierarchical_parent=adm_dir,
                              hierarchical_child=gironde, description=u'Coucou',
                              start_date=datetime.date(2008, 1, 1),
                              end_date=datetime.date(2099, 1, 1))
            cnx.create_entity('ChronologicalRelation', chronological_predecessor=cg32,
                              chronological_successor=gironde)
            cnx.create_entity('AssociationRelation', association_from=gironde,
                              association_to=agent_x)
            cnx.create_entity('EACResourceRelation', agent_role=u'creatorOf',
                              resource_role=u"Fonds d'archives",
                              start_date=datetime.date(1673, 1, 1),
                              end_date=datetime.date(1963, 1, 1),
                              resource_relation_resource=resource_uri,
                              resource_relation_agent=gironde)
            cnx.commit()
            gironde.cw_adapt_to('IWorkflowable').fire_transition('publish')
            cnx.commit()
            self.agent1_eid = agent1.eid
            self.agent2_eid = agent2.eid
            self.agent3_eid = agent3.eid
            self.gironde_eid = gironde.eid
            self.adm_dir_eid = adm_dir.eid
            self.cg32_eid = cg32.eid
            self.agent_x_eid = agent_x.eid
            self.work_address2_eid = work_address2.eid
            self.work_address3_eid = work_address3.eid
            self.home_address_eid = home_address.eid

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
        replaced_uri = u'http://purl.org/dc/terms/isReplacedBy'
        replaces_uri = u'http://purl.org/dc/terms/replaces'
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
            self.assertItemsIn([(agent1.absolute_url(), archival_agent_uri, agent2.absolute_url())],
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
            # agent1 replaced by agent2 and agent2 replaced by agent3
            self.assertItemsIn(
                [(agent2.absolute_url(), replaced_uri, agent3.absolute_url()),
                 (agent3.absolute_url(), replaces_uri, agent2.absolute_url())],
                triples)

    def test_agent_eac_export(self):
        """Check that an agent is correctly exported into a valid EAC-CPF XML file."""
        # Given an agent (created in setup_database), export it to EAC-CPF
        with self.admin_access.client_cnx() as cnx:
            agent3 = cnx.entity_from_eid(self.agent3_eid)
            agent2 = cnx.entity_from_eid(self.agent2_eid)
            agent2.absolute_url = MagicMock(return_value=u'http://www.example.org/agent2')
            agent3_eac = agent3.cw_adapt_to('EAC-CPF').dump()
        # Then check that output XML is as expected
        with open(self.datapath('EAC/agent3_export.xml')) as f:
            expected_eac = f.read()
        self.assertXmlEqual(agent3_eac, expected_eac)
        self.assertXmlValid(agent3_eac, self.datapath('cpf.xsd'))
        # Same for a more complete example
        with self.admin_access.client_cnx() as cnx:
            adm_dir = cnx.entity_from_eid(self.adm_dir_eid)
            adm_dir.absolute_url = MagicMock(return_value=u'http://www.example.org/adm_dir')
            cg32 = cnx.entity_from_eid(self.cg32_eid)
            cg32.absolute_url = MagicMock(return_value=u'http://www.example.org/cg32')
            agent_x = cnx.entity_from_eid(self.agent_x_eid)
            agent_x.absolute_url = MagicMock(return_value=u'http://www.example.org/agent_x')
            gironde = cnx.entity_from_eid(self.gironde_eid)
            gironde_eac = gironde.cw_adapt_to('EAC-CPF').dump()
        with open(self.datapath('EAC/FRAD033_EAC_00001_simplified_export.xml')) as f:
            expected_eac = f.read()
        self.assertXmlEqual(gironde_eac, expected_eac)
        self.assertXmlValid(gironde_eac, self.datapath('cpf.xsd'))


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
