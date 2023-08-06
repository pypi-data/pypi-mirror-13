# coding: utf-8
"""cubicweb-saem_ref unit tests for views"""

from logilab.common import flatten

from cubicweb.devtools import PostgresApptestConfiguration, startpgcluster, stoppgcluster
from cubicweb.devtools.testlib import CubicWebTC

from cubes.saem_ref.views.autocompletesearch import get_results_from_query


def setUpModule():
    startpgcluster(__file__)


def tearDownModule():
    stoppgcluster(__file__)


def sql(cnx, string, param=None):
    return cnx.system_sql(string, param).fetchall()


class AutocompleteSearchTC(CubicWebTC):
    configcls = PostgresApptestConfiguration

    def test_syncro_concepts(self):
        with self.admin_access.client_cnx() as cnx:
            self.assertFalse(sql(cnx, 'SELECT * from words WHERE word=%(w)s;',
                                 {'w': u'déclaration'}))
            scheme = cnx.create_entity('ConceptScheme', title=u'my thesaurus')
            concept = scheme.add_concept(label=u'Déclaration universelle', language_code=u'fr',
                                         definition=u"Déclaration des droits de l'homme")
            scheme.add_concept(label=u'The Universal Declaration', language_code=u'fr',
                               definition=u'Declaration of human rights and citizen')
            cnx.commit()
            all_words = flatten(sql(cnx, 'SELECT word FROM words'))
            for word in (u'responsabilit\xe9', u'responsable', u'responsables'):
                self.assertIn(word, all_words)
            self.assertEqual(get_results_from_query(cnx, {'q': u'déclaration'}),
                             [(u'd\xe9claration', u'Concept', 1.0),
                              (u'declaration', u'Concept', 0.6)])
            self.assertEqual(get_results_from_query(cnx, {'q': u'statisti'}),
                             [(u'statistica', u'Concept', 0.666667),
                              (u'statistique', u'Concept', 0.615385),
                              (u'statistiques', u'Concept', 0.571429)])
            self.assertEqual(get_results_from_query(cnx, {'q': u'rspons'}),
                             [])
            concept.preferred_label[0].cw_set(label=u'Loi renseignement')
            concept.cw_set(definition=u'''L'Assemblée et le Sénat se sont mis d'accord, mardi 16
            juin, sur une version définitive de la loi renseignement. Un texte voté dans une sorte
            d'indifférence générale et qui dote la France d'une des lois les plus intrusives
            d’Europe.''')
            cnx.commit()
            self.assertEqual(get_results_from_query(cnx, {'q': u'déclaration'}),
                             [(u'declaration', u'Concept', 0.6)])

if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
