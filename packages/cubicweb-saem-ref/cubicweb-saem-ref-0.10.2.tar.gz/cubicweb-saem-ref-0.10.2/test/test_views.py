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
"""cubicweb-saem-ref test for views."""

import json
import os
from datetime import date
from tempfile import NamedTemporaryFile

from yams.schema import role_name
from logilab.common.testlib import TestCase, unittest_main

from cubicweb.devtools.testlib import CubicWebTC

from cubes.skos.rdfio import default_graph

from cubes.saem_ref.views import seda
from cubes.saem_ref.views.widgets import process_incomplete_date
from cubes.saem_ref.views.agent import AgentRestPathEvaluator

import testutils


class SetDateTC(TestCase):

    def test_set_date_month_beginning(self):
        self.assertEqual(date(1997, 6, 5), process_incomplete_date("5/6/1997"))
        self.assertEqual(date(1997, 6, 5), process_incomplete_date("5/6/97"))
        self.assertEqual(date(2012, 6, 5), process_incomplete_date("5/6/12"))
        self.assertEqual(date(1997, 6, 5), process_incomplete_date("1997/6/5"))
        self.assertEqual(date(1997, 6, 1), process_incomplete_date("6/1997"))
        self.assertEqual(date(1997, 1, 1), process_incomplete_date("1997"))

    def test_set_date_month_end(self):
        self.assertEqual(date(1994, 8, 28), process_incomplete_date("28/08/1994", True))
        self.assertEqual(date(1994, 8, 31), process_incomplete_date("08/1994", True))
        self.assertEqual(date(1994, 2, 28), process_incomplete_date("1994/02", True))
        self.assertEqual(date(1994, 12, 31), process_incomplete_date("1994", True))

    def test_set_date_failure(self):
        with self.assertRaises(ValueError) as cm:
            process_incomplete_date("31/02/2012")
        self.assertIn("day is out of range for month", str(cm.exception))

        with self.assertRaises(ValueError) as cm:
            process_incomplete_date("20/14/2015")
        self.assertIn("month must be in 1..12", str(cm.exception))

        with self.assertRaises(ValueError) as cm:
            process_incomplete_date("20")


class FuncViewsTC(CubicWebTC):

    def test_eac_import_ok(self):
        regid = 'saem_ref.eac-import'
        fname = 'FRAD033_EAC_00001_simplified.xml'
        with self.admin_access.web_request() as req:
            anything = req.execute('Any X LIMIT 1')
            # simply test the form properly render and is well formed
            self.view(regid, rset=anything, req=req, template=None)
            fields = {'file': (fname, open(self.datapath('EAC/' + fname)))}
            req.form = self.fake_form(regid, fields)
            # now actually test the import
            req.view(regid)
            rset = req.find('Agent', name=u'Gironde. Conseil général')
            self.assertTrue(rset)

    def test_eac_non_unique_isni(self):
        regid = 'saem_ref.eac-import'
        fname = 'FRAD033_EAC_00001_simplified.xml'
        # Query for agents not related to a CWUser
        agent_rql = 'Any X WHERE X is Agent, NOT EXISTS(X agent_user U)'
        with self.admin_access.client_cnx() as cnx:
            akind = cnx.find('AgentKind', name=u'person').one()
            # ISNI is the same as the agent in EAC file.
            cnx.create_entity('Agent', name=u'bob', isni=u'22330001300016',
                              agent_kind=akind)
            cnx.commit()
            rset = cnx.execute(agent_rql)
            self.assertEqual(len(rset), 1)
        with self.admin_access.web_request() as req:
            anything = req.execute('Any X LIMIT 1')
            # simply test the form properly render and is well formed
            self.view(regid, rset=anything, req=req, template=None)
            fields = {'file': (fname, open(self.datapath('EAC/' + fname)))}
            req.form = self.fake_form(regid, fields)
            # now actually test the import
            html = req.view(regid)
            self.assertIn('EAC import failed', html)
            # Still only one Agent.
            rset = req.execute(agent_rql)
            self.assertEqual(len(rset), 1)

    def test_eac_invalid_xml(self):
        regid = 'saem_ref.eac-import'
        fname = 'invalid_xml.xml'
        with self.admin_access.web_request() as req:
            fields = {'file': (fname, open(self.datapath('EAC/' + fname)))}
            req.form = self.fake_form(regid, fields)
            # now actually test the import
            html = req.view(regid)
            self.assertIn('Invalid XML file', html)

    def test_eac_missing_tag(self):
        regid = 'saem_ref.eac-import'
        fname = 'missing_tag.xml'
        with self.admin_access.web_request() as req:
            fields = {'file': (fname, open(self.datapath('EAC/' + fname)))}
            req.form = self.fake_form(regid, fields)
            # now actually test the import
            html = req.view(regid)
            self.assertIn('Missing tag cpfDescription in XML file', html)

    def test_highlight_script_execution(self):
        with self.admin_access.client_cnx() as cnx:
            scheme = cnx.create_entity('ConceptScheme', title=u'my thesaurus')
            cnx.commit()
            url = scheme.absolute_url(highlight='toto')
        self.assertIn(
            '$(document).ready(function(){$("h1, h2, h3, h4, h5, table tbody td")'
            '.highlight("toto");});}',
            self.http_publish(url)[0])

    def test_highlight_on_rql_plain_text_search_same_etype(self):
        with self.admin_access.client_cnx() as cnx:
            scheme = cnx.create_entity('ConceptScheme', title=u'my thesaurus')
            concept1 = cnx.create_entity('Concept', in_scheme=scheme, definition=u'toto tata')
            concept2 = cnx.create_entity('Concept', in_scheme=scheme, definition=u'titi toto')
            cnx.create_entity('Label', label=u'toto', language_code=u'fr', label_of=concept1)
            cnx.create_entity('Label', label=u'tutu', language_code=u'fr', label_of=concept2)
            cnx.commit()
        url = 'http://testing.fr/cubicweb/view?rql=toto&__fromsearchbox=1&subvid=tsearch'
        html = self.http_publish(url)[0]
        self.assertIn(
            '<a href="http://testing.fr/cubicweb/%s?highlight=toto" title="">' % concept1.eid, html)
        self.assertIn(
            '<a href="http://testing.fr/cubicweb/%s?highlight=toto" title="">' % concept2.eid, html)

    def test_highlight_on_rql_plain_text_search(self):
        with self.admin_access.client_cnx() as cnx:
            scheme = cnx.create_entity('ConceptScheme', title=u'my thesaurus')
            concept = cnx.create_entity('Concept', in_scheme=scheme, definition=u'toto tata')
            akind = cnx.find('AgentKind', name=u'person').one()
            agent = cnx.create_entity('Agent', name=u'toto', isni=u'1234', agent_kind=akind)
            cnx.create_entity('Label', label=u'tutu', language_code=u'fr', label_of=concept)
            cnx.create_entity('Label', label=u'toti', language_code=u'fr', label_of=concept,
                              kind=u'alternative')
            cnx.commit()
        url = 'http://testing.fr/cubicweb/view?rql=toto&__fromsearchbox=1&subvid=tsearch'
        html = self.http_publish(url)[0]
        self.assertIn(
            '<a href="http://testing.fr/cubicweb/%s?highlight=toto" title="">' % concept.eid, html)
        self.assertIn(
            '<a href="http://testing.fr/cubicweb/%s?highlight=toto" title="">' % agent.eid, html)

    def test_skos_negociation(self):
        with self.admin_access.client_cnx() as cnx:
            scheme = cnx.create_entity('ConceptScheme', title=u'musique')
            scheme.add_concept(u'pop')
            cnx.commit()
        with self.admin_access.web_request(headers={'Accept': 'application/rdf+xml'}) as req:
            result = self.app_handle_request(req, 'conceptscheme')
            with NamedTemporaryFile(delete=False) as fobj:
                try:
                    fobj.write(result)
                    fobj.close()
                    graph = default_graph()
                    graph.load('file://' + fobj.name, rdf_format='xml')
                finally:
                    os.unlink(fobj.name)

    def test_seda_document_type_code_vocabulary(self):
        """Check that we get correct values in the combo box for document type code."""
        with self.admin_access.web_request() as req:
            doc = self.vreg['etypes'].etype_class('SEDADocumentTypeCode')(req)
            form = self.vreg['forms'].select('edition', req, entity=doc)
            field = form.field_by_name('seda_document_type_code_value', 'subject')
            labels = [label for label, _ in field.vocabulary(form)]
            self.assertEqual(labels, [u'CDO', u'PDI', u'PDICTX', u'PDIFIX', u'PDIPRO', u'PDIREF',
                                      u'RI', u'RISEM', u'RISTR'])

    def test_seda_file_type_code_vocabulary(self):
        """Check that we get correct values in the combo box for file type code."""
        with self.admin_access.web_request() as req:
            doc = self.vreg['etypes'].etype_class('SEDAFileTypeCode')(req)
            form = self.vreg['forms'].select('edition', req, entity=doc)
            field = form.field_by_name('seda_file_type_code_value', 'subject')
            values = list(field.vocabulary(form))
            labels = [label for label, _ in values]
            self.assertEqual(len(labels), 367)
            self.assertIn(u'3GPP Audio/Video File 3GPP Audio/Video File', labels)
            self.assertIn(u'ESRI World File Format ESRI World File Format', labels)
            self.assertIn(u'pulse EKKO header file pulse EKKO header file', labels)

    def test_seda_character_set_code_vocabulary(self):
        """Check that we get correct values in the combo box for character set code."""
        with self.admin_access.web_request() as req:
            doc = self.vreg['etypes'].etype_class('SEDACharacterSetCode')(req)
            form = self.vreg['forms'].select('edition', req, entity=doc)
            field = form.field_by_name('seda_character_set_code_value', 'subject')
            values = list(field.vocabulary(form))
            labels = [label for label, _ in values]
            self.assertEqual(len(labels), 256)
            self.assertIn(u'ANSI_X3.110-1983 [RFC1345,KXS2]', labels)
            self.assertIn(u'windows-874', labels)
            self.assertIn(u'UTF-8 [RFC3629]', labels)

    def test_seda_get_related_version(self):
        """Check that we get correct results when asking for `draft`, `published`, `replaced`
        version of a profile."""
        with self.admin_access.web_request() as req:
            profile1 = testutils.publishable_profile(req, title=u'Profile 1')
            req.cnx.commit()
            profile1.cw_adapt_to('IWorkflowable').fire_transition('publish')
            req.cnx.commit()
            profile1.cw_clear_all_caches()
            profile2 = testutils.publishable_profile(req, title=u'Profile 2', seda_replace=profile1)
            req.cnx.commit()
            profile2.cw_adapt_to('IWorkflowable').fire_transition('publish')
            req.cnx.commit()
            profile2.cw_clear_all_caches()
            profile3 = testutils.publishable_profile(req, title=u'Profile 3', seda_replace=profile2)
            req.cnx.commit()
            profile3.cw_adapt_to('IWorkflowable').fire_transition('publish')
            req.cnx.commit()
            profile3.cw_clear_all_caches()
            profile4 = testutils.publishable_profile(req, title=u'Profile 4', seda_replace=profile3)
            req.cnx.commit()

            def unwrap_generator(gen):
                try:
                    return next(iter(gen))
                except StopIteration:
                    return None

            # Draft profile
            box4 = self.vreg['ctxcomponents'].select('saem.seda.relatedprofiles', req,
                                                     entity=profile4)
            self.assertEqual(unwrap_generator(box4.predecessor()).eid, profile3.eid)
            self.assertIsNone(unwrap_generator(box4.current_version(state=u'published')))
            self.assertIsNone(unwrap_generator(box4.current_version(state=u'draft')))
            # Published profile
            box3 = self.vreg['ctxcomponents'].select('saem.seda.relatedprofiles', req,
                                                     entity=profile3)
            self.assertEqual(unwrap_generator(box3.predecessor()).eid, profile2.eid)
            self.assertIsNone(unwrap_generator(box3.current_version(state=u'published')))
            self.assertEqual(unwrap_generator(box3.current_version(state=u'draft')).eid,
                             profile4.eid)
            # Deprecated profile
            box2 = self.vreg['ctxcomponents'].select('saem.seda.relatedprofiles', req,
                                                     entity=profile2)
            self.assertIsNone(unwrap_generator(box2.predecessor()))
            self.assertEqual(unwrap_generator(box2.current_version(state=u'published')).eid,
                             profile3.eid)
            self.assertEqual(unwrap_generator(box2.current_version(state=u'draft')).eid,
                             profile4.eid)
            # Older deprecated profile
            box1 = self.vreg['ctxcomponents'].select('saem.seda.relatedprofiles', req,
                                                     entity=profile1)
            self.assertIsNone(unwrap_generator(box1.predecessor()))
            self.assertEqual(unwrap_generator(box1.current_version(state=u'published')).eid,
                             profile3.eid)
            self.assertEqual(unwrap_generator(box1.current_version(state=u'draft')).eid,
                             profile4.eid)

    def test_seda_actions_notype_to_import(self):
        with self.admin_access.web_request() as req:
            profile = testutils.setup_seda_profile(req)
            req.cnx.commit()
            profile._cw = req  # XXX
            actions = self.pactionsdict(req, profile.as_rset())
            self.assertIn(seda.SEDAImportProfileArchiveObjectAction, actions['moreactions'])
            self.assertNotIn(seda.SEDAImportProfileDocumentAction, actions['moreactions'])
            actions = self.pactionsdict(req, profile.archives[0].as_rset())
            self.assertIn(seda.SEDAImportProfileArchiveObjectAction, actions['moreactions'])
            self.assertIn(seda.SEDAImportProfileDocumentAction, actions['moreactions'])
        with self.new_access('anon').web_request() as req:
            profile = req.entity_from_eid(profile.eid)
            actions = self.pactionsdict(req, profile.as_rset())
            self.assertNotIn(seda.SEDAImportProfileArchiveObjectAction, actions['moreactions'])
            self.assertNotIn(seda.SEDAImportProfileDocumentAction, actions['moreactions'])

    def test_seda_actions_not_exportable(self):
        with self.admin_access.web_request() as req:
            profile = req.create_entity('SEDAProfile')
            req.cnx.commit()
            profile._cw = req  # XXX
            actions = self.pactionsdict(req, profile.as_rset())
            self.assertNotIn(seda.SEDA1DownloadAction, actions['moreactions'])
            self.assertNotIn(seda.SEDA02DownloadAction, actions['moreactions'])
            req.create_entity('ProfileArchiveObject',
                              seda_name=req.create_entity('SEDAName'),
                              seda_parent=profile)
            req.cnx.commit()
            profile.cw_clear_all_caches()
        with self.admin_access.web_request() as req:
            profile = req.entity_from_eid(profile.eid)
            actions = self.pactionsdict(req, profile.as_rset())
            self.assertIn(seda.SEDA1DownloadAction, actions['moreactions'])
            self.assertIn(seda.SEDA02DownloadAction, actions['moreactions'])

    def test_ark_agent_creation(self):
        with self.admin_access.web_request() as req:
            akind = req.cnx.find('AgentKind', name=u'person').one()
            agent = self.vreg['etypes'].etype_class('Agent')(req)
            agent.eid = 'A'
            fields = {role_name('name', 'subject'): u'007',
                      role_name('ark', 'subject'): u'',
                      role_name('agent_kind', 'subject'): str(akind.eid)}
            req.form = self.fake_form('edition', entity_field_dicts=[(agent, fields)])
            eid = int(self.expect_redirect_handle_request(req)[0])
            agent = req.cnx.entity_from_eid(eid)
            self.assertEqual(agent.ark, u'saemref-test/%09d' % eid)

    def test_ark_scheme_creation(self):
        with self.admin_access.web_request() as req:
            scheme = self.vreg['etypes'].etype_class('ConceptScheme')(req)
            scheme.eid = 'A'
            fields = {role_name('ark', 'subject'): u''}
            req.form = self.fake_form('edition', entity_field_dicts=[(scheme, fields)])
            eid = int(self.expect_redirect_handle_request(req)[0])
            scheme = req.cnx.entity_from_eid(eid)
            self.assertEqual(scheme.ark, u'saemref-test/%09d' % eid)
            concept = self.vreg['etypes'].etype_class('Concept')(req)
            concept.eid = 'A'
            concept_fields = {role_name('in_scheme', 'subject'): str(scheme.eid),
                              role_name('ark', 'subject'): u''}
            label = self.vreg['etypes'].etype_class('Label')(req)
            label.eid = 'B'
            label_fields = {role_name('label', 'subject'): u'Hello',
                            role_name('label_of', 'subject'): 'A'}
            req.form = self.fake_form('edition', entity_field_dicts=[(concept, concept_fields),
                                                                     (label, label_fields)])
            eid = int(self.expect_redirect_handle_request(req)[0])
            concept = req.cnx.entity_from_eid(eid)
            self.assertEqual(concept.ark, u'saemref-test/%09d' % eid)

    def test_ark_url_rewrite(self):
        with self.admin_access.web_request() as req:
            rewriter = self.vreg['urlrewriting'].select('schemabased', req)
            _pmid, rset = rewriter.rewrite(req, u'/ark:/JoE/Dalton')
            self.assertEqual(rset.printable_rql(), 'Any X WHERE X ark "JoE/Dalton"')

    def test_ark_ws(self):
        with self.admin_access.web_request(headers={'Accept': 'application/json'},
                                           method='POST') as req:
            result = self.app_handle_request(req, 'ark')
            self.assertEqual(json.loads(result),
                             [{'ark': 'saemref-test/ext-000000001'}])
        with self.admin_access.web_request(headers={'Accept': 'application/json'}) as req:
            result = self.app_handle_request(req, 'ark')
            self.assertEqual(json.loads(result),
                             [{'error': 'This service is only accessible using POST.'}])
        with self.new_access('anon').web_request(headers={'Accept': 'application/json'},
                                                 method='POST') as req:
            result = self.app_handle_request(req, 'ark')
            self.assertEqual(json.loads(result),
                             [{'error': 'This service requires authentication.'}])

    def test_agents_list(self):
        with self.admin_access.web_request() as req:
            req.cnx.create_entity('Agent', name=u'bob')
            vid, rset = AgentRestPathEvaluator(self).evaluate_path(req, ['Agent'])
            self.assertEqual(vid, None)
            self.assertEqual(len(rset), 1)  # agent created for e.g. admin not displayed


if __name__ == '__main__':
    unittest_main()
