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
"""cubicweb-saem-ref SKOS entity's classes"""

from cubicweb.predicates import is_instance, score_entity

from cubes.skos.entities import ConceptSchemeRDFPrimaryAdapter
from cubes.saem_ref.entities import oai


# prefetch 'ark' attribute of concept for RDF export
ConceptSchemeRDFPrimaryAdapter.concept_attributes.append('ark')


class ConceptSchemeOAIPMHRecordAdapter(oai.OAIPMHActiveRecordAdapter):
    """OAI-PMH adapter for ConceptScheme entity type."""
    __select__ = oai.OAIPMHActiveRecordAdapter.__select__ & is_instance('ConceptScheme')
    metadata_view = 'list.rdf'

    @classmethod
    def set_definition(cls):
        return oai.PublicETypeOAISetSpec(
            'ConceptScheme', cls.identifier_attribute)


class ConceptInPublicSchemeETypeOAISetSpec(oai.ETypeOAISetSpec):
    """OAI-PMH set specifier matching on "Concept" entity type and fetching
    concepts related to scheme not in "draft" state.
    """

    def __init__(self):
        super(ConceptInPublicSchemeETypeOAISetSpec, self).__init__(
            'Concept', 'ark')

    def setspec_restrictions(self, value=None):
        return 'X in_scheme Y, Y in_state ST, NOT ST name "draft"', {}


class ConceptInPublicSchemeRelatedEntityOAISetSpec(oai.RelatedEntityOAISetSpec):
    """OAI-PMH second-level set specifier to match "Concept" entity type
    related to scheme not in "draft" state.
    """

    def __init__(self):
        super(ConceptInPublicSchemeRelatedEntityOAISetSpec, self).__init__(
            'in_scheme', 'ConceptScheme', 'ark',
            description=u'A concept in scheme identified by {0}')

    def setspecs(self, cnx):
        rset = cnx.execute('Any A WHERE X is ConceptScheme, X ark A,'
                           '            X in_state ST, NOT ST name "draft"')
        for value, in rset.rows:
            yield value, self.description.format(value)


def not_in_draft_scheme(concept):
    """Return True if `concept` is in a ConceptScheme not in "draft" state.
    """
    return concept.in_scheme[0].in_state[0].name != 'draft'


class ConceptOAIPMHRecordAdapter(oai.ArkOAIPMHRecordAdapter):
    """OAI-PMH adapter for ConceptScheme entity type."""
    __select__ = (oai.ArkOAIPMHRecordAdapter.__select__ & is_instance('Concept') &
                  score_entity(not_in_draft_scheme))
    metadata_view = 'primary.rdf'

    @classmethod
    def set_definition(cls):
        specifier = ConceptInPublicSchemeETypeOAISetSpec()
        specifier['in_scheme'] = ConceptInPublicSchemeRelatedEntityOAISetSpec()
        return specifier
