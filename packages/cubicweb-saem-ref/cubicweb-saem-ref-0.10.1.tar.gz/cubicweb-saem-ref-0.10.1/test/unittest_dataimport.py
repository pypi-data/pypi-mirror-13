# coding: utf-8
"""cubicweb-saem_ref unit tests for dataimport"""

import datetime
import os.path
import sys
from itertools import count, imap

from logilab.common.testlib import TestCase

from cubicweb.dataimport.importer import ExtEntity, SimpleImportLog
from cubicweb.devtools.testlib import CubicWebTC

from cubes.saem_ref.dataimport import eac


def mock_(string):
    return string


class EACXMLParserTC(TestCase):

    def test_parse_FRAD033_EAC_00001(self):
        expected = [
            ('Agent',
             'FRAD033_EAC_00001',
             {'isni': set([u'22330001300016']),
              'name': set([u'Gironde. Conseil général']),
              'start_date': set([datetime.date(1800, 1, 1)]),
              'end_date': set([datetime.date(2099, 1, 1)]),
              'agent_kind': set(['agentkind/authority']),
             },
            ),
            ('EACSource',
             '0',
             {'source_agent': set(['FRAD033_EAC_00001']),
              'title': set([u'1. Ouvrages imprimés...']),
              'description': set([u'des bouquins']),
              'description_format': set([u'text/plain']),
             },
            ),
            ('EACSource',
             '1',
             {'source_agent': set(['FRAD033_EAC_00001']),
              'url': set([u'http://archives.gironde.fr']),
              'title': set([u'Site des Archives départementales de la Gironde']),
             },
            ),
            ('Activity',
             '2',
             {'type': set([u'create']),
              'generated': set(['FRAD033_EAC_00001']),
              'start': set([datetime.datetime(2013, 4, 24, 5, 34, 41)]),
              'end': set([datetime.datetime(2013, 4, 24, 5, 34, 41)]),
              'description': set([u'bla bla']),
              'description_format': set([u'text/plain']),
             },
            ),
            ('AgentKind',
             'agentkind/person',
             {'name': set([u'person'])},
            ),
            ('Agent',
             '3',
             {'name': set([u'Delphine Jamet']),
              'agent_kind': set(['agentkind/person']),
             },
            ),
            ('Activity',
             '4',
             {'associated_with': set(['3']),
              'generated': set(['FRAD033_EAC_00001']),
              'type': set([u'modify']),
              'start': set([datetime.datetime(2015, 1, 15, 7, 16, 33)]),
              'end': set([datetime.datetime(2015, 1, 15, 7, 16, 33)]),
             },
            ),
            ('AgentKind',
             'agentkind/authority',
             {'name': set([u'authority'])},
            ),
            ('PostalAddress',
             '5',
             {'street': set([u'1 Esplanade Charles de Gaulle']),
              'postalcode': set([u'33074']),
              'city': set([u' Bordeaux Cedex']),
             },
            ),
            ('AgentPlace',
             '6',
             {'name': set([u'Bordeaux (Gironde, France)']),
              'role': set([u'siege']),
              'place_agent': set(['FRAD033_EAC_00001']),
              'place_address': set(['5']),
              'equivalent_concept': set([u'http://catalogue.bnf.fr/ark:/12148/cb152418385']),
             },
            ),
            ('AgentPlace',
             '7',
             {'name': set([u'Toulouse (France)']),
              'place_agent': set(['FRAD033_EAC_00001']),
              'role': set([u'domicile']),
             },
            ),
            ('AgentPlace',
             '8',
             {'name': set([u'Lit']),
              'place_agent': set(['FRAD033_EAC_00001']),
              'role': set([u'dodo']),
             },
            ),
            ('LegalStatus',
             '9',
             {'term': set([u'Collectivité territoriale']),
              'start_date': set([datetime.date(1234, 1, 1)]),
              'end_date': set([datetime.date(3000, 1, 1)]),
              'description': set([u'Description du statut']),
              'description_format': set([u'text/plain']),
              'legal_status_agent': set(['FRAD033_EAC_00001']),
             },
            ),
            ('Mandate',
             '10',
             {'term': set([u'1. Constitutions françaises']),
              'description': set([u'Description du mandat']),
              'description_format': set([u'text/plain']),
              'mandate_agent': set(['FRAD033_EAC_00001']),
             },
            ),
            ('History',
             '11',
             {'text': set([u'<p xmlns="urn:isbn:1-931666-33-4" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xlink="http://www.w3.org/1999/xlink">La loi du 22 décembre 1789, en divisant ...</p>']),  # noqa
              'text_format': set([u'text/html']),
              'history_agent': set(['FRAD033_EAC_00001']),
             },
            ),
            ('Structure',
             '12',
             {'description': set([u'<p xmlns="urn:isbn:1-931666-33-4" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xlink="http://www.w3.org/1999/xlink">Pour accomplir ses missions ...</p>']),  # noqa
              'description_format': set([u'text/html']),
              'structure_agent': set(['FRAD033_EAC_00001']),
             },
            ),
            ('AgentFunction',
             '13',
             {'description': set([u'<p xmlns="urn:isbn:1-931666-33-4" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xlink="http://www.w3.org/1999/xlink">Quatre grands domaines de compétence...</p>']),
              'description_format': set([u'text/html']),
              'function_agent': set(['FRAD033_EAC_00001']),
             },
            ),
            ('AgentFunction',
             '14',
             {'name': set([u'action sociale']),
              'function_agent': set(['FRAD033_EAC_00001']),
              'description': set([u'''<p xmlns="urn:isbn:1-931666-33-4" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xlink="http://www.w3.org/1999/xlink">1. Solidarité
            blablabla.</p>''']),
              'description_format': set([u'text/html']),
              'equivalent_concept': set([u'http://data.culture.fr/thesaurus/page/ark:/67717/T1-200']),
             },
            ),
            ('AgentFunction',
             '15',
             {'name': set([u'environnement']),
              'function_agent': set(['FRAD033_EAC_00001']),
              'equivalent_concept': set([u'http://data.culture.fr/thesaurus/page/ark:/67717/T1-1074']),
             },
            ),
            ('Citation',
             '16',
             {'note': set([u'la bible']),
             },
            ),
            ('Occupation',
             '17',
             {'term': set([u'Réunioniste']),
              'start_date': set([datetime.date(1987, 1, 1)]),
              'end_date': set([datetime.date(2099, 1, 1)]),
              'description': set([u'Organisation des réunions ...']),
              'description_format': set([u'text/plain']),
              'occupation_agent': set(['FRAD033_EAC_00001']),
              'has_citation': set(['16']),
              'equivalent_concept': set(['http://pifgadget.com']),
             },
            ),
            ('Agent',
             'CG33-DIRADSJ',
             {'name': set([u"Gironde. Conseil général. Direction de l'administration et de la "
                           u"sécurité juridique"]),
              'agent_kind': set(['agentkind/unknown-agent-kind']),
             },
            ),
            ('HierarchicalRelation',
             '18',
             {'start_date': set([datetime.date(2008, 1, 1)]),
              'end_date': set([datetime.date(2099, 1, 1)]),
              'description': set([u'Coucou']),
              'description_format': set([u'text/plain']),
              'hierarchical_parent': set(['CG33-DIRADSJ']),
              'hierarchical_child': set(['FRAD033_EAC_00001']),
             },
            ),
            ('Agent',
             'whatever',
             {'name': set([u'CG32']),
              'agent_kind': set(['agentkind/unknown-agent-kind']),
             },
            ),
            ('ChronologicalRelation',
             '19',
             {'chronological_predecessor': set(['whatever']),
              'chronological_successor': set(['FRAD033_EAC_00001']),
             },
            ),
            ('AssociationRelation',
             '20',
             {'association_from': set(['FRAD033_EAC_00001']),
              'association_to': set(['agent-x']),
             },
            ),
            ('EACResourceRelation',
             '21',
             {'agent_role': set([u'creatorOf']),
              'resource_role': set([u'Fonds d\'archives']),
              'resource_relation_resource': set([
                  'http://gael.gironde.fr/ead.html?id=FRAD033_IR_N']),
              'resource_relation_agent': set(['FRAD033_EAC_00001']),
              'start_date': set([datetime.date(1673, 1, 1)]),
              'end_date': set([datetime.date(1963, 1, 1)]),
             },
            ),
            ('ExternalUri',
             'http://gael.gironde.fr/ead.html?id=FRAD033_IR_N',
             {'uri': set([u'http://gael.gironde.fr/ead.html?id=FRAD033_IR_N']),
              'cwuri': set([u'http://gael.gironde.fr/ead.html?id=FRAD033_IR_N'])},
            ),
            ('ExternalUri',
             'agent-x',
             {'uri': set([u'agent-x']), 'cwuri': set([u'agent-x'])},
            ),
            ('ExternalUri',
             'http://data.culture.fr/thesaurus/page/ark:/67717/T1-200',
             {'uri': set([u'http://data.culture.fr/thesaurus/page/ark:/67717/T1-200']),
              'cwuri': set([u'http://data.culture.fr/thesaurus/page/ark:/67717/T1-200'])},
            ),
            ('ExternalUri',
             'http://data.culture.fr/thesaurus/page/ark:/67717/T1-1074',
             {'uri': set([u'http://data.culture.fr/thesaurus/page/ark:/67717/T1-1074']),
              'cwuri': set([u'http://data.culture.fr/thesaurus/page/ark:/67717/T1-1074'])},
            ),
            ('ExternalUri',
             'http://catalogue.bnf.fr/ark:/12148/cb152418385',
             {'uri': set([u'http://catalogue.bnf.fr/ark:/12148/cb152418385']),
              'cwuri': set([u'http://catalogue.bnf.fr/ark:/12148/cb152418385'])},
            ),
            ('ExternalUri',
             'http://pifgadget.com',
             {'uri': set([u'http://pifgadget.com']),
              'cwuri': set([u'http://pifgadget.com'])},
            ),
        ]
        expected = [ExtEntity(*vals) for vals in expected]
        fpath = self.datapath('EAC/FRAD033_EAC_00001_simplified.xml')
        import_log = SimpleImportLog(fpath)
        # Use a predictable extid_generator.
        extid_generator = imap(str, count()).next
        importer = eac.EACCPFImporter(fpath, import_log, mock_,
                                      extid_generator=extid_generator)
        entities = list(importer.external_entities())
        self.check_external_entities(entities, expected)
        visited = set([])
        for x in importer._visited.values():
            visited.update(x)
        self.assertItemsEqual(visited, [x.extid for x in expected])
        # Gather not-visited tag by name and group source lines.
        not_visited = {}
        for tagname, sourceline in importer.not_visited():
            not_visited.setdefault(tagname, set([])).add(sourceline)
        self.assertEqual(not_visited,
                         {'maintenanceStatus': set([10]),
                          'publicationStatus': set([12]),
                          'maintenanceAgency': set([14]),
                          'languageDeclaration': set([19]),
                          'conventionDeclaration': set([23, 33, 42]),
                          'localControl': set([52]),
                          'generalContext': set([188]),
                          'nameEntry': set([112]),  # alternative form.
                          'source': set([74]),  # empty.
                          'biogHist': set([193]),  # empty.
                          'structureOrGenealogy': set([186]),  # empty.
                          })

    def test_mandate_under_mandates(self):
        """In FRAD033_EAC_00003.xml, <mandate> element are within <mandates>."""
        fpath = self.datapath('EAC/FRAD033_EAC_00003.xml')
        import_log = SimpleImportLog(fpath)
        # Use a predictable extid_generator.
        extid_generator = imap(str, count()).next
        importer = eac.EACCPFImporter(fpath, import_log, mock_,
                                      extid_generator=extid_generator)
        entities = list(importer.external_entities())
        expected_terms = [
            u'Code du patrimoine, Livre II',
            u'Loi du 5 brumaire an V [26 octobre 1796]',
            (u'Loi du 3 janvier 1979 sur les archives, accompagnée de ses décrets\n'
             u'                        d’application datant du 3 décembre.'),
            u'Loi sur les archives du 15 juillet 2008',
        ]
        self.assertCountEqual([next(iter(x.values['term'])) for x in entities
                               if x.etype == 'Mandate' and 'term' in x.values],
                              expected_terms)
        mandate_with_link = next(x for x in entities if x.etype == 'Mandate' and
                                 u'Code du patrimoine, Livre II' in x.values['term'])
        extid = next(iter(mandate_with_link.values['has_citation']))
        url = u'http://www.legifrance.gouv.fr/affichCode.do?idArticle=LEGIARTI000019202816'
        citation = next(x for x in entities if x.etype == 'Citation'
                        and url in x.values['uri'])
        self.assertEqual(extid, citation.extid)

    def test_agentfunction_within_functions_tag(self):
        """In FRAD033_EAC_00003.xml, <function> element are within <functions>
        not <description>.
        """
        fpath = self.datapath('EAC/FRAD033_EAC_00003.xml')
        import_log = SimpleImportLog(fpath)
        # Use a predictable extid_generator.
        extid_generator = imap(str, count()).next
        importer = eac.EACCPFImporter(fpath, import_log, mock_,
                                      extid_generator=extid_generator)
        entities = importer.external_entities()
        self.assertCountEqual(
            [x.values['name'].pop() for x in entities
             if x.etype == 'AgentFunction' and 'name' in x.values],
            [u'contr\xf4le', u'collecte', u'classement', u'restauration', u'promotion'])

    def ctx_assert(self, method, actual, expected, ctx, msg=None):
        """Wrap assertion method with a context message"""
        try:
            getattr(self, method)(actual, expected, msg=msg)
        except AssertionError as exc:
            msg = str(exc)
            if ctx:
                msg = ('[%s] ' % ctx) + msg
            raise AssertionError(msg), None, sys.exc_info()[-1]

    def check_external_entities(self, entities, expected):
        entities = extentities2dict(entities)
        expected = extentities2dict(expected)
        etypes, expected_etypes = entities.keys(), expected.keys()
        self.ctx_assert('assertCountEqual', etypes, expected_etypes, ctx='etypes')
        for etype, edict in expected.iteritems():
            entities_etype = entities[etype]
            extids, expected_extids = entities_etype.keys(), edict.keys()
            self.ctx_assert('assertCountEqual', extids, expected_extids,
                            ctx='%s/extids' % etype)
            for extid, values in edict.iteritems():
                self.ctx_assert('assertEqual', entities_etype[extid], values,
                                ctx='%s/%s/values' % (etype, extid))


def extentities2dict(entities):
    edict = {}
    for extentity in entities:
        edict.setdefault(extentity.etype, {})[extentity.extid] = extentity.values
    return edict


def eac_import(cnx, fpath):
    import_log = SimpleImportLog(os.path.basename(fpath))
    created, updated, _ = cnx.call_service(
        'saem_ref.eac-import', stream=fpath, import_log=import_log,
        raise_on_error=True)
    return created, updated


class EACDataImportTC(CubicWebTC):

    def test_FRAD033_EAC_00001(self):
        fpath = self.datapath('EAC/FRAD033_EAC_00001_simplified.xml')
        with self.admin_access.repo_cnx() as cnx:
            # create a skos concept to ensure it's used instead of a ExternalUri
            scheme = cnx.create_entity('ConceptScheme')
            scheme.add_concept(u'environnement',
                               cwuri=u'http://data.culture.fr/thesaurus/page/ark:/67717/T1-1074')
            cnx.commit()
            created, updated = eac_import(cnx, fpath)
            self.assertEqual(len(created), 30)
            person_eid = cnx.find('AgentKind', name=u'person')[0][0]
            authority_eid = cnx.find('AgentKind', name=u'authority')[0][0]
            self.assertEqual(updated, set([authority_eid, person_eid]))
            rset = cnx.find('Agent', isni=u'22330001300016')
            self.assertEqual(len(rset), 1)
            agent = rset.one()
            self.assertEqual(agent.kind, 'authority')
            self.assertEqual(agent.start_date, datetime.date(1800, 1, 1))
            self.assertEqual(agent.end_date, datetime.date(2099, 1, 1))
            address = agent.postal_address[0]
            self.assertEqual(address.street, u'1 Esplanade Charles de Gaulle')
            self.assertEqual(address.postalcode, u'33074')
            self.assertEqual(address.city, u' Bordeaux Cedex')
            rset = cnx.execute('Any R,N WHERE P place_agent A, A eid %(eid)s, P role R, P name N',
                               {'eid': agent.eid})
            self.assertCountEqual(rset.rows,
                                  [[u'siege', u'Bordeaux (Gironde, France)'],
                                   [u'domicile', u'Toulouse (France)'],
                                   [u'dodo', u'Lit']])
            self.assertEqual(len(agent.reverse_function_agent), 3)
            self.set_description('check Structure')
            self._check_structure(cnx, agent)
            self.set_description('check History')
            self._check_history(cnx, agent)
            self.set_description('check Mandate')
            self._check_mandate(cnx, agent)
            self.set_description('check Occupation')
            self._check_occupation(cnx, agent)
            self.set_description('check LegalStatus')
            self._check_legal_status(cnx, agent)
            self.set_description('check relations')
            self._check_eac_relations(cnx, agent)
            self.set_description('check vocabulary source')
            self._check_equivalent_concept(cnx, agent)
            self.set_description('check control')
            self._check_control(cnx, agent)

    def _check_structure(self, cnx, agent):
        rset = cnx.find('Structure', structure_agent=agent)
        self.assertEqual(len(rset), 1)
        self.assertEqual(rset.one().printable_value('description',
                                                    format=u'text/plain').strip(),
                         u'Pour accomplir ses missions ...')

    def _check_history(self, cnx, agent):
        rset = cnx.find('History', history_agent=agent)
        self.assertEqual(len(rset), 1)
        self.assertEqual(rset.one().printable_value('text',
                                                    format=u'text/plain').strip(),
                         u'La loi du 22 décembre 1789, en divisant ...')

    def _check_mandate(self, cnx, agent):
        rset = cnx.find('Mandate', mandate_agent=agent)
        self.assertEqual(len(rset), 1)
        self.assertEqual(rset.one().printable_value('description',
                                                    format=u'text/plain').strip(),
                         u'Description du mandat')

    def _check_occupation(self, cnx, agent):
        occupation = cnx.find('Occupation', occupation_agent=agent).one()
        self.assertEqual(occupation.term, u'Réunioniste')
        citation = occupation.has_citation[0]
        self.assertEqual(citation.note, u'la bible')
        voc = occupation.equivalent_concept[0]
        self.assertEqual(voc.uri, u'http://pifgadget.com')

    def _check_legal_status(self, cnx, agent):
        rset = cnx.find('LegalStatus', legal_status_agent=agent)
        self.assertEqual(len(rset), 1)
        self.assertEqual(rset.one().printable_value('description',
                                                    format=u'text/plain').strip(),
                         u'Description du statut')

    def _check_eac_relations(self, cnx, agent):
        relation = cnx.find('HierarchicalRelation').one()
        self.assertEqual(relation.printable_value('description',
                                                  format='text/plain'),
                         u'Coucou')
        other_agent = cnx.find('Agent', name=u"Gironde. Conseil général. Direction de "
                               u"l'administration et de la sécurité juridique").one()
        self.assertEqual(relation.hierarchical_parent[0], other_agent)
        relation = cnx.find('AssociationRelation').one()
        self.assertEqual(relation.association_from[0], agent)
        other_agent = cnx.find('ExternalUri', uri=u'agent-x').one()
        self.assertEqual(other_agent.cwuri, 'agent-x')
        self.assertEqual(relation.association_to[0], other_agent)
        rset = cnx.find('EACResourceRelation', agent_role=u'creatorOf')
        self.assertEqual(len(rset), 1)
        rrelation = rset.one()
        self.assertEqual(rrelation.resource_relation_agent[0], agent)
        exturi = rrelation.resource_relation_resource[0]
        self.assertEqual(exturi.uri,
                         u'http://gael.gironde.fr/ead.html?id=FRAD033_IR_N')

    def _check_equivalent_concept(self, cnx, agent):
        functions = dict((f.name, f) for f in agent.reverse_function_agent)
        self.assertEqual(functions['action sociale'].equivalent_concept[0].cwuri,
                         'http://data.culture.fr/thesaurus/page/ark:/67717/T1-200')
        self.assertEqual(functions['action sociale'].equivalent_concept[0].cw_etype,
                         'ExternalUri')
        self.assertEqual(functions['environnement'].equivalent_concept[0].cwuri,
                         'http://data.culture.fr/thesaurus/page/ark:/67717/T1-1074')
        self.assertEqual(functions['environnement'].equivalent_concept[0].cw_etype,
                         'Concept')
        self.assertEqual(functions['environnement'].vocabulary_source[0].eid,
                         functions['environnement'].equivalent_concept[0].scheme.eid)
        place = cnx.find('AgentPlace', role=u'siege').one()
        self.assertEqual(place.equivalent_concept[0].cwuri,
                         'http://catalogue.bnf.fr/ark:/12148/cb152418385')

    def _check_control(self, cnx, agent):
        rset = cnx.find('EACSource')
        self.assertEqual(len(rset), 2)
        rset = cnx.execute('Any A WHERE A generated X, X eid %s' % agent.eid)
        # Two activities imported from EAC-CPF file, one created by our hook.
        self.assertEqual(len(rset), 3)
        rset = cnx.execute('Any A WHERE A associated_with X, X name "Delphine Jamet"')
        self.assertEqual(len(rset), 1)

    def test_multiple_imports(self):
        with self.admin_access.repo_cnx() as cnx:
            for fname in ('FRAD033_EAC_00001.xml', 'FRAD033_EAC_00003.xml',
                          'FRAD033_EAC_00071.xml'):
                self.set_description('importing ' + fname)
                fpath = self.datapath('EAC/' + fname)
                created, updated = eac_import(cnx, fpath)
            self.set_description('check')
            # Imported agent do not have a CWUSer associated.
            rset = cnx.execute('Any X WHERE X is Agent, NOT EXISTS(X agent_user U)')
            self.assertEqual(len(rset), 15)


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
