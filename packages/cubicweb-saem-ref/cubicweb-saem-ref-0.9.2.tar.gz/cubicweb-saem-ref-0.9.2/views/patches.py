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
"""cubicweb-saem-ref monkeypatch of not-yet-integrated patches"""

from logilab.common.decorators import monkeypatch

# https://www.cubicweb.org/ticket/5334750 ##########################################################

from cubicweb.web.views import reledit


@monkeypatch(reledit.AutoClickAndEditFormView)
def _may_delete_related(self, related_rset, rschema, role):
    # we assume may_edit_related, only 1 related entity
    if not related_rset:
        return False
    rentity = related_rset.get_entity(0, 0)
    entity = self.entity
    if role == 'subject':
        kwargs = {'fromeid': entity.eid, 'toeid': rentity.eid}
        cardinality = rschema.rdefs[(entity.cw_etype, rentity.cw_etype)].cardinality[0]
    else:
        kwargs = {'fromeid': rentity.eid, 'toeid': entity.eid}
        cardinality = rschema.rdefs[(rentity.cw_etype, entity.cw_etype)].cardinality[1]
    if cardinality in '1+':
        return False
    # NOTE: should be sufficient given a well built schema/security
    return rschema.has_perm(self._cw, 'delete', **kwargs)


# https://www.cubicweb.org/ticket/5352619 ##########################################################
# other part in site_cubicweb.py

from cubicweb import neg_role  # noqa
from cubicweb.web import ProcessFormError  # noqa
from cubicweb.web.views import editcontroller  # noqa

orig_insert_entity = editcontroller.EditController._insert_entity


@monkeypatch(editcontroller.EditController)
def _insert_entity(self, etype, eid, rqlquery):
    if getattr(rqlquery, 'canceled', False):
        return
    return orig_insert_entity(self, etype, eid, rqlquery)


orig_update_entity = editcontroller.EditController._update_entity


@monkeypatch(editcontroller.EditController)
def _update_entity(self, eid, rqlquery):
    if getattr(rqlquery, 'canceled', False):
        return
    return orig_update_entity(self, eid, rqlquery)


@monkeypatch(editcontroller.EditController)
def handle_formfield(self, form, field, rqlquery=None):
    eschema = form.edited_entity.e_schema
    try:
        for field, value in field.process_posted(form):
            if not ((field.role == 'subject' and field.name in eschema.subjrels) or
                    (field.role == 'object' and field.name in eschema.objrels)):
                continue
            rschema = self._cw.vreg.schema.rschema(field.name)
            if rschema.final:
                rqlquery.set_attribute(field.name, value)
            else:
                if form.edited_entity.has_eid():
                    origvalues = set(e.eid for e in form.edited_entity.related(field.name,
                                                                               field.role,
                                                                               entities=True))
                else:
                    origvalues = set()
                if value is None or value == origvalues:
                    continue  # not edited / not modified / to do later
                rdef = eschema.rdef(rschema, field.role)
                if not value and rdef.composite == neg_role(field.role):
                    # deleted composite relation, delete the subject entity
                    self.handle_composite_deletion(form, field, rqlquery)
                if rschema.inlined and rqlquery is not None and field.role == 'subject':
                    self.handle_inlined_relation(form, field, value, origvalues, rqlquery)
                elif form.edited_entity.has_eid():
                    self.handle_relation(form, field, value, origvalues)
                else:
                    form._cw.data['pending_others'].add((form, field))
    except ProcessFormError as exc:
        self.errors.append((field, exc))


@monkeypatch(editcontroller.EditController)
def handle_composite_deletion(self, form, field, rqlquery):
    """handle deletion of the entity when relation to its parent is removed
    """
    rql = 'DELETE %s X WHERE X eid %%(x)s' % form.edited_entity.cw_etype
    self.relations_rql.append((rql, {'x': form.edited_entity.eid}))
    rqlquery.canceled = True


# monkey-patch for https://www.cubicweb.org/ticket/5457548 ########################################

from cubicweb.web import formwidgets  # noqa

orig_button_render = formwidgets.Button.render


@monkeypatch(formwidgets.Button)
def render(self, form, field=None, renderer=None):
    self.attrs['class'] = self.css_class
    return orig_button_render(self, form, field, renderer)


# monkey-patch for https://www.cubicweb.org/ticket/5705835 #########################################

from cubicweb.web import views  # noqa
from cubicweb.web.views import urlpublishing  # noqa


@monkeypatch(views)
def vid_from_rset(req, rset, schema, check_table=True):
    """given a result set, return a view id"""
    if rset is None:
        return 'index'
    for mimetype in req.parse_accept_header('Accept'):
        if mimetype in views.VID_BY_MIMETYPE:
            return views.VID_BY_MIMETYPE[mimetype]
    nb_rows = len(rset)
    # empty resultset
    if nb_rows == 0:
        return 'noresult'
    # entity result set
    if not schema.eschema(rset.description[0][0]).final:
        if check_table and views.need_table_view(rset, schema):
            return 'table'
        if nb_rows == 1:
            if req.search_state[0] == 'normal':
                return 'primary'
            return 'outofcontext-search'
        if len(rset.column_types(0)) == 1:
            return 'sameetypelist'
        return 'list'
    return 'table'


@monkeypatch(urlpublishing.RestPathEvaluator)
def set_vid_for_rset(self, req, cls, rset):
    if rset.rowcount == 0:
        raise urlpublishing.NotFound()
    if 'vid' not in req.form:
        req.form['vid'] = views.vid_from_rset(req, rset, req.vreg.schema,
                                              check_table=False)


# https://www.cubicweb.org/ticket/6211101 ##########################################################

from cubicweb.server.sources import native  # noqa
from cubicweb.hooks import syncschema  # noqa


@monkeypatch(syncschema.AfterDelRelationTypeHook)
def __call__(self):
    cnx = self._cw
    try:
        rdef = cnx.vreg.schema.schema_by_eid(self.eidfrom)
    except KeyError:
        self.critical('cant get schema rdef associated to %s', self.eidfrom)
        return
    subjschema, rschema, objschema = rdef.as_triple()
    pendingrdefs = cnx.transaction_data.setdefault('pendingrdefs', set())
    # first delete existing relation if necessary
    if rschema.final:
        pendingrdefs.add((subjschema, rschema))
    else:
        pendingrdefs.add((subjschema, rschema, objschema))
        if not (cnx.deleted_in_transaction(subjschema.eid) or
                cnx.deleted_in_transaction(objschema.eid)):
            if rdef.rtype.inlined:
                # if rtype is inlined, we may have to remove NOT NULL constraint from the
                # database before attempting to clean data
                dbhelper = cnx.repo.system_source.dbhelper
                table, column = native.rdef_table_column(rdef)
                coltype, allownull = native.rdef_physical_info(dbhelper, rdef)
                if not allownull:
                    dbhelper.set_null_allowed(cnx.cnxset.cu,
                                              table, column, coltype, True)
            cnx.execute('DELETE X %s Y WHERE X is %s, Y is %s'
                        % (rschema, subjschema, objschema))
    syncschema.RDefDelOp(cnx, rdef=rdef)


# https://www.cubicweb.org/ticket/6510921 ##########################################################

from logilab.common.registry import NoSelectableObject  # noqa
from cubicweb.web.views.autoform import AutomaticEntityForm  # noqa


@monkeypatch(AutomaticEntityForm)
def inline_creation_form_view(self, rschema, ttype, role):
    """yield inline form views to a newly related (hence created) entity
    through the given relation
    """
    try:
        yield self._cw.vreg['views'].select('inline-creation', self._cw,
                                            etype=ttype, rtype=rschema, role=role,
                                            peid=self.edited_entity.eid,
                                            petype=self.edited_entity.e_schema,
                                            pform=self)
    except NoSelectableObject:
        # may be raised if user doesn't have the permission to add ttype entities (no checked
        # earlier) or if there is some custom selector on the view
        pass


# https://www.cubicweb.org/ticket/6711900 ##########################################################

@monkeypatch(AutomaticEntityForm)
def check_inlined_rdef_permissions(self, rschema, role, tschema, ttype):
    """return true if permissions are granted on the inlined object and
    relation"""
    if not tschema.has_perm(self._cw, 'add'):
        return False
    entity = self.edited_entity
    rdef = entity.e_schema.rdef(rschema, role, ttype)
    if entity.has_eid():
        if role == 'subject':
            rdefkwargs = {'fromeid': entity.eid}
        else:
            rdefkwargs = {'toeid': entity.eid}
        return rdef.has_perm(self._cw, 'add', **rdefkwargs)
    return rdef.may_have_permission('add', self._cw)
