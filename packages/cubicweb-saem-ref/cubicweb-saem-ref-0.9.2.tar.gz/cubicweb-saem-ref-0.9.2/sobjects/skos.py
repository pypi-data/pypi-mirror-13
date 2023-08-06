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
"""SKOS import overrides"""

from logilab.common.decorators import cached

from cubicweb.dataimport import MetaGenerator

from cubes.skos import sobjects as skos

from cubes.saem_ref.hooks import set_skos_ark_and_cwuri


class SAEMMetaGennerator(MetaGenerator):
    """SAEM specific meta-generator, necessary when no hooks are activated (e.g. skos import) to
    handle ARK generation and setting of the initial state.

    The ARK generation part is a kind of abuse of the MetaGenerator which is designed to set values
    for meta-data which are shared by all entity types. That being said, it remains the easiest way
    to generate the ark attribute of Concept and ConceptScheme, by overriding init_entity and
    implementing gen_ark (see docstrings below).

    """

    def init_entity(self, entity):
        """overriden so that if and only if entity is a Concept or a ConceptScheme, the `gen_ark`
        callback is called.
        """
        if entity.cw_etype in ('ConceptScheme', 'Concept'):
            self.entity_attrs.insert(0, 'ark')  # insert before cwuri
        try:
            return super(SAEMMetaGennerator, self).init_entity(entity)
        finally:
            if entity.cw_etype in ('ConceptScheme', 'Concept'):
                del self.entity_attrs[0]

    @cached
    def base_etype_dicts(self, entity):
        """Overriden to set state on entities needing it (ie ConceptScheme)."""
        entity, rels = super(SAEMMetaGennerator, self).base_etype_dicts(entity)
        if entity.cw_etype == 'ConceptScheme':
            wf_state = self._cnx.execute('Any S WHERE ET default_workflow WF, ET name %(etype)s, '
                                         'WF initial_state S', {'etype': entity.cw_etype}).one()
            rels['in_state'] = wf_state.eid
        return entity, rels

    def gen_ark(self, entity):
        """ARK generation callback"""
        set_skos_ark_and_cwuri(entity)
        # returning value, even if set by the function, is necessary due to the meta generator
        # implementation
        return entity.cw_edited['ark']


class RDFSKOSImportService(skos.RDFSKOSImportService):
    """service overriden from skos cube to provide functionnalities handled in saem_ref's hooks"""

    def _do_import(self, stream, import_log, **kwargs):
        metagenerator = SAEMMetaGennerator(self._cw)
        return super(RDFSKOSImportService, self)._do_import(stream, import_log,
                                                            metagenerator=metagenerator, **kwargs)


class LCSVSKOSImportService(skos.LCSVSKOSImportService):
    """service overriden from skos cube to provide functionnalities handled in saem_ref's hooks"""

    def _do_import(self, stream, import_log, **kwargs):
        metagenerator = SAEMMetaGennerator(self._cw)
        return super(LCSVSKOSImportService, self)._do_import(stream, import_log,
                                                             metagenerator=metagenerator, **kwargs)


class SKOSParser(skos.SKOSParser):
    """parser overriden from skos cube to provide functionnalities handled in saem_ref's hooks"""

    def _do_import(self, url, raise_on_error):
        metagenerator = SAEMMetaGennerator(self._cw, source=self.source)
        return super(SKOSParser, self)._do_import(url, raise_on_error=raise_on_error,
                                                  metagenerator=metagenerator)


def registration_callback(vreg):
    vreg.register_and_replace(RDFSKOSImportService, skos.RDFSKOSImportService)
    vreg.register_and_replace(LCSVSKOSImportService, skos.LCSVSKOSImportService)
    vreg.register_and_replace(SKOSParser, skos.SKOSParser)
