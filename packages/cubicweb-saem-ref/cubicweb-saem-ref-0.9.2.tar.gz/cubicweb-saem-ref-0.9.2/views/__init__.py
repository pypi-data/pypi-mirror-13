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
"""cubicweb-saem-ref views/forms/actions/components for web ui"""

import calendar
from datetime import datetime
from functools import wraps

from dateutil.parser import parse as parse_date

from logilab.common.date import ustrftime
from logilab.common.decorators import monkeypatch
from logilab.mtconverter import xml_escape

from cubicweb import tags
from cubicweb.uilib import js, domid
from cubicweb.utils import JSString, json_dumps, UStringIO
from cubicweb.view import View, EntityView, AnyRsetView
from cubicweb.predicates import (match_http_method, match_user_groups, has_permission,
                                 is_instance, any_rset, multi_lines_rset, match_kwargs)
from cubicweb.web import ProcessFormError, formwidgets as fw, component
from cubicweb.web.views import (basecomponents, uicfg, tableview, actions, urlrewrite, tabs,
                                primary, json, debug)

from cubes.squareui.views.basetemplates import basetemplates

from cubes.saem_ref import cwuri_url


_ = unicode


def view_link(req, *args, **kwargs):
    """Return an HTML link with a "view" icon."""
    return tags.a(u'', href=req.build_url(*args, **kwargs),
                  klass='icon-eye pull-right',
                  title=req._('View'))


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


def dropdown_button(req, text, *links):
    """Return an HTML button with `text` and dropdown content from `links`.
    """
    data = UStringIO()
    w = data.write
    w(u'<div class="btn-group pull-right clearfix">')
    w(tags.button(text, klass='btn btn-success'))
    w(tags.button(
        tags.span(klass='caret'),
        escapecontent=False,
        klass='btn btn-success dropdown-toggle',
        **{'data-toggle': 'dropdown', 'aria-expanded': 'false'}))
    w(u'<ul class="dropdown-menu" role="menu">')
    for link in links:
        w(u'<li>{0}</li>'.format(link))
    w(u'</ul>')
    w(u'</div>')
    return data.getvalue()


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
                editurlparams['tabid'] = kwargs.pop('tabid')
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


# Startup
for etype in ('AgentKind', 'ArchivalRole', 'AgentPlace',
              'AssociationRelation', 'ChronologicalRelation', 'HierarchicalRelation',
              'EACResourceRelation', 'Activity', 'SEDADate'):
    uicfg.indexview_etype_section[etype] = 'subobject'


for etype in ('Agent', 'ConceptScheme', 'SEDAProfile'):
    uicfg.autoform_section.tag_subject_of(
        (etype, 'custom_workflow', '*'), 'main', 'hidden')


class RsetTableView(tableview.RsetTableView):
    """Table view accepting ``column_renderers`` as call parameter"""
    # Drop bw compat selector part as it.does not permit the use of `headers`
    # parameter.
    __select__ = AnyRsetView.__select__

    def call(self, *args, **kwargs):
        self.column_renderers = self.column_renderers.copy()
        colrenderers = kwargs.pop('column_renderers', {})
        self.column_renderers.update(colrenderers)
        super(RsetTableView, self).call(*args, **kwargs)


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


class EditableRsetTableColRenderer(tableview.RsetTableColRenderer):
    """Column render with an `edit` link"""

    def __init__(self, editurlparams):
        cellvid = 'saem_ref.edit-link'
        super(EditableRsetTableColRenderer, self).__init__(cellvid)
        self.editurlparams = editurlparams

    def render_header(self, w):
        pass

    def render_cell(self, w, rownum):
        self._cw.view(self.cellvid, self.cw_rset, 'empty-cell',
                      row=rownum, col=self.colid, w=w, editurlparams=self.editurlparams)


# Form Widget
class JQueryIncompleteDatePicker(fw.JQueryDatePicker):
    """ custom datefield enabling the user to enter only the year or the month and year
    of the date.
    If the given string is a valid date, return the date
    If only the year or the year and the month is given, return a date completed with default
    day and/or month value :
    if the field is end_date, default day/month is 31/12 and default day is the last day
    of the given month
    if the field is start_date, default day/month is 01/01 and default day is 1
    """
    def __init__(self, *args, **kwargs):
        self.default_end = kwargs.pop("default_end", False)
        self.update_min = kwargs.pop("update_min", None)
        self.update_max = kwargs.pop("update_max", None)
        super(JQueryIncompleteDatePicker, self).__init__(*args, **kwargs)

    def process_field_data(self, form, field):
        datestr = form._cw.form.get(field.input_name(form))
        try:
            return process_incomplete_date(datestr, self.default_end)
        except ValueError as exc:
            if "day is out of range for month" in exc:
                raise ProcessFormError(form._cw._("day is out of range for month"))
            elif "month must be in 1..12" in exc:
                raise ProcessFormError(form._cw._("month must be in 1..12"))
            else:
                raise ProcessFormError(form._cw._("can not process %s: expected format "
                                                  "dd/mm/yyyy, mm/yyyy or yyyy" % datestr))

    def attributes(self, form, field):
        attrs = super(JQueryIncompleteDatePicker, self).attributes(form, field)
        form._cw.add_js('cubes.saem_ref.js')
        if self.update_max:
            domid = '%s-subject:%s' % (self.update_max, form.edited_entity.eid)
            attrs['onChange'] = js.saem.update_datepicker_minmax(domid, 'maxDate',
                                                                 JSString('this.value'))
        if self.update_min:
            domid = '%s-subject:%s' % (self.update_min, form.edited_entity.eid)
            attrs['onChange'] = js.saem.update_datepicker_minmax(domid, 'minDate',
                                                                 JSString('this.value'))
        return attrs

    def _render(self, form, field, renderer):
        req = form._cw
        if req.lang != 'en':
            req.add_js('jquery.ui.datepicker-%s.js' % req.lang)
        domid = field.dom_id(form, self.suffix)
        # XXX find a way to understand every format
        fmt = req.property_value('ui.date-format')
        picker_fmt = fmt.replace('%Y', 'yy').replace('%m', 'mm').replace('%d', 'dd')
        max_date = min_date = None
        if self.update_min:
            current = getattr(form.edited_entity, self.update_min)
            if current is not None:
                max_date = ustrftime(current, fmt)
        if self.update_max:
            current = getattr(form.edited_entity, self.update_max)
            if current is not None:
                min_date = ustrftime(current, fmt)
        req.add_onload(u'cw.jqNode("%s").datepicker('
                       '{buttonImage: "%s", dateFormat: "%s", firstDay: 1,'
                       ' showOn: "button", buttonImageOnly: true, minDate: %s, maxDate: %s});'
                       % (domid, req.uiprops['CALENDAR_ICON'], picker_fmt, json_dumps(min_date),
                          json_dumps(max_date)))
        return self._render_input(form, field)


def process_incomplete_date(datestr, end=False):
    """ parse a date from a string
    If the given string is a valid date, return the date
    If only the year or the year and the month is given, return a date completed with default
    day and/or month value :
    if end is True, default day/month is 31/12 and default day is the last day of the given month
    if end is False, default day/month is 01/01 and default day is 1
    """
    if not datestr:
        return None
    if end:
        if len(datestr.split("/")) == 2:  # = day is not defined
            pdate = parse_date(datestr, default=datetime(9999, 12, 1), dayfirst=True)
            last_day = calendar.monthrange(pdate.year, pdate.month)[1]
            pdate = pdate.replace(day=last_day)
        else:
            pdate = parse_date(datestr, default=datetime(9999, 12, 31), dayfirst=True)
    else:
        pdate = parse_date(datestr, default=datetime(9999, 1, 1), dayfirst=True)
    if pdate.year == 9999:
        raise ValueError()
    return pdate.date()


def navigation_menu():
    """Yield navigation component instance to fill the navigation menu"""
    def header_component(path, label, order):
        def render(self, w, label=label, path=path, **kwargs):
            self._cw.add_css('cubes.saem_ref.css')
            w(tags.a(self._cw._(label), href=self._cw.build_url(path)))
        return type(path + 'NavMenuEntryComponent', (basecomponents.HeaderComponent,), {
            '__regid__': 'saem_ref.navmenu_' + path.lower(),
            '__select__': any_rset(),
            'context': 'header-left',
            'order': order,
            'render': render,
        })

    for order, etype in enumerate(('Agent', 'ConceptScheme', 'SEDAProfile'), 101):
        yield header_component(etype, etype + '_plural', order)
    yield header_component('sedalib', _('SEDA components library'), order + 1)


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
    """Overriden from cubicweb to handle case where ark is directly used in cwuri, and so absolute url
    should be generated from it.
    """
    def entity_call(self, entity, rtype, **kwargs):
        if rtype == 'cwuri':
            url = xml_escape(cwuri_url(entity))
        else:
            url = entity.printable_value(rtype)
        if url:
            self.w(u'<a href="%s">%s</a>' % (url, url))


class AssignArkWebService(json.JsonMixIn, View):
    """JSON view to assign a new Ark for external usage."""

    __regid__ = 'saem_ref.ws.ark'
    __select__ = match_user_groups('users', 'managers') & match_http_method('POST')

    # XXX could check Accept=application/json
    def call(self):
        self.wdata([{'ark': self._cw.call_service('saem_ref.attribute-ark')}])


class AssignArkWebServiceNonPOST(AssignArkWebService):
    """JSON view to assign a new Ark for external usage."""
    __select__ = match_user_groups('users', 'managers')

    def call(self):
        self.wdata([{'error': 'This service is only accessible using POST.'}])


class AssignArkWebServiceNonAuthenticated(AssignArkWebService):
    """JSON view to assign a new Ark for external usage."""
    __select__ = ~match_user_groups('users', 'managers')

    def call(self):
        self.wdata([{'error': 'This service requires authentication.'}])


actions.SiteConfigurationAction.order = 100
debug.SiteInfoAction.order = 101


def registration_callback(vreg):
    from cubicweb.web.views import undohistory
    vreg.register_all(globals().values(), __name__, (RsetTableView, URLAttributeView))
    vreg.register_and_replace(RsetTableView, tableview.RsetTableView)
    vreg.register_and_replace(URLAttributeView, primary.URLAttributeView)
    vreg.unregister(tableview.TableView)
    vreg.unregister(undohistory.UndoHistoryView)
    vreg.unregister(basecomponents.ApplicationName)
    for menu_entry in navigation_menu():
        vreg.register(menu_entry)
    # disable 'add a etype' action replaced by appropriate ctx components for
    # scheme and agent, and providing poor user experience anyway (hidden
    # in the actions box)
    vreg.unregister(actions.AddNewAction)
