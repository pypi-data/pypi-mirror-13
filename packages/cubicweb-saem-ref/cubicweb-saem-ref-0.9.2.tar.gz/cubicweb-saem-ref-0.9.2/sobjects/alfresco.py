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

from datetime import datetime

from logilab.common.textutils import unormalize

from cubicweb.predicates import match_user_groups
from cubicweb.server import Service

from cubes.saem_ref.predicates import is_connector, eid_is_etype
from cubes.saem_ref.lib import alfresco as lib


class _UpToDate(Exception):
    """Internal exception used to indicate that a subtree is up-to-date and doesn't have to be
    synchronized to Alfresco.
    """


class AlfrescoSyncEntityService(Service):
    """Cubicweb service to synchronize an entity"""
    __abstract__ = True
    __select__ = match_user_groups('managers') & is_connector('AlfrescoConnector')

    def mirror_entity(self, entity):
        """return the mirror entity for the given entity or None if it doesn't exist yet"""
        rset = self._cw.execute('Any M,U WHERE M extid U, M mirror_of X, M using_connector C, '
                                'X eid %(x)s, C eid %(c)s', {'x': entity.eid,
                                                             'c': self.connector.eid})
        if rset:
            return rset.get_entity(0, 0)
        else:
            return None

    def mirror(self, entity, node_ref):
        """create a MirrorEntity and commit immediatly, since the REST API call has been done"""
        mirror = self._cw.create_entity('MirrorEntity', extid=unicode(node_ref),
                                        mirror_of=entity, using_connector=self.connector.eid)
        self._cw.commit()
        return mirror

    def method_and_args(self, entity, parent_mirror_entity=None):
        """return (method name, method args) 2-uple to create or update the given entity"""
        mirror = self.mirror_entity(entity)
        if mirror is None:
            method = 'create_%s' % entity.cw_etype.lower()
            args = (entity, )
            if parent_mirror_entity is not None:
                args += (parent_mirror_entity, )
        else:
            method = 'update_%s' % entity.cw_etype.lower()
            args = (entity, mirror)
        return method, args

    def login(self):
        """Connect to Alfresco and save connection data"""
        assert hasattr(self, 'connector')
        self.helper = lib.AlfrescoRESTHelper(self.connector)
        self.helper.login(self.connector.user, self.connector.password)


class AlfrescoSyncConceptSchemeService(AlfrescoSyncEntityService):
    """Cubicweb service to synchronize a ConceptScheme"""
    __regid__ = 'saem_ref.alfresco.sync'
    __select__ = AlfrescoSyncEntityService.__select__ & eid_is_etype('ConceptScheme')

    def call(self, connector_eid, eid):
        self.connector = self._cw.entity_from_eid(connector_eid)
        with self._cw.security_enabled(False, False):
            self.login()
            # mirror the entity
            entity = self._cw.entity_from_eid(eid)
            method, args = self.method_and_args(entity)
            mirror_entity = getattr(self, method)(*args)
            # then iterate on top-concepts and mirror them as well
            self.sync_children(mirror_entity, self._cw.execute(
                'Any X WHERE X in_scheme S, NOT X broader_concept C, S eid %(s)s',
                {'s': eid}).entities())

    def sync_children(self, parent_mirror_entity, children):
        try:
            for concept in children:
                self.recursive_sync(concept, parent_mirror_entity)
            parent_mirror_entity.cw_set(modification_date=datetime.utcnow(), error_flag=False)
        except Exception:
            # unexpected error while synchronizing some children
            parent_mirror_entity.cw_set(modification_date=datetime.utcnow(), error_flag=True)
            raise

    def recursive_sync(self, entity, parent_mirror_entity):
        """recursivly synchronize a concept entity and its children (narrow concepts)"""
        method, args = self.method_and_args(entity, parent_mirror_entity)
        try:
            mirror_entity = getattr(self, method)(*args)
        except _UpToDate:
            return  # no need for update of the subtree
        # sort for test predictability
        self.sync_children(mirror_entity, sorted(entity.narrower_concept, key=lambda x: x.eid))

    def create_conceptscheme(self, entity):
        """create a ConceptScheme: alfresco's root category"""
        store_ref = self.helper.add_root_category(entity.title)
        return self.mirror(entity, store_ref)

    def update_conceptscheme(self, entity, mirror_entity):
        """update a ConceptScheme already existing as an alfresco's root category"""
        self.helper.update_category(mirror_entity.extid, entity.title)
        return mirror_entity

    def create_concept(self, entity, parent_mirror_entity):
        """create a Concept: alfresco's sub-category"""
        name = entity.label(self.connector.language_code)
        store_ref = self.helper.add_sub_category(parent_mirror_entity.extid, name)
        return self.mirror(entity, store_ref)

    def update_concept(self, entity, mirror_entity):
        """update a Concept already existing as an alfresco's sub-category"""
        # thanks to hooks updating concept's modification date upon modification in its sub-tree, we
        # know that if mirror's entity modification date is greater or equal the concept's
        # modification date, the whole sub-tree is up-to-date
        if (not mirror_entity.error_flag
                and mirror_entity.modification_date >= entity.modification_date):
            raise _UpToDate()
        name = entity.label(self.connector.language_code)
        self.helper.update_category(mirror_entity.extid, name)
        # XXX what if concept has been reparented
        return mirror_entity


class AlfrescoSyncSEDAProfileService(AlfrescoSyncEntityService):
    """Cubicweb service to synchronize a SEDAProfile"""
    __regid__ = 'saem_ref.alfresco.sync'
    __select__ = AlfrescoSyncEntityService.__select__ & eid_is_etype('SEDAProfile')

    def call(self, connector_eid, eid):
        self.connector = self._cw.entity_from_eid(connector_eid)
        assert self.connector.sedaprofiles_node is not None, (
            'connector `sedaprofiles_node` attribute unset')
        with self._cw.security_enabled(False, False):
            self.login()
            # mirror the entity
            entity = self._cw.entity_from_eid(eid)
            method, args = self.method_and_args(entity)
            getattr(self, method)(*args)

    @staticmethod
    def _profile_data(entity):
        """Return SEDAProfile data for upload to Alfresco instance."""
        adapter = entity.cw_adapt_to('SEDA-0.2.xsd')
        fname = unormalize(adapter.file_name).encode()
        return fname, adapter.dump()

    def create_sedaprofile(self, entity):
        """Create a SEDAProfile: upload the corresponding file on alfresco

        SEDA_PROFILES_NODE environment variable must be set to the identifier of the node
        corresponding to the directory on which to upload the SEDA profile.
        """
        node_ref = self.helper.add_sedaprofile(*self._profile_data(entity))
        return self.mirror(entity, node_ref)

    def update_sedaprofile(self, entity, mirror_entity):
        """Update a SEDAProfile already existing: replace the corresponding file on alfresco"""
        fname, fcontent = self._profile_data(entity)
        self.helper.update_sedaprofile(fname, fcontent, mirror_entity.extid)
