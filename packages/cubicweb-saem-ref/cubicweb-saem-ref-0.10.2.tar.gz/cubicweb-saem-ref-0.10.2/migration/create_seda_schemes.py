# coding: utf-8
"""Create concept schemes used by SEDA profile data model"""

from os.path import join, dirname

from cubicweb.dataimport.importer import HTMLImportLog

from cubes.skos.sobjects import lcsv_extentities, store_skos_extentities

from cubes.saem_ref.sobjects.skos import _store


def lcsv_import(cnx, store, fname, scheme_uri):
    import_log = HTMLImportLog(fname)
    stream = open(join(dirname(__file__), 'data', fname))
    entities = lcsv_extentities(stream, scheme_uri, '\t', 'utf-8')
    store_skos_extentities(cnx, store, entities, import_log,
                           raise_on_error=True, extid_as_cwuri=False)


def import_seda_schemes(cnx):
    store = _store(cnx)
    for title, rtype, comment, fname in (
            (u"SEDA : Codes de restriction d'accès",
             'seda_access_restriction_code',
             'access control',
             'seda_access_control.csv'),
            (u'SEDA : Sort final',
             'seda_appraisal_rule_code',
             'appraisal rule',
             'seda_appraisal_rule_code.csv'),
            (u'SEDA : Niveaux de description de contenu',
             'seda_description_level',
             'description level',
             'seda_description_level.csv'),
            (u'SEDA : Formats de fichier source',
             'seda_file_type_code',
             'file type code',
             'seda_file_type_code.csv'),
            (u'SEDA : Jeu de caractères de codage',
             'seda_character_set_code',
             'character set code',
             'seda_character_set_code.csv'),
            (u'SEDA : Codes des types de contenu',
             'seda_document_type_code',
             'document type code',
             'seda_document_type_code.csv'),
    ):
        if not cnx.find('ConceptScheme', title=title):
            scheme = cnx.create_entity('ConceptScheme', title=title)
            inserted = cnx.execute(
                'SET X scheme_relation CR WHERE CR name "%s", X eid %%(x)s' % rtype,
                {'x': scheme.eid})
            assert inserted, comment
            lcsv_import(cnx, store, fname, scheme.cwuri)
    store.flush()
    store.commit()
    store.finish()


print('-> creating SEDA concept schemes')
import_seda_schemes(cnx)

if repo.system_source.dbdriver == 'postgres':
    # massive store is used, which doesn't handle full-text indexation
    reindex_entities(['ConceptScheme', 'Concept'])
