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
"""cubicweb-saem-ref views/forms/actions/components for web ui"""

from functools import wraps

from logilab.common.decorators import monkeypatch
from logilab.mtconverter import xml_escape

from cubicweb import tags
from cubicweb.uilib import js, domid
from cubicweb.utils import JSString
from cubicweb.view import EntityView
from cubicweb.predicates import has_permission, is_instance, multi_lines_rset, match_kwargs
from cubicweb.web import component
from cubicweb.web.views import uicfg, actions, urlrewrite, tabs, primary, debug

from cubes.squareui.views.basetemplates import basetemplates

from cubes.saem_ref import cwuri_url


_ = unicode


def external_link(text, href):
    """Return an HTML link with an icon indicating that the URL is external.
    """
    icon = tags.span(klass="glyphicon glyphicon-share-alt")
    return tags.a(u' '.join([text, icon]), href=href, escapecontent=False)


def add_etype_link(req, etype, text=u'', klass='icon-plus-circled pull-right',
                   **urlparams):
    """Return an HTML link to add an entity of type 'etype'."""
    vreg = req.vreg
    eschema = vreg.schema.eschema(etype)
    if eschema.has_perm(req, 'add'):
        url = vreg['etypes'].etype_class(etype).cw_create_url(req, **urlparams)
        return tags.a(text, href=url, klass=klass,
                      title=req.__('New %s' % etype))
    return u''


def import_etype_link(req, etype, url):
    """Return an HTML link to the view that may be used to import an entity of type `etype`.
    """
    eschema = req.vreg.schema.eschema(etype)
    if eschema.has_perm(req, 'add'):
        return tags.a(u'', href=url, klass='icon-upload pull-right',
                      title=req.__('Import %s' % etype))
    return u''


def index_dropdown_button(text, links):
    """Return an HTML button with `text` and dropdown content from `links`, for use in an index box
    title.
    """
    links = [l for l in links if l]  # there may be empty links for not allowed actions
    if not links:
        return u''  # no need for the dropdown
    data = []
    w = data.append
    w(u'<div class="btn-group pull-right clearfix">')
    w(tags.a('', href='', klass='icon-plus-circled pull-right dropdown-toggle',
             title=text, **{'data-toggle': 'dropdown', 'aria-expanded': 'false'}))
    w(u'<ul class="dropdown-menu" role="menu">')
    for link in links:
        w(u'<li>{0}</li>'.format(link))
    w(u'</ul>')
    w(u'</div>')
    return u''.join(data)


def editlinks(icon_info):
    """Decorator for `entity_call` to add "edit" links."""
    def decorator(entity_call):
        @wraps(entity_call)
        def wrapper(self, entity, **kwargs):
            editurlparams = {
                '__redirectpath': kwargs.pop('__redirectpath',
                                             entity.rest_path()),
            }
            if 'tabid' in kwargs:
                editurlparams['__redirectparams'] = 'tab=' + kwargs.pop('tabid')
            html_icons = entity.view('saem_ref.edit-link',
                                     icon_info=icon_info,
                                     editurlparams=editurlparams)
            if html_icons:
                self.w(tags.div(html_icons, klass='pull-right'))
            return entity_call(self, entity, **kwargs)
        return wrapper
    return decorator


class ExternalLinkView(EntityView):
    """Render an entity as an external link according to `rtype` keyword
    argument or automatically if it is an ExternalUri.
    """

    __regid__ = 'saem.external_link'
    __select__ = EntityView.__select__ & (
        is_instance('ExternalUri') | match_kwargs('rtype'))

    def entity_call(self, entity, rtype=None):
        if rtype is None:
            rtype = 'uri'  # ExternalUri
        href = text = getattr(entity, rtype)
        self.w(external_link(text, href))


def configure_relation_widget(req, div, search_url, title, multiple, validate):
    """Build a javascript link to invoke a relation widget

    Widget will be linked to div `div`, with a title `title`. It will display selectable entities
    matching url `search_url`. bool `multiple` indicates whether several entities can be selected or
    just one, `validate` identifies the javascript callback that must be used to validate the
    selection.
    """
    req.add_js(('jquery.ui.js',
                'cubicweb.ajax.js',
                'cubicweb.widgets.js',
                'cubicweb.facets.js',
                'cubes.relationwidget.js',
                'cubes.saem_ref.js'))
    return 'javascript: %s' % js.saem.relateWidget(div, search_url, title, multiple,
                                                   JSString(validate))


class AddEntityComponent(component.CtxComponent):
    """Component with 'add' link to be displayed in 'same etype' views usually 'SameETypeListView'.
    """
    __regid__ = 'saem_ref.add_entity'
    __select__ = (component.CtxComponent.__select__ & multi_lines_rset() & has_permission('add') &
                  is_instance('Agent', 'ConceptScheme', 'SEDAProfile'))
    context = 'navtop'

    def render_body(self, w):
        etype = self.cw_rset.description[0][0]
        w(add_etype_link(self._cw, etype))


class ImportEntityComponent(component.CtxComponent):
    """Component with 'import' link to be displayed in 'same etype' views usually
    'SameETypeListView'.

    Concret class should fill the `import_vid` class attribute and add a proper `is_instance`
    selector.
    """
    __abstract__ = True
    __regid__ = 'saem_ref.import_entity'
    __select__ = component.CtxComponent.__select__ & multi_lines_rset() & has_permission('add')
    import_url = None  # URL of the view that may be used to import data
    context = 'navtop'

    def render_body(self, w):
        etype = self.cw_rset.description[0][0]
        w(import_etype_link(self._cw, etype, self.import_url))


# Bootstrap configuration.
basetemplates.TheMainTemplate.twbs_container_cls = 'container'
basetemplates.HTMLPageHeader.css = {
    'navbar-extra': 'navbar-default',
    'breadcrumbs': 'cw-breadcrumb',
    'container-cls': basetemplates.TheMainTemplate.twbs_container_cls,
    'header-left': '',
    'header-right': 'navbar-right',
}


# Wrap breadcrumbs items within a "container" div.
@monkeypatch(basetemplates.HTMLPageHeader)
def breadcrumbs(self, view):
    components = self.get_components(view, context='header-center')
    if components:
        self.w(u'<nav role="navigation" class="%s">' %
               self.css.get('breadcrumbs', 'breadcrumbs-defaul'))
        for comp in components:
            self.w(u'<div class="container">')
            comp.render(w=self.w)
            self.w(u'</div>')
        self.w(u'</nav>')


for etype in ('Agent', 'ConceptScheme', 'SEDAProfile'):
    uicfg.autoform_section.tag_subject_of(
        (etype, 'custom_workflow', '*'), 'main', 'hidden')


class EditLinkView(EntityView):
    """Render entity as a link to the edition view"""
    __regid__ = 'saem_ref.edit-link'

    def entity_call(self, entity, icon_info=True, editurlparams=None):
        editurlparams = editurlparams or {}
        links = []
        if icon_info:
            links.append(('icon-info', self._cw._('view'), entity.absolute_url()))
        if entity.cw_has_perm('update'):
            links.append(('icon-pencil', self._cw._('edit'),
                          entity.absolute_url(vid='edition', **editurlparams)))
        if entity.cw_has_perm('delete'):
            links.append(('icon-trash', self._cw._('delete'),
                          entity.absolute_url(vid='deleteconf', **editurlparams)))
        for csscls, label, href in links:
            self.w(u'<span title="{label}">{link}</span>'.format(
                label=label, link=tags.a(klass=csscls, href=href)))


urlrewrite.SchemaBasedRewriter.rules.append(
    (urlrewrite.rgx('/ark:/(.+)'),
     urlrewrite.build_rset(rql=r'Any X WHERE X ark %(text)s', rgxgroups=[('text', 1)]))
)


class SAEMRefRewriter(urlrewrite.SimpleReqRewriter):
    """URL rewriter for SAEM-Ref"""
    rules = [
        ('/oai', dict(vid='oai')),
        ('/ark', dict(vid='saem_ref.ws.ark')),
        ('/sedalib', dict(rql='Any X WHERE X is in (ProfileArchiveObject, ProfileDocument), '
                              'NOT X seda_parent P',
                          vid='saem_ref.sedalib')),
    ]


@monkeypatch(tabs.TabsMixin)
def active_tab(self, default):
    return self._cw.form.get('tab', domid(default))


class URLAttributeView(primary.URLAttributeView):
    """Overriden from cubicweb to handle case where ark is directly used in cwuri, and so absolute
    url should be generated from it.
    """
    def entity_call(self, entity, rtype, **kwargs):
        if rtype == 'cwuri':
            url = xml_escape(cwuri_url(entity))
        else:
            url = entity.printable_value(rtype)
        if url:
            self.w(u'<a href="%s">%s</a>' % (url, url))


actions.SiteConfigurationAction.order = 100
debug.SiteInfoAction.order = 101


def registration_callback(vreg):
    from cubicweb.web.views import tableview, basecomponents, undohistory
    vreg.register_all(globals().values(), __name__, (URLAttributeView,))
    vreg.register_and_replace(URLAttributeView, primary.URLAttributeView)
    vreg.unregister(tableview.TableView)
    vreg.unregister(undohistory.UndoHistoryView)
    vreg.unregister(basecomponents.ApplicationName)
    # disable 'add a etype' action replaced by appropriate ctx components for
    # scheme and agent, and providing poor user experience anyway (hidden
    # in the actions box)
    vreg.unregister(actions.AddNewAction)
