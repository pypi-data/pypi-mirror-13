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
"""cubicweb-saem-ref views related to Alfresco / As@lae synchronisation"""

from cubicweb.view import EntityView
from cubicweb.predicates import (is_instance, one_line_rset, score_entity,
                                 match_kwargs, match_form_params, match_user_groups)
from cubicweb.web import Redirect, action, component, formwidgets as fw
from cubicweb.web.views import uicfg, tableview, actions

from cubes.skos import to_unicode
from cubes.saem_ref.predicates import etype_exists, entity_has_mirror
from cubes.saem_ref.entities.sync import SynchronizationError


_ = unicode

pvs = uicfg.primaryview_section
abaa = uicfg.actionbox_appearsin_addmenu
affk = uicfg.autoform_field_kwargs

affk.set_field_kwargs('AlfrescoConnector', 'url', widget=fw.TextInput())
affk.set_field_kwargs('AlfrescoConnector', 'sedaprofiles_node', widget=fw.TextInput())
for attr in ('user', 'database', 'dbuser', 'dbpassword', 'dbhost', 'dbport', 'url'):
    affk.set_field_kwargs('AsalaeConnector', attr, widget=fw.TextInput())

# MirrorEntity
pvs.tag_object_of(('MirrorEntity', 'mirror_of', '*'), 'hidden')
pvs.tag_object_of(('*', 'using_connector', '*'), 'hidden')
abaa.tag_object_of(('*', 'using_connector', '*'), False)


class SynchronizeView(EntityView):
    """Handle synchronization of some entity to Alfresco or As@lae"""
    __regid__ = 'saem_ref.connector.sync'
    __select__ = (is_instance('AlfrescoConnector', 'AsalaeConnector')
                  & (match_kwargs('eid') | match_form_params('eid')))

    def entity_call(self, connector):
        try:
            eid = self._cw.form['eid']
        except KeyError:
            eid = self.cw_extra_kwargs['eid']
        eid = int(eid)
        try:
            connector.synchronize(eid)
        except SynchronizationError as exc:
            self.exception('synchronization failure for entity #%d', eid)
            msg_details = to_unicode(exc)
            msg = self._cw._('synchronization failed: %s') % msg_details
        except Exception as exc:
            self.exception('synchronization failure for entity #%d', eid)
            msg_details = self._cw._('see instance logs for details')
            msg = self._cw._('synchronization failed (%s)') % msg_details
        else:
            msg = self._cw._('synchronization successfully completed')
        entity = self._cw.entity_from_eid(eid)
        raise Redirect(entity.absolute_url(__message=msg))


class AbstractMirroredComponent(component.EntityCtxComponent):
    __abstract__ = True
    __regid__ = 'saem_ref.connector.issync'
    __select__ = component.EntityCtxComponent.__select__ & match_user_groups('managers')
    title = _('Synchronization status')
    context = 'navcontentbottom'
    connector_etypes = None  # tuple of connector types to be specified by concrete class

    def render_body(self, w):
        for conn_etype in self.connector_etypes:
            self._cw.view('saem_ref.connector.sync-status', self._cw.find(conn_etype),
                          w=w, eid=self.entity.eid)


class StatusColRenderer(tableview.EntityTableColRenderer):
    entity_sortvalue = None

    def render_entity(self, w, entity):
        sync_status = entity.synchronization_status(self.view.cw_extra_kwargs['eid'])
        w(self._cw._(sync_status))


class SyncActionColRenderer(tableview.EntityTableColRenderer):
    entity_sortvalue = None

    def render_entity(self, w, entity):
        blockers = entity.synchronize_blockers(self.view.cw_extra_kwargs['eid'])
        if blockers:
            w(u'<div class="blocker">%s' %
              self._cw._('The following problem(s) prevents this entity from being synchronized:'))
            w(u'<ul>')
            w(u''.join(u'<li>%s</li>' % msg for msg in blockers))
            w(u'</ul></div>')
        else:
            sync_url = entity.absolute_url(vid='saem_ref.connector.sync',
                                           eid=self.view.cw_extra_kwargs['eid'])
            w('<a href="%s">%s</a>' % (sync_url, self._cw._('synchronize')))


class SynchronizationStatusTable(tableview.EntityTableView):
    __regid__ = 'saem_ref.connector.sync-status'
    __select__ = (match_user_groups('managers')
                  & is_instance('AlfrescoConnector', 'AsalaeConnector')
                  & match_kwargs('eid'))
    columns = ['connector', 'status', 'action']
    column_renderers = {
        'connector': tableview.MainEntityColRenderer(),
        'status': StatusColRenderer(),
        'action': SyncActionColRenderer(),
    }


# As@lae synchronization

class AsalaeMirroredComponent(AbstractMirroredComponent):
    __select__ = (AbstractMirroredComponent.__select__
                  & etype_exists('AsalaeConnector')
                  & is_instance('Agent'))
    connector_etypes = ('AsalaeConnector',)


class DeleteAsalaeOrgMixin(object):
    """Mixin for deletion of As@lae organization corresponding to an Agent."""
    __regid__ = 'saem_ref.asalae.delete_organization'
    __select__ = (etype_exists('AsalaeConnector') & is_instance('Agent') &
                  score_entity(entity_has_mirror) & one_line_rset())


class DeleteAsalaeOrgAction(DeleteAsalaeOrgMixin, action.Action):
    """Action to trigger deletion of the organization in As@lae instance
    corresponding to an Agent.
    """
    title = _('delete As@lae organization')

    def url(self):
        entity = self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
        return entity.absolute_url(vid=self.__regid__)


class DeleteAsalaeOrgView(DeleteAsalaeOrgMixin, EntityView):
    """Handle deletion of an organization in As@lae instance for an Agent."""

    def entity_call(self, entity):
        rset = self._cw.execute('Any X WHERE X is AsalaeConnector')
        assert len(rset) == 1, 'using multiple Asalae connectors is not supported'
        try:
            self._cw.call_service('saem_ref.asalae.delete-agent',
                                  connector_eid=rset[0][0], eid=entity.eid)
        except Exception:
            msg_details = self._cw._('see instance logs for details')
            self.exception('deletion of Asalae organization for entity #%d failed' % entity.eid)
            msg = self._cw._('deletion of As@lae organization failed (%s)') % msg_details
        else:
            msg = self._cw._('deletion of As@lae organization successfully completed')
        raise Redirect(entity.absolute_url(__message=msg))


# Alfresco synchronization

class AlfrescoMirroredComponent(AbstractMirroredComponent):
    __select__ = (AbstractMirroredComponent.__select__
                  & etype_exists('AlfrescoConnector')
                  & is_instance('ConceptScheme'))
    connector_etypes = ('AlfrescoConnector',)


class AsalaeAlfrescoMirroredComponent(AbstractMirroredComponent):
    __select__ = (AbstractMirroredComponent.__select__
                  & (etype_exists('AlfrescoConnector') | etype_exists('AsalaeConnector'))
                  & is_instance('SEDAProfile'))
    connector_etypes = ('AlfrescoConnector', 'AsalaeConnector')


class ManageAlfrescoConnectorsAction(actions.ManagersAction):
    __regid__ = 'alfrescoconnector'
    title = _('Alfresco connectors')
    category = 'manage'
    order = 1


class ManageAsalaeConnectorsAction(actions.ManagersAction):
    __regid__ = 'asalaeconnector'
    title = _('Asalae connectors')
    category = 'manage'
    order = 1
