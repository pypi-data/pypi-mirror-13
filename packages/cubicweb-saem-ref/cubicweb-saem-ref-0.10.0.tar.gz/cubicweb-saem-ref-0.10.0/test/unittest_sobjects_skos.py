# coding: utf-8
# copyright 2015-2016 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

from cubicweb.devtools.testlib import CubicWebTC
from cubicweb.devtools import PostgresApptestConfiguration, startpgcluster, stoppgcluster


def setUpModule():
    startpgcluster(__file__)


def tearDownModule():
    stoppgcluster(__file__)


class SKOSImportTC(CubicWebTC):
    configcls = PostgresApptestConfiguration

    def setup_database(self):
        with self.admin_access.client_cnx() as cnx:
            # create some agent and related objects
            akind = cnx.find('AgentKind', name=u'person').one()
            agent = cnx.create_entity('Agent', name=u'bob', agent_kind=akind)
            function = cnx.create_entity('AgentFunction', name=u'sponge', function_agent=agent)
            cnx.commit()
            # create some external uri and link it to place, function and information entities
            cnx.create_entity('ExternalUri',
                              cwuri=u'http://data.culture.fr/thesaurus/resource/ark:/67717/T1-543',
                              uri=u'http://data.culture.fr/thesaurus/resource/ark:/67717/T1-543',
                              reverse_equivalent_concept=function)
            cnx.commit()
            self.function_eid = function.eid

    def check_skos_ark(self):
        with self.admin_access.client_cnx() as cnx:
            scheme = cnx.find('ConceptScheme',
                              cwuri='http://data.culture.fr/thesaurus/resource/ark:/67717/Matiere').one()
            self.assertEqual(scheme.ark, u'67717/Matiere')
            self.assertEqual(set(c.ark for c in scheme.top_concepts),
                             set(['67717/T1-503', '67717/T1-543']))
            self.assertEqual(scheme.cw_adapt_to('IWorkflowable').state, 'draft')
            # ensure the external uri has been replaced by the concept and deleted
            concept = cnx.find('Concept', ark='67717/T1-543').one()
            function = cnx.entity_from_eid(self.function_eid)
            function.cw_clear_all_caches()
            self.assertEqual(function.equivalent_concept[0].eid, concept.eid)
            # XXX also unique extid  pb when skos import will support externaluri

    def test_service(self):
        with self.admin_access.repo_cnx() as cnx:
            cnx.call_service('rdf.skos.import', stream=open(self.datapath('skos.rdf')))
        self.check_skos_ark()

    def test_datafeed_source(self):
        with self.admin_access.repo_cnx() as cnx:
            url = u'file://%s' % self.datapath('skos.rdf')
            cnx.create_entity('CWSource', name=u'mythesaurus', type=u'datafeed', parser=u'rdf.skos',
                              url=url)
            cnx.commit()
        dfsource = self.repo.sources_by_uri['mythesaurus']
        # test creation upon initial pull
        with self.repo.internal_cnx() as cnx:
            dfsource.pull_data(cnx, force=True, raise_on_error=True)
        self.check_skos_ark()


class LCSVImportTC(CubicWebTC):

    def test_cwuri_with_ark(self):
        with self.admin_access.repo_cnx() as cnx:
            scheme = cnx.create_entity('ConceptScheme')
            cnx.commit()
            cnx.call_service('lcsv.skos.import', scheme_uri=scheme.cwuri,
                             stream=open(self.datapath('lcsv_example_shortened.csv')),
                             delimiter='\t', encoding='utf-8', language_code='es')
            concept1 = cnx.find(
                'Concept', definition="Définition de l'organisation politique de l'organisme").one()
            self.assertEqual(concept1.cwuri,
                             'ark:/saemref-test/%09d' % concept1.eid)

if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
