# coding: utf-8
"""Create concept schemes used by SEDA profile data model"""

from os.path import join, dirname
from cubes.skos.sobjects import _skos_import_lcsv
from cubes.skos.dataimport import HTMLImportLog
from cubes.saem_ref.sobjects.skos import SAEMMetaGennerator

def lcsv_import(fname, scheme_uri):
    import_log = HTMLImportLog(fname)
    stream = open(join(dirname(__file__), 'data', fname))
    _skos_import_lcsv(session, stream, import_log, scheme_uri, '\t', 'utf-8',
                      metagenerator=SAEMMetaGennerator(session),
                      raise_on_error=True)
    commit()


print '-> creating SEDA concept schemes'
for title, rtype, comment, fname in [
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
    ]:
    if not find('ConceptScheme', title=title):
        scheme = create_entity('ConceptScheme', title=title)
        inserted = rql(
            'SET X scheme_relation CR WHERE CR name "%s", X eid %%(x)s' % rtype,
            {'x': scheme.eid})
        assert inserted, comment
        lcsv_import(fname, scheme.cwuri)
