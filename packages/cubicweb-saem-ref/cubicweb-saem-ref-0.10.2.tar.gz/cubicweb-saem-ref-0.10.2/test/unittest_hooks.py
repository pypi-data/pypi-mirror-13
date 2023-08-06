"""cubicweb-saem_ref unit tests for hooks"""

from datetime import datetime, timedelta
from time import mktime

import pytz

from logilab.common.testlib import TestCase
from yams import ValidationError

from cubicweb.devtools.testlib import CubicWebTC

from cubes.saem_ref.hooks import extract_ark

import testutils

YESTERDAY = datetime.now(tz=pytz.utc) - timedelta(days=1)


def create_agent(cnx, name, kind='person', **kwargs):
    akind = cnx.find('AgentKind', name=kind).one()
    return cnx.create_entity('Agent', name=name, agent_kind=akind, **kwargs)


class SAEMRefHooksTC(CubicWebTC):

    def assertMDNow(self, entity):
        entity.cw_clear_all_caches()
        self.assertAlmostEqual(mktime(entity.modification_date.timetuple()),
                               mktime(datetime.utcnow().timetuple()), delta=60)

    def resetMD(self, cnx, *entities):
        for entity in entities:
            with cnx.deny_all_hooks_but():
                entity.cw_set(modification_date=YESTERDAY)
        cnx.commit()

    def test_reset_md(self):
        """Ensure `resetMD` method above works."""
        with self.admin_access.repo_cnx() as cnx:
            agent = create_agent(cnx, u'bob')
            cnx.commit()
            self.resetMD(cnx, agent)
            agent.cw_clear_all_caches()
            self.assertEqual(agent.modification_date, YESTERDAY)

    def test_sync_scheme_md(self):
        with self.admin_access.repo_cnx() as cnx:
            scheme = cnx.create_entity('ConceptScheme', title=u'my thesaurus')
            cnx.commit()
            self.resetMD(cnx, scheme)
            c1 = cnx.create_entity('Concept', in_scheme=scheme)
            cnx.create_entity('Label', label=u'concept 1', language_code=u'fr', label_of=c1)
            cnx.commit()
            self.assertMDNow(scheme)
            self.resetMD(cnx, scheme)
            lab = cnx.create_entity('Label', label=u'concept 1.1', language_code=u'en',
                                    label_of=c1)
            cnx.commit()
            self.assertMDNow(scheme)
            self.resetMD(cnx, scheme)
            lab.cw_set(label=u'concept 1.1.1')
            cnx.commit()
            self.assertMDNow(scheme)
            self.resetMD(cnx, scheme, c1)
            c2 = c1.add_concept(u'sub concept')
            cnx.commit()
            self.assertMDNow(c1)
            self.assertMDNow(scheme)
            self.resetMD(cnx, scheme, c1, c2)
            c2.add_concept(u'sub-sub concept')
            cnx.commit()
            self.assertMDNow(c2)
            self.assertMDNow(c1)
            self.assertMDNow(scheme)
            self.resetMD(cnx, scheme, c1, c2)
            c2.preferred_label[0].cw_set(label=u'sub concept 2')
            cnx.commit()
            self.assertMDNow(c2)
            self.assertMDNow(c1)
            self.assertMDNow(scheme)

    def test_sync_profile_md(self):
        with self.admin_access.repo_cnx() as cnx:
            profile = testutils.setup_seda_profile(cnx)
            profile.cw_set(modification_date=YESTERDAY)
            cnx.commit()
            archive = profile.archives[0]
            # edit composite children
            archive.seda_name[0].cw_set(value=u'archive name')
            cnx.commit()
            self.assertMDNow(profile)
            self.resetMD(cnx, profile)
            # edit link from root to an entity which is not part of the container
            arch = cnx.create_entity('Agent', name=u'marcel archives',
                                     agent_kind=cnx.find('AgentKind', name=u'person').one(),
                                     archival_role=cnx.find('ArchivalRole', name='archival').one())
            agent = cnx.create_entity('Agent', name=u'marcel',
                                      agent_kind=cnx.find('AgentKind', name=u'person').one(),
                                      archival_agent=arch,
                                      archival_role=cnx.find('ArchivalRole', name='deposit').one())
            profile.cw_set(seda_transferring_agent=agent)
            cnx.commit()
            self.assertMDNow(profile)
            self.resetMD(cnx, profile)
            # edit link from composite children to an entity which is not part of the container
            code = testutils.concept(cnx, 'AR038')
            archive.seda_access_restriction_code[0].cw_set(seda_access_restriction_code_value=code)
            cnx.commit()
            self.assertMDNow(profile)
            self.resetMD(cnx, profile)
            archive.seda_access_restriction_code[0].cw_set(seda_access_restriction_code_value=None)
            cnx.commit()
            self.assertMDNow(profile)
            self.resetMD(cnx, profile)
            # edit relation to a composite children
            arc = cnx.create_entity('SEDAAppraisalRuleCode')
            ard = cnx.create_entity('SEDAAppraisalRuleDuration')
            ar = cnx.create_entity('SEDAAppraisalRule', seda_appraisal_rule_code=arc,
                                   seda_appraisal_rule_duration=ard)
            archive.cw_set(seda_appraisal_rule=ar)
            cnx.commit()
            self.assertMDNow(profile)
            self.resetMD(cnx, profile)
            ar.cw_delete()
            cnx.commit()
            self.assertMDNow(profile)
            self.resetMD(cnx, profile)

    def test_externaluri_to_concept(self):
        with self.admin_access.repo_cnx() as cnx:
            # create some agent and related objects
            agent = create_agent(cnx, u'bob')
            address = cnx.create_entity('PostalAddress', street=u"1 av. de l'europe",
                                        postalcode=u'31400', city=u'Toulouse')
            place = cnx.create_entity('AgentPlace', place_address=address, place_agent=agent)
            function = cnx.create_entity('AgentFunction', name=u'sponge', function_agent=agent)
            info = cnx.create_entity('LegalStatus', legal_status_agent=agent)
            cnx.commit()
            # create some external uri and link it to place, function and information entities
            exturi = cnx.create_entity('ExternalUri', cwuri=u'http://someuri/someobject',
                                       uri=u'http://someuri/someobject',
                                       reverse_equivalent_concept=[place, function, info])
            cnx.commit()
            # now insert a concept with the external uri as cwuri
            scheme = cnx.create_entity('ConceptScheme')
            concept = scheme.add_concept(u'some object', cwuri=u'http://someuri/someobject')
            cnx.commit()
            # ensure the external uri has been replaced by the concept and deleted
            place.cw_clear_all_caches()
            self.assertEqual(place.equivalent_concept[0].eid, concept.eid)
            function.cw_clear_all_caches()
            self.assertEqual(function.equivalent_concept[0].eid, concept.eid)
            info.cw_clear_all_caches()
            self.assertEqual(info.equivalent_concept[0].eid, concept.eid)
            self.failIf(cnx.execute('Any X WHERE X eid %(x)s', {'x': exturi.eid}))

    def test_externaluri_to_agent_subject(self):
        with self.admin_access.repo_cnx() as cnx:
            bob = create_agent(cnx, u'bob')
            exturi = cnx.create_entity('ExternalUri', cwuri=u'a/b/c', uri=u'a/b/c')
            arelation = cnx.create_entity('AssociationRelation',
                                          association_from=bob,
                                          association_to=exturi)
            cnx.commit()
            alice = create_agent(cnx, u'alice', cwuri=u'a/b/c')
            cnx.commit()
            arelation.cw_clear_all_caches()
            self.assertEqual(arelation.association_to[0], alice)
            self.failIf(cnx.execute('Any X WHERE X eid %(x)s', {'x': exturi.eid}))

    def test_externaluri_to_agent_object(self):
        with self.admin_access.repo_cnx() as cnx:
            bob = create_agent(cnx, u'bob')
            exturi = cnx.create_entity('ExternalUri', cwuri=u'a/b/c', uri=u'a/b/c')
            arelation = cnx.create_entity('AssociationRelation',
                                          association_from=exturi,
                                          association_to=bob)
            cnx.commit()
            alice = create_agent(cnx, u'alice', cwuri=u'a/b/c')
            cnx.commit()
            arelation.cw_clear_all_caches()
            self.assertEqual(arelation.association_from[0], alice)
            self.failIf(cnx.execute('Any X WHERE X eid %(x)s', {'x': exturi.eid}))

    def test_ark_generation_agent(self):
        with self.admin_access.repo_cnx() as cnx:
            agent = create_agent(cnx, u'bob')
            cnx.commit()
            self.assertEqual(agent.ark, 'saemref-test/%09d' % agent.eid)
            self.assertEqual(agent.cwuri, 'ark:/saemref-test/%09d' % agent.eid)
            agent = create_agent(cnx, u'john', ark=u'authority/123456')
            cnx.commit()
            self.assertEqual(agent.ark, 'authority/123456')
            self.assertEqual(agent.cwuri, 'ark:/authority/123456')
            agent = create_agent(cnx, u'alf', cwuri=u'http://someuri/someagent')
            cnx.commit()
            self.assertEqual(agent.ark, 'saemref-test/%09d' % agent.eid)
            self.assertEqual(agent.cwuri, 'http://someuri/someagent')

    def test_ark_generation_seda_profile(self):
        with self.admin_access.repo_cnx() as cnx:
            profile = testutils.setup_seda_profile(cnx)
            self.assertEqual(profile.ark, 'saemref-test/{0:09d}'.format(profile.eid))
            self.assertEqual(profile.cwuri, 'ark:/saemref-test/{0:09d}'.format(profile.eid))
            # Profile with given ark
            profile = testutils.setup_seda_profile(cnx, ark=u'authority/124')
            self.assertEqual(profile.ark, 'authority/124')
            self.assertEqual(profile.cwuri, 'ark:/authority/124')
            # Imported profile with cwuri
            profile = testutils.setup_seda_profile(cnx,
                                                   cwuri=u'http://example.org/profile/125')
            self.assertEqual(profile.ark, 'saemref-test/{0:09d}'.format(profile.eid))
            self.assertEqual(profile.cwuri, 'http://example.org/profile/125')

    def test_ark_generation_concept(self):
        with self.admin_access.repo_cnx() as cnx:
            scheme = cnx.create_entity('ConceptScheme')
            concept = scheme.add_concept(u'some object')
            cnx.commit()
            self.assertEqual(scheme.ark, 'saemref-test/%09d' % scheme.eid)
            self.assertEqual(scheme.cwuri,
                             'ark:/saemref-test/%09d' % scheme.eid)
            self.assertEqual(concept.ark, 'saemref-test/%09d' % concept.eid)
            self.assertEqual(concept.cwuri,
                             'ark:/saemref-test/%09d' % concept.eid)
            scheme = cnx.create_entity('ConceptScheme', cwuri=u'http://someuri/somescheme')
            concept = scheme.add_concept(u'some object', cwuri=u'http://someuri/someconcept')
            cnx.commit()
            self.assertEqual(scheme.ark, 'saemref-test/%09d' % scheme.eid)
            self.assertEqual(scheme.cwuri, 'http://someuri/somescheme')
            self.assertEqual(concept.ark, 'saemref-test/%09d' % concept.eid)
            self.assertEqual(concept.cwuri, 'http://someuri/someconcept')
            scheme = cnx.create_entity('ConceptScheme', cwuri=u'http://dcf/res/ark:/67717/Matiere')
            concept = scheme.add_concept(u'some object', cwuri=u'http://dcf/res/ark:/67717/1234')
            cnx.commit()
            self.assertEqual(scheme.ark, '67717/Matiere')
            self.assertEqual(scheme.cwuri, 'http://dcf/res/ark:/67717/Matiere')
            self.assertEqual(concept.ark, '67717/1234')
            self.assertEqual(concept.cwuri, 'http://dcf/res/ark:/67717/1234')

    def test_check_archival_agent_relation(self):
        with self.admin_access.repo_cnx() as cnx:
            archival = cnx.find('ArchivalRole', name=u'archival').one()
            archivist = cnx.create_entity('Agent',
                                          name=u'archivist',
                                          archival_role=archival,
                                          agent_kind=cnx.find('AgentKind', name=u'person').one())
            cnx.commit()
            deposit = cnx.find('ArchivalRole', name=u'deposit').one()
            with self.assertRaises(ValidationError) as cm:
                cnx.create_entity('Agent', name=u'depositor', archival_role=deposit)
                cnx.commit()
            self.assertEqual(cm.exception.errors,
                             {'archival_agent-subject':
                              'this relation is mandatory on deposit agents'})
            cnx.rollback()
            # check it is not mandatory for another archival role
            control = cnx.find('ArchivalRole', name=u'control').one()
            cnx.create_entity('Agent', name=u'tata',
                              archival_role=control,
                              agent_kind=cnx.find('AgentKind', name=u'person').one())
            # check no error if we give a archival_agent to depositor
            depositor = cnx.create_entity('Agent', name=u'depositor',
                                          archival_role=deposit,
                                          archival_agent=archivist,
                                          agent_kind=cnx.find('AgentKind', name=u'person').one())
            # check one can change the archival agent of a deposit agent
            new_archivist = cnx.create_entity('Agent', name=u'new_archivist',
                                              archival_role=archival,
                                              agent_kind=cnx.find('AgentKind',
                                                                  name=u'person').one())
            depositor.cw_set(archival_agent=new_archivist)
            cnx.commit()
            # check one can't remove the archival agent of a deposit agent
            with self.assertRaises(ValidationError) as cm:
                depositor.cw_set(archival_agent=None)
                cnx.commit()
            self.assertEqual(cm.exception.errors,
                             {'archival_agent-subject':
                              'this relation is mandatory on deposit agents'})
            cnx.rollback()
            # Check it is possible to delete an archival agent if it is not linked to any deposit
            # agent
            cnx.execute('DELETE Agent X WHERE X eid %s' % archivist.eid)
            # check that if an archival agent is responsible of a deposit agent, it can't be deleted
            with self.assertRaises(ValidationError) as cm:
                cnx.execute('DELETE Agent X WHERE X eid %s' % new_archivist.eid)
            self.assertEqual(cm.exception.errors,
                             {'archival_role-subject':
                              'this agent is the archival agent of other agents, therefore the '
                              'role "archival" cannot be deleted'})
            cnx.rollback()
            # check that if an archival agent is responsible of a deposit agent, its "archival" role
            # can't be deleted
            with self.assertRaises(ValidationError) as cm:
                new_archivist.cw_set(archival_role=None)
            self.assertEqual(cm.exception.errors,
                             {'archival_role-subject':
                              'this agent is the archival agent of other agents, therefore the '
                              'role "archival" cannot be deleted'})


class ExtractArkTC(TestCase):

    def test_ok(self):
        self.assertEqual(extract_ark('http://dcf/res/ark:/67717/1234'), '67717/1234')
        self.assertEqual(extract_ark('http://dcf/res/ark:/67717/1234#something'), '67717/1234')
        self.assertEqual(extract_ark('http://dcf/res/ark:/67717/1234?value'), '67717/1234')
        self.assertEqual(extract_ark('http://dcf/res/ark:/67717/1234/sub'), '67717/1234')
        self.assertEqual(extract_ark('ark:/67717/1234'), '67717/1234')

    def test_ko(self):
        self.assertEqual(extract_ark('http://dcf/res/ark:/67717'), None)
        self.assertEqual(extract_ark('http://someuri/67717/1234'), None)


class AgentUserTC(CubicWebTC):

    def test_agent_added(self):
        with self.admin_access.repo_cnx() as cnx:
            bob = self.create_user(cnx, u'bob')
            cnx.commit()
            rset = cnx.find('Agent', name=u'bob')
            self.assertEqual(len(rset), 1)
            agent = rset.one()
            self.assertEqual(agent.agent_kind[0].name, u'person')
            self.assertEqual(agent.agent_user[0], bob)


class EntityLifeCycleTC(CubicWebTC):

    def setup_database(self):
        with self.admin_access.repo_cnx() as cnx:
            bob = self.create_user(cnx, u'bob')
            cnx.commit()
            self.bob_eid = bob.reverse_agent_user[0].eid
            self.akind_eid = cnx.create_entity('AgentKind', name=u'in black').eid
            cnx.create_entity('AgentKind', name=u'space beast')
            cnx.commit()

    def _check_create(self, cnx, eid, msg):
        activity = cnx.find('Activity', type=u'create', used=eid).one()
        self.assertEqual(activity.associated_with[0].eid, self.bob_eid)
        self.assertEqual(activity.generated[0].eid, eid)
        self.assertEqual(activity.description, msg)

    def _check_modification(self, cnx, eid, msg):
        activity = cnx.find('Activity', type=u'modify', used=eid).one()
        self.assertEqual(activity.associated_with[0].eid, self.bob_eid)
        self.assertEqual(activity.used[0].eid, eid)
        self.assertEqual(activity.generated[0].eid, eid)
        self.assertEqual(activity.description, msg)

    def test_agent_create_update(self):
        with self.new_access(u'bob').repo_cnx() as cnx:
            agent = cnx.create_entity('Agent', name=u'Smith', agent_kind=self.akind_eid)
            cnx.commit()
            self.set_description('agent creation')
            self._check_create(cnx, agent.eid, 'created agent')
            agent.cw_set(isni=u'123', name=u'Adam')
            cnx.commit()
            self.set_description('agent update')
            self._check_modification(cnx, agent.eid, 'modified isni, name')

    def test_agent_related_change(self):
        with self.new_access(u'bob').repo_cnx() as cnx:
            agent = cnx.create_entity('Agent', name=u'Smith', agent_kind=self.akind_eid)
            cnx.commit()
            agent.cw_set(agent_kind=cnx.execute('AgentKind X WHERE X name "space beast"').one())
            cnx.commit()
            self._check_modification(cnx, agent.eid, 'modified agent_kind')

    def test_agent_add_component(self):
        with self.new_access(u'bob').repo_cnx() as cnx:
            agent = cnx.create_entity('Agent', name=u'Smith', agent_kind=self.akind_eid)
            cnx.commit()
            cnx.create_entity('PhoneNumber', number=u'99 88 77', reverse_phone_number=agent)
            cnx.commit()
            self._check_modification(cnx, agent.eid, 'added phone_number')

    def test_agent_delete_component(self):
        with self.new_access(u'bob').repo_cnx() as cnx:
            agent = cnx.create_entity('Agent', name=u'Smith', agent_kind=self.akind_eid)
            pn = cnx.create_entity('PhoneNumber', number=u'99 88 77',
                                   reverse_phone_number=agent)
            cnx.commit()
            pn.cw_delete()
            cnx.commit()
            self._check_modification(cnx, agent.eid, 'removed phone_number')

    def test_agent_update_component(self):
        with self.new_access(u'bob').repo_cnx() as cnx:
            agent = cnx.create_entity('Agent', name=u'Smith', agent_kind=self.akind_eid)
            pn = cnx.create_entity('PhoneNumber', number=u'99 88 77', reverse_phone_number=agent)
            cnx.commit()
            pn.cw_set(number=u'11 22 33')
            cnx.commit()
            self._check_modification(cnx, agent.eid, 'modified phone_number')

    def test_agent_add_subcomponent(self):
        with self.new_access(u'bob').repo_cnx() as cnx:
            agent = cnx.create_entity('Agent', name=u'Smith', agent_kind=self.akind_eid)
            cnx.commit()
            address = cnx.create_entity('PostalAddress', street=u"1 av. de l'europe",
                                        postalcode=u'31400', city=u'Toulouse')
            cnx.create_entity('AgentPlace', place_address=address, place_agent=agent)
            cnx.commit()
            self._check_modification(cnx, agent.eid, 'added place_address, place_agent_object')

    def test_agent_delete_subcomponent(self):
        with self.new_access(u'bob').repo_cnx() as cnx:
            agent = cnx.create_entity('Agent', name=u'Smith', agent_kind=self.akind_eid)
            address = cnx.create_entity('PostalAddress', street=u"1 av. de l'europe",
                                        postalcode=u'31400', city=u'Toulouse')
            cnx.create_entity('AgentPlace', place_address=address, place_agent=agent)
            cnx.commit()
            address.cw_delete()
            cnx.commit()
            self._check_modification(cnx, agent.eid, 'removed place_address')

    def test_agent_update_subcomponent(self):
        with self.new_access(u'bob').repo_cnx() as cnx:
            agent = cnx.create_entity('Agent', name=u'Smith', agent_kind=self.akind_eid)
            address = cnx.create_entity('PostalAddress', street=u"1 av. de l'europe",
                                        postalcode=u'31400', city=u'Toulouse')
            cnx.create_entity('AgentPlace', place_address=address, place_agent=agent)
            cnx.commit()
            address.cw_set(street=u"1 avenue de l'Europe")
            cnx.commit()
            self._check_modification(cnx, agent.eid, 'modified place_address')

    def test_agent_multi_modification(self):
        with self.new_access(u'bob').repo_cnx() as cnx:
            agent = cnx.create_entity('Agent', name=u'Smith', agent_kind=self.akind_eid)
            pn = cnx.create_entity('PhoneNumber', number=u'99 88 77', reverse_phone_number=agent)
            cnx.commit()
            pn.cw_set(number=u'11 22 33')
            address = cnx.create_entity('PostalAddress', street=u"1 av. de l'europe",
                                        postalcode=u'31400', city=u'Toulouse')
            cnx.create_entity('AgentPlace', place_address=address, place_agent=agent)
            agent.cw_set(isni=u'123', name=u'Adam',
                         agent_kind=cnx.execute('AgentKind X WHERE X name "space beast"').one())
            cnx.commit()
            self._check_modification(cnx, agent.eid,
                                     '* modified agent_kind, isni, name, phone_number\n'
                                     '* added place_address, place_agent_object')

    def test_agent2agent_relation(self):
        with self.new_access(u'bob').repo_cnx() as cnx:
            k = cnx.create_entity('Agent', name=u'Agent K', agent_kind=self.akind_eid)
            d = cnx.create_entity('Agent', name=u'Agent D', agent_kind=self.akind_eid)
            cnx.commit()
            cnx.create_entity('AssociationRelation', association_from=k, association_to=d)
            cnx.commit()
            self._check_modification(cnx, k.eid, 'added association_from_object')
            self._check_modification(cnx, d.eid, 'added association_to_object')

    def test_no_activity_generated(self):
        with self.admin_access.repo_cnx() as cnx:
            agent = cnx.create_entity('Agent', name=u'Smith', agent_kind=self.akind_eid)
            cnx.commit()
            kind = cnx.execute('AgentKind X WHERE X name "in black"').one()
            kind.cw_set(name=u'in white')
            cnx.commit()
            self.failIf(cnx.find('Activity', type=u'modify', used=agent.eid))

    def test_concept(self):
        with self.new_access(u'bob').repo_cnx() as cnx:
            scheme = cnx.create_entity('ConceptScheme', title=u'my thesaurus')
            cnx.commit()
            self.set_description('concept scheme creation')
            self._check_create(cnx, scheme.eid, 'created conceptscheme')
            concept = scheme.add_concept(u'hello')
            cnx.commit()
            self.set_description('concept scheme add concept')
            self._check_modification(cnx, scheme.eid, 'added in_scheme_object')
            self.set_description('concept creation')
            self._check_create(cnx, concept.eid, 'created concept')
            subconcept = concept.add_concept(u'goodbye')
            cnx.commit()
            self.set_description('concept add concept')
            self._check_modification(cnx, concept.eid, 'added broader_concept_object')
            self.set_description('subconcept creation')
            self._check_create(cnx, subconcept.eid, 'created concept')
            self.set_description('subconcept creation scheme')
            rset = cnx.execute('Activity X ORDERBY X DESC WHERE X type "modify", X used %(x)s',
                               {'x': scheme.eid})
            self.assertEqual(len(rset), 2)
            self.assertEqual(rset.get_entity(0, 0).description, 'added in_scheme_object')


class SEDAProfileHooksTC(CubicWebTC):

    def test_archive_created(self):
        """Test hook creating a Profile Archive upon creation of a SEDAProfile."""
        with self.admin_access.repo_cnx() as cnx:
            profile = testutils.setup_seda_profile(cnx, complete_archive=False)
            cnx.commit()
            arch = profile.archives[0]
            self.assertTrue(arch.seda_access_restriction_code)
            self.assertTrue(arch.seda_content_description)
            content_desc = arch.content_description
            self.assertTrue(content_desc.seda_description_level)
            self.assertEqual(profile.support_seda_exports, 'SEDA-0.2.xsd, SEDA-1.0.xsd')

    def test_profile_deprecated(self):
        """Test hook deprecating a SEDA Profile upon successor publication."""
        with self.admin_access.repo_cnx() as cnx:
            profile = testutils.setup_seda_profile(cnx, complete_archive=False)
            cnx.commit()
            workflow = profile.cw_adapt_to('IWorkflowable')
            workflow.fire_transition('publish')
            cnx.commit()
            profile.cw_clear_all_caches()
            self.assertEqual(workflow.state, 'published')
            cloned = cnx.create_entity('SEDAProfile', title=u'Clone', seda_replace=profile)
            cnx.commit()
            cloned.cw_adapt_to('IWorkflowable').fire_transition('publish')
            cnx.commit()
            profile.cw_clear_all_caches()
            self.assertEqual(workflow.state, 'deprecated')

    def test_profile_export_compat(self):
        with self.admin_access.client_cnx() as cnx:
            profile = cnx.create_entity('SEDAProfile')
            cnx.commit()
            self.assertEqual(profile.support_seda_exports, '')
            ao = cnx.create_entity('ProfileArchiveObject',
                                   user_cardinality=u'0..1',
                                   seda_name=cnx.create_entity('SEDAName'),
                                   seda_parent=profile)
            cnx.commit()
            self.assertEqual(profile.support_seda_exports, '')
            ao.cw_set(user_cardinality=u'1')
            cnx.commit()
            profile.cw_clear_all_caches()
            self.assertEqual(profile.support_seda_exports, 'SEDA-0.2.xsd, SEDA-1.0.xsd')


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
