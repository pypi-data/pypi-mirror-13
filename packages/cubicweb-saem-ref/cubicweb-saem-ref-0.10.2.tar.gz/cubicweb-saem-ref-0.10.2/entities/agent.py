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
"""cubicweb-saem-ref entity's classes for Agent and its associated classes"""

from cubicweb.predicates import is_instance
from cubicweb.entities import AnyEntity, fetch_config

from cubes.skos import rdfio
from cubes.skos.entities import AbstractRDFAdapter

from cubes.saem_ref.entities import oai


def _register_agent_prov_mapping(reg):  # XXX move to the prov cube
    """Register RDF mapping for PROV-O entity types related to Agent.
    """
    reg.register_prefix('prov', 'http://www.w3.org/ns/prov#')
    # reg.register_etype_equivalence('Agent', 'prov:Agent')
    reg.register_etype_equivalence('Activity', 'prov:Activity')
    reg.register_attribute_equivalence('Activity', 'type', 'prov:type')
    reg.register_attribute_equivalence('Activity', 'description', 'prov:label')
    reg.register_attribute_equivalence('Activity', 'start', 'prov:startedAtTime')
    reg.register_attribute_equivalence('Activity', 'end', 'prov:endedAtTime')
    reg.register_relation_equivalence('Activity', 'associated_with', 'Agent',
                                      'prov:wasAssociatedWith')
    reg.register_relation_equivalence('Activity', 'generated', 'Agent', 'prov:generated')
    reg.register_relation_equivalence('Activity', 'used', 'Agent', 'prov:used')


class Agent(AnyEntity):
    __regid__ = 'Agent'
    fetch_attrs, cw_fetch_order = fetch_config(('name', 'agent_kind'))

    @property
    def kind(self):
        """The kind of agent"""
        return self.agent_kind[0].name

    def has_role(self, role):
        """Return true if the agent has the archival role `role` else False"""
        return any(archival_role for archival_role in self.archival_role
                   if archival_role.name == role)

    @property
    def printable_kind(self):
        """The kind of agent, for display"""
        return self.agent_kind[0].printable_value('name')


def _fill_agent_rdf_mapping(reg, agent):
    reg.register_prefix('foaf', 'http://xmlns.com/foaf/0.1/')
    reg.register_prefix('dc', 'http://purl.org/dc/elements/1.1/')
    foaf_kind = {'person': 'Person',
                 'authority': 'Organization',
                 'family': 'Group'}.get(agent.kind, 'Agent')
    reg.register_etype_equivalence('Agent', 'foaf:' + foaf_kind)
    # Standard metadata.
    reg.register_attribute_equivalence('Agent', 'name', 'foaf:name')
    # Additionnal metadata for Asalae export.
    reg.register_attribute_equivalence('Agent', 'ark', 'dc:identifier')


def _complete_agent_rdf_mapping(reg):
    reg.register_prefix('dct', 'http://purl.org/dc/terms/')
    reg.register_prefix('schema_org', 'http://schema.org/')
    reg.register_prefix('vcard', 'http://www.w3.org/2006/vcard/ns#')
    reg.register_attribute_equivalence('Agent', 'creation_date', 'dct:created')
    reg.register_attribute_equivalence('Agent', 'modification_date', 'dct:modified')
    reg.register_attribute_equivalence('Agent', 'start_date', 'schema_org:startDate')
    reg.register_attribute_equivalence('Agent', 'end_date', 'schema_org:endDate')
    reg.register_etype_equivalence('PostalAddress', 'vcard:Location')
    reg.register_attribute_equivalence('PostalAddress', 'street', 'vcard:street-address')
    reg.register_attribute_equivalence('PostalAddress', 'postalcode', 'vcard:postal-code')
    reg.register_attribute_equivalence('PostalAddress', 'city', 'vcard:locality')
    reg.register_attribute_equivalence('PostalAddress', 'country', 'vcard:country-name')
    reg.register_attribute_equivalence('PostalAddress', 'state', 'vcard:region')


class AgentRDFListAdapter(AbstractRDFAdapter):
    __regid__ = 'RDFList'
    __select__ = is_instance('Agent')

    def register_rdf_mapping(self, reg):
        _fill_agent_rdf_mapping(reg, self.entity)


class AgentRDFPrimaryAdapter(AgentRDFListAdapter):
    __regid__ = 'RDFPrimary'

    def register_rdf_mapping(self, reg):
        """RDF mapping for Agent entity type."""
        super(AgentRDFPrimaryAdapter, self).register_rdf_mapping(reg)
        _complete_agent_rdf_mapping(reg)
        reg.register_prefix('saem', 'http://www.logilab.org/saem/0#')
        reg.register_relation_equivalence('Agent', 'contact_point', 'Agent',
                                          'schema_org:contactPoint')
        reg.register_relation_equivalence('Agent', 'archival_agent', 'Agent',
                                          'saem:archivalAgent')

    def fill(self, graph):
        super(AgentRDFPrimaryAdapter, self).fill(graph)
        reg = self.registry
        generator = rdfio.RDFGraphGenerator(graph)
        # Export archival roles for the agent
        for archival_role in self.entity.archival_role:
            graph.add(graph.uri(self.entity.absolute_url()),
                      graph.uri(reg.normalize_uri('vcard:role')),
                      archival_role.name)
        # Export contact agent
        if self.entity.contact_point:
            contact_agent = self.entity.contact_point[0]
            # this is necessary to generate proper foaf:type for the contact agent, else it will
            # reuse the foaf:type of the exported agent
            contact_reg = rdfio.RDFRegistry()
            _fill_agent_rdf_mapping(contact_reg, contact_agent)
            _complete_agent_rdf_mapping(contact_reg)
            generator.add_entity(contact_agent, contact_reg)
        # Export addresses for the agent
        for place in self.entity.reverse_place_agent:
            for address in place.place_address:
                graph.add(graph.uri(self.entity.absolute_url()),
                          graph.uri(reg.normalize_uri('vcard:hasAddress')),
                          graph.uri(address.absolute_url()))
                if place.role:
                    graph.add(graph.uri(address.absolute_url()),
                              graph.uri(reg.normalize_uri('vcard:role')),
                              place.role)
                generator.add_entity(address, reg)
        # Export chronological relations
        for rtype_name, reverse_rtype_name, obj_property, subj_property in [
            ('reverse_chronological_successor', 'chronological_predecessor', 'dct:isReplacedBy',
             'dct:replaces'),
            ('reverse_chronological_predecessor', 'chronological_successor', 'dct:replaces',
             'dct:isreplacedBy')
        ]:
            for chrono_relation in getattr(self.entity, rtype_name):
                for related_agent in getattr(chrono_relation, reverse_rtype_name):
                    graph.add(graph.uri(related_agent.absolute_url()),
                              graph.uri(reg.normalize_uri(obj_property)),
                              graph.uri(self.entity.absolute_url()))
                    graph.add(graph.uri(self.entity.absolute_url()),
                              graph.uri(reg.normalize_uri(subj_property)),
                              graph.uri(related_agent.absolute_url()))


class AgentOAIPMHRecordAdapter(oai.OAIPMHActiveRecordAdapter):
    """OAI-PMH adapter for Agent entity type."""
    __select__ = oai.OAIPMHActiveRecordAdapter.__select__ & is_instance('Agent')
    metadata_view = 'primary.rdf'

    @classmethod
    def set_definition(cls):
        specifier = oai.PublicETypeOAISetSpec(
            'Agent', identifier_attribute=cls.identifier_attribute)
        specifier['role'] = oai.RelatedEntityOAISetSpec(
            'archival_role', 'ArchivalRole', 'name',
            description=u'An agent with {0} archival role')
        specifier['kind'] = oai.RelatedEntityOAISetSpec(
            'agent_kind', 'AgentKind', 'name',
            description=u'An agent of kind {0}',
            exclude=['unknown-agent-kind'])
        return specifier


class AgentKind(AnyEntity):
    __regid__ = 'AgentKind'
    fetch_attrs, cw_fetch_order = fetch_config(('name',))


class ArchivalRole(AnyEntity):
    __regid__ = 'AgentKind'
    fetch_attrs, cw_fetch_order = fetch_config(('name',))


class ChronologicalRelation(AnyEntity):
    __regid__ = 'ChronologicalRelation'

    def dc_description(self):
        if self.description:
            return self.description


class EACResourceRelation(AnyEntity):
    __regid__ = 'EACResourceRelation'

    @property
    def agent(self):
        return self.resource_relation_agent[0]

    @property
    def resource(self):
        return self.resource_relation_resource[0]

    def dc_title(self):
        agent_title = self.agent.dc_title()
        if self.agent_role:
            agent_title += u' (%s)' % self.printable_value('agent_role')
        resource_title = self.resource.dc_title()
        if self.resource_role:
            resource_title += u' (%s)' % self.printable_value('resource_role')
        return (self._cw._('Relation from %(from)s to %(to)s ') %
                {'from': agent_title,
                 'to': resource_title})


class Citation(AnyEntity):
    __regid__ = 'Citation'

    def dc_title(self):
        title = []
        if self.note:
            title.append(self.note)
        if self.uri:
            title.append(u'<{0}>'.format(self.uri))
        if title:
            return u' '.join(title)
        return u'{0} #{1}'.format(self._cw._('Citation'), self.eid)


class SameAsMixIn(object):
    """Mix-in class for entity types supporting vocabulary_source and equivalent_concept relations
    """

    @property
    def scheme(self):
        return self.vocabulary_source and self.vocabulary_source[0] or None

    @property
    def concept(self):
        return self.equivalent_concept and self.equivalent_concept[0] or None


class AgentPlace(SameAsMixIn, AnyEntity):
    __regid__ = 'AgentPlace'


class AgentFunction(SameAsMixIn, AnyEntity):
    __regid__ = 'AgentFunction'


class Mandate(SameAsMixIn, AnyEntity):
    __regid__ = 'Mandate'


class LegalStatus(SameAsMixIn, AnyEntity):
    __regid__ = 'LegalStatus'


class Occupation(SameAsMixIn, AnyEntity):
    __regid__ = 'Occupation'
