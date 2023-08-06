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
"""cubicweb-saem-ref site customizations"""

from os.path import abspath, join, dirname
from warnings import warn
import sys

from logilab.common.decorators import monkeypatch, classproperty

from yams import ValidationError
from yams.constraints import OPERATORS, BoundaryConstraint, Attribute, actual_value

from cubicweb import cwvreg
from cubicweb.devtools.testlib import CubicWebTC

from cubes.skos import rdfio

from cubes.saem_ref import cwuri_url
# this import is needed to take account of pg_trgm monkeypatches
# while executing cubicweb-ctl commands (db-rebuild-fti)
from cubes.saem_ref import pg_trgm  # noqa


@monkeypatch(rdfio.RDFGraphGenerator, methodname='same_as_uris')
@staticmethod
def same_as_uris(entity):
    yield cwuri_url(entity)


# Ensure ValidationError get translated, see
# https://www.logilab.org/ticket/1234481 (Yams 0.42.0 hopefully)
@monkeypatch(ValidationError)
def translate(self, _):
    """Translate and interpolate messsages in the errors dictionary, using
    the given translation function.

    If no substitution has been given, suppose msg is already translated for
    bw compat, so no translation occurs.

    This method may only be called once.
    """
    assert not self._translated
    self._translated = True
    if self.msgargs is not None:
        if self.i18nvalues:
            for key in self.i18nvalues:
                self.msgargs[key] = _(self.msgargs[key])
        for key, msg in self.errors.items():
            msg = _(msg)
            if key is not None:
                msg = msg.replace('%(KEY-', '%(' + key + '-')
            self.errors[key] = msg % self.msgargs
    else:
        for key, msg in self.errors.items():
            self.errors[key] = _(msg)


@monkeypatch(CubicWebTC, methodname='config')
@classproperty
def config(cls):
    """return the configuration object

    Configuration is cached on the test class.
    """
    if cls is CubicWebTC:
        warn("Don't use CubicWebTC directly to prevent database caching issue",
             RuntimeWarning)
        return None
    try:
        return cls.__dict__['_config']
    except KeyError:
        home = abspath(join(dirname(sys.modules[cls.__module__].__file__), cls.appid))
        config = cls._config = cls.configcls(cls.appid, apphome=home)
        config.mode = 'test'
        return config


@monkeypatch(BoundaryConstraint)
def check(self, entity, rtype, value):
    """return true if the value satisfy the constraint, else false"""
    boundary = actual_value(self.boundary, entity)
    if boundary is None:
        return True
    return OPERATORS[self.operator](value, boundary)


# support for custom message on boundary constraint, awaiting for #288874 to be integrated

@monkeypatch(BoundaryConstraint)
def __init__(self, op, boundary=None, msg=None):
    assert op in OPERATORS, op
    self.msg = msg
    self.operator = op
    self.boundary = boundary


@monkeypatch(BoundaryConstraint)
def failed_message(self, key, value):
    if self.msg:
        return self.msg, {}
    boundary = self.boundary
    if isinstance(boundary, Attribute):
        boundary = boundary.attr
    return "value %(KEY-value)s must be %(KEY-op)s %(KEY-boundary)s", {
        key + '-value': value,
        key + '-op': self.operator,
        key + '-boundary': boundary}


@monkeypatch(BoundaryConstraint)
def serialize(self):
    """simple text serialization"""
    value = u'%s %s' % (self.operator, self.boundary)
    if self.msg:
        value += '\n' + self.msg
    return value


@monkeypatch(BoundaryConstraint, methodname='deserialize')
@classmethod
def deserialize(cls, value):
    """simple text deserialization"""
    try:
        value, msg = value.split('\n', 1)
    except ValueError:
        msg = None
    op, boundary = value.split(' ', 1)
    return cls(op, eval(boundary), msg or None)


# deactivate date-format and datetime-format cw properties. This is because we do some advanced date
# manipulation such as allowing partial date and this is not generic enough to allow arbitrary
# setting of date and time formats

base_user_property_keys = cwvreg.CWRegistryStore.user_property_keys


@monkeypatch(cwvreg.CWRegistryStore)
def user_property_keys(self, withsitewide=False):
    props = base_user_property_keys(self, withsitewide)
    return [prop for prop in props if prop not in ('ui.date-format', 'ui.datetime-format')]


# https://www.cubicweb.org/ticket/4848923 ######################################
# other part in schema and hooks
import pytz  # noqa
from logilab.common.date import ustrftime  # noqa
from cubicweb.cwconfig import register_persistent_options  # noqa
from cubicweb.uilib import PRINTERS  # noqa

_ = unicode

register_persistent_options((
    ('timezone',
     {'type': 'choice',
      'choices': pytz.common_timezones,
      'default': 'Europe/Paris',
      'help': _('timezone in which time should be displayed'),
      'group': 'ui', 'sitewide': True,
      }),
))


def print_tzdatetime_local(value, req, *args, **kwargs):
    tz = pytz.timezone(req.property_value('ui.timezone'))
    value = value.replace(tzinfo=pytz.utc).astimezone(tz)
    return ustrftime(value, req.property_value('ui.datetime-format'))

PRINTERS['TZDatetime'] = print_tzdatetime_local


# monkey-patch for https://www.cubicweb.org/ticket/5352619 #########################################
# other part in views/patches.py

from cubicweb import neg_role  # noqa
from cubicweb.web import formfields  # noqa

orig_guess_field = formfields.guess_field


@monkeypatch(formfields)
def guess_field(eschema, rschema, role='subject', req=None, **kwargs):
    rdef = eschema.rdef(rschema, role)
    card = rdef.role_cardinality(role)
    composite = getattr(rdef, 'composite', None)
    # don't mark composite relation as required, we want the composite element to be removed when
    # not linked to its parent
    kwargs.setdefault('required', card in '1+' and composite != neg_role(role))
    return orig_guess_field(eschema, rschema, role, req, **kwargs)


# monkey-patch for https://www.cubicweb.org/ticket/4985752 #########################################
# other part in schema.py

from logilab.common.decorators import cached  # noqa
from cubicweb import entity  # noqa


@monkeypatch(entity.Entity, methodname='cw_rest_attr_info')
@classmethod
@cached
def cw_rest_attr_info(cls):
    """this class method return an attribute name to be used in URL for
    entities of this type and a boolean flag telling if its value should be
    checked for uniqness.

    The attribute returned is, in order of priority:

    * class's `rest_attr` class attribute
    * an attribute defined as unique in the class'schema
    * 'eid'
    """
    mainattr, needcheck = 'eid', True
    if cls.rest_attr:
        mainattr = cls.rest_attr
        needcheck = not cls.e_schema.has_unique_values(mainattr)
    else:
        for rschema in cls.e_schema.subject_relations():
            if (rschema.final
                    and rschema not in ('eid', 'cwuri')
                    and cls.e_schema.has_unique_values(rschema)
                    and cls.e_schema.rdef(rschema.type).cardinality[0] == '1'):
                mainattr = str(rschema)
                needcheck = False
                break
    if mainattr == 'eid':
        needcheck = False
    return mainattr, needcheck


# Monkeypatch for http://hg.logilab.org/review/cubicweb/rev/68bb6d35f0e8 (no ticket) ###############
# commit message: [hook] remove assumption invalidated by cubicweb 3.21

from cubicweb.hooks import security  # noqa


@monkeypatch(security)
def skip_inlined_relation_security(cnx, rschema, eid):
    """return True if security for the given inlined relation should be skipped,
    in case where the relation has been set through modification of
    `entity.cw_edited` in a hook
    """
    assert rschema.inlined
    try:
        entity = cnx.transaction_data['ecache'][eid]
    except KeyError:
        return False
    edited = getattr(entity, 'cw_edited', None)
    if edited is None:
        return False
    return rschema.type in edited.skip_security


# monkey-patch for https://www.cubicweb.org/ticket/6206636 #########################################

from cubicweb.server.sources import native  # noqa


@monkeypatch(native.NativeSQLSource)
def index_entity(self, cnx, entity):
    """create an operation to [re]index textual content of the given entity
    on commit
    """
    if self.do_fti:
        native.FTIndexEntityOp.get_instance(cnx).add_data(entity.eid)

# monkey-patch for https://www.cubicweb.org/ticket/6978316 #########################################

from datetime import time, datetime  # noqa
from logilab.common.date import utctime, utcdatetime  # noqa
from cubicweb import Binary  # noqa
from cubicweb.server import sqlutils  # noqa
from cubicweb.server.sources import rql2sql  # noqa


@monkeypatch(sqlutils.SQLAdapterMixIn)
def merge_args(self, args, query_args):
    if args is not None:
        newargs = {}
        for key, val in args.iteritems():
            # convert cubicweb binary into db binary
            if isinstance(val, Binary):
                val = self._binary(val.getvalue())
            # convert timestamp to utc.
            # expect SET TiME ZONE to UTC at connection opening time.
            # This shouldn't change anything for datetime without TZ.
            elif isinstance(val, datetime) and val.tzinfo is not None:
                val = utcdatetime(val)
            elif isinstance(val, time) and val.tzinfo is not None:
                val = utctime(val)
            newargs[key] = val
        # should not collide
        assert not (frozenset(newargs) & frozenset(query_args)), \
            'unexpected collision: %s' % (frozenset(newargs) & frozenset(query_args))
        newargs.update(query_args)
        return newargs
    return query_args


@monkeypatch(rql2sql.SQLGenerator)
def visit_constant(self, constant):
    """generate SQL name for a constant"""
    if constant.type is None:
        return 'NULL'
    value = constant.value
    if constant.type == 'etype':
        return value
    # don't substitute int, causes pb when used as sorting column number
    if constant.type == 'Int':
        return str(value)
    if constant.type in ('Date', 'Datetime'):
        rel = constant.relation()
        if rel is not None:
            rel._q_needcast = value
        return self.keyword_map[value]()
    if constant.type == 'Substitute':
        try:
            # we may found constant from simplified var in varmap
            return self._mapped_term(constant, '%%(%s)s' % value)[0]
        except KeyError:
            _id = value
            if isinstance(_id, unicode):
                _id = _id.encode()
    else:
        _id = str(id(constant)).replace('-', '', 1)
        self._query_attrs[_id] = value
    return '%%(%s)s' % _id


# monkey-patch for https://www.cubicweb.org/ticket/7170830 #########################################

from cubicweb.server import migractions  # noqa


@monkeypatch(migractions.ServerMigrationHelper)
def cmd_change_attribute_type(self, etype, attr, newtype, commit=True):
    """low level method to change the type of an entity attribute. This is
    a quick hack which has some drawback:
    * only works when the old type can be changed to the new type by the
      underlying rdbms (eg using ALTER TABLE)
    * the actual schema won't be updated until next startup
    """
    rschema = self.repo.schema.rschema(attr)
    oldschema = rschema.objects(etype)[0]
    rdef = rschema.rdef(etype, oldschema)
    sql = ("UPDATE cw_CWAttribute "
           "SET cw_to_entity=(SELECT cw_eid FROM cw_CWEType WHERE cw_name='%s')"
           "WHERE cw_eid=%s") % (newtype, rdef.eid)
    self.sqlexec(sql, ask_confirm=False)
    dbhelper = self.repo.system_source.dbhelper
    sqltype = dbhelper.TYPE_MAPPING[newtype]
    cursor = self.cnx._cnx.cnxset.cu
    allownull = rdef.cardinality[0] != '1'
    dbhelper.change_col_type(cursor, 'cw_%s' % etype, 'cw_%s' % attr, sqltype, allownull)
    if commit:
        self.commit()
        # manually update live schema
        eschema = self.repo.schema[etype]
        rschema._subj_schemas[eschema].remove(oldschema)
        rschema._obj_schemas[oldschema].remove(eschema)
        newschema = self.repo.schema[newtype]
        rschema._update(eschema, newschema)
        rdef.object = newschema
        del rschema.rdefs[(eschema, oldschema)]
        rschema.rdefs[(eschema, newschema)] = rdef
