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
"""cubicweb-saem-ref dataimport utilities for EAC-CPF (Encoded Archival
Context -- Corporate Bodies, Persons, and Families).
"""

import datetime
from functools import wraps
import inspect
import logging
from uuid import uuid4

from dateutil.parser import parse as parse_date
from lxml import etree

from cubes.skos import ExtEntity, to_unicode

ETYPES_ORDER_HINT = ('AgentKind', 'PhoneNumber', 'PostalAddress', 'Agent',
                     'AgentPlace', 'Mandate', 'LegalStatus', 'History',
                     'Structure', 'AgentFunction',
                     'AssociationRelation', 'ChronologicalRelation', 'HierarchicalRelation',
                     'EACResourceRelation', 'ExternalUri', 'EACSource',
                     'Activity')


class InvalidEAC(RuntimeError):
    """EAC input is malformed."""


class InvalidXML(RuntimeError):
    """EAC input has an invalid XML format"""


class MissingTag(RuntimeError):
    """Mandatory tag is missing in EAC input"""

    def __init__(self, tag, tag_parent=None):
        super(MissingTag, self).__init__()
        self.tag = tag
        self.tag_parent = tag_parent


def external_uri(uri):
    values = [unicode(uri)]
    return ExtEntity('ExternalUri', uri, {'uri': set(values), 'cwuri': set(values)})


def filter_none(func):
    """Filter None value from a generator function."""
    def wrapped(*args, **kwargs):
        for x in func(*args, **kwargs):
            if x is not None:
                yield x
    return wraps(func)(wrapped)


def elem_maybe_none(func):
    """Method decorator for external entity builder function handling the case
    of `elem` being None.
    """
    if inspect.isgeneratorfunction(func):
        def wrapped(self, elem, *args, **kwargs):
            if elem is None:
                return
            for extentity in func(self, elem, *args, **kwargs):
                yield extentity
    else:
        def wrapped(self, elem, *args, **kwargs):
            if elem is None:
                return None
            else:
                return func(self, elem, *args, **kwargs)
    return wraps(func)(wrapped)


def require_tag(tagname):
    """Method decorator handling a mandatory tag within a XML element."""
    def warn(self, elem):
        self.import_log.record_warning(
            self._('expecting a %s tag in element %s, found none') %
            (tagname, elem.tag), line=elem.sourceline)

    def decorator(func):
        if inspect.isgeneratorfunction(func):
            def wrapped(self, elem, *args, **kwargs):
                if self._elem_find(elem, tagname) is None:
                    warn(self, elem)
                    return
                for extentity in func(self, elem, *args, **kwargs):
                    yield extentity
        else:
            def wrapped(self, elem, *args, **kwargs):
                if self._elem_find(elem, tagname) is None:
                    warn(self, elem)
                    return None
                return func(self, elem, *args, **kwargs)
        return wraps(func)(wrapped)

    return decorator


def vocabulary_source(tagname, etype):
    """Method decorator indicating that a sub-tag may have a vocabularySource attribute indicating
    that a relation to some ExternalUri object should be drown from any entity of type `etype` built
    by decorated method.
    """
    def decorator(func):
        @wraps(func)
        def wrapped(self, elem, *args, **kwargs):
            subelem = self._elem_find(elem, tagname)
            if subelem is not None:
                extid = subelem.attrib.get('vocabularySource')
                if extid is not None:
                    yield external_uri(extid)
            else:
                extid = None

            def update_extentity(extentity):
                if extid is not None and extentity.etype == etype:
                    extentity.values['vocabulary_source'] = set([extid])

            if inspect.isgeneratorfunction(func):
                for extentity in func(self, elem, *args, **kwargs):
                    update_extentity(extentity)
                    yield extentity
            else:
                extentity = func(self, elem, *args, **kwargs)
                update_extentity(extentity)
                yield extentity
        return wrapped
    return decorator


class EACCPFImporter(object):
    """Importer for EAC-CPF data.

    The importer will generate `extid`s using the `extid_generator` function
    if specified or use `uuid.uuid4` to generate unique `extid`s.

    During import the `agent` attribute is set to the external entity of the
    imported Agent.

    Ref: http://eac.staatsbibliothek-berlin.de/fileadmin/user_upload/schema/cpfTagLibrary.html
    """
    def __init__(self, fpath, import_log, _, extid_generator=None):
        try:
            tree = etree.parse(fpath)
        except etree.XMLSyntaxError as exc:
            raise InvalidXML(str(exc))
        self._ = _
        self._root = tree.getroot()
        self.namespaces = self._root.nsmap.copy()
        self.namespaces['eac'] = self.namespaces.pop(None)
        self.import_log = import_log
        if extid_generator is None:
            def extid_generator():
                return str(uuid4())
        self._gen_extid = extid_generator
        self.agent = ExtEntity('Agent', None, {})

    def _elem_find(self, elem, path, method='find'):
        """Wrapper around lxml.etree.Element find* methods to support
        namespaces also for old lxml versions.
        """
        finder = getattr(elem, method)
        try:
            return finder(path, self.namespaces)
        except TypeError:
            # In old lxml, find() does not accept namespaces argument.
            path = path.split(':', 1)
            try:
                ns, path = path
            except ValueError:
                # path has no namespace
                pass
            else:
                path = '{' + self.namespaces[ns] + '}' + path
            return finder(path)

    def _elem_findall(self, *args):
        return self._elem_find(*args, method='findall')

    def external_entities(self):
        """Parse a EAC XML file to and yield external entities."""
        # control element.
        control = self._elem_find(self._root, 'eac:control')
        for extentity in self.parse_control(control):
            yield extentity
        # Agents (identity tags) are within cpfDescription tag.
        cpf_desc = self._elem_find(self._root, 'eac:cpfDescription')
        if cpf_desc is None:
            raise MissingTag('cpfDescription')
        # identity element.
        for extentity in self.parse_identity(cpf_desc):
            yield extentity
        # description element.
        for extentity in self.parse_description(cpf_desc):
            yield extentity
        # relations element.
        for extentity in self.parse_relations(cpf_desc):
            yield extentity
        # Agent is complete.
        yield self.agent

    def parse_identity(self, cpf_description):
        """Parse the `identity` tag and yield external entities, possibly
        updating agent's `values` dict.
        """
        identity = self._elem_find(cpf_description, 'eac:identity')
        if identity is None:
            raise MissingTag('identity', 'cpfDescription')
        # entityId
        isni = self._elem_find(identity, 'eac:entityId')
        if isni is not None:
            self.agent.values['isni'] = set([unicode(isni.text)])
        # entityType
        akind = self._elem_find(identity, 'eac:entityType')
        if akind is None:
            raise MissingTag('entityType', 'cpfDescription')
        agent_kind = self.build_agent_kind(akind)
        yield agent_kind
        self.agent.values['agent_kind'] = set([agent_kind.extid])
        # nameEntry.
        # look for the nameEntry with authorizedForm, take its part
        # element.
        name_entry_part = identity.xpath(
            '//eac:nameEntry/eac:part[../eac:authorizedForm]',
            namespaces=self.namespaces)
        if name_entry_part is not None:
            self.agent.values.setdefault('name', set()).add(
                unicode(name_entry_part[0].text))
        else:
            raise NotImplementedError('found no nameEntry with authorizedForm')

    @filter_none
    def parse_description(self, cpf_description):
        """Parse the `description` tag and yield external entities, possibly
        updating agent's `values` dict.
        """
        description = self._elem_find(cpf_description, 'eac:description')
        if description is None:
            return
        # dates.
        daterange = description.xpath('eac:existDates/eac:dateRange',
                                      namespaces=self.namespaces)
        if daterange:
            dates = self.parse_daterange(daterange[0])
            if dates:
                self.agent.values.update(dates)
        # address.
        for place in self.find_nested(description, 'eac:place', 'eac:places'):
            for extentity in self.build_place(place):
                yield extentity
        # additional EAC-CPF information.
        for legal_status in self._elem_findall(description, 'eac:legalStatus'):
            for extentity in self.build_legal_status(legal_status):
                yield extentity
        for mandate in self._elem_findall(description, 'eac:mandate'):
            for extentity in self.build_mandate(mandate):
                yield extentity
        for history in self._elem_findall(description, 'eac:biogHist'):
            yield self.build_history(history)
        for structure in self._elem_findall(description, 'eac:structureOrGenealogy'):
            yield self.build_structure(structure)
        # function elements (may appear under 'description' and/or 'functions').
        for function in self.find_nested(description, 'eac:function', 'eac:functions'):
            for extentity in self.build_function(function):
                yield extentity

    def find_nested(self, elem, tagname, innertag):
        """Return a list of element with `tagname` within `element` possibly
        nested within `innertag`.
        """
        all_elems = self._elem_findall(elem, tagname)
        wrappers = self._elem_find(elem, innertag)
        if wrappers is not None:
            all_elems.extend(self._elem_findall(wrappers, tagname))
        return all_elems

    def parse_tag_description(self, elem, tagname='eac:descriptiveNote',
                              attrname='description'):
        """Return a dict with `attrname` and `attrname`_format retrieved from
        a description-like tag.
        """
        elems = self._elem_findall(elem, tagname)
        if len(elems) > 1:
            self.import_log.record_warning(self._(
                'found multiple %s tag within %s element, only one will be '
                'used.') % (tagname, elem.tag), line=elem.sourceline)
        elem = elems[0] if elems else None
        values = {}
        if elem is not None:
            parsed = self.parse_tag_content(elem)
            values.update(zip((attrname, attrname + '_format'),
                              (set([p]) for p in parsed)))
        return values

    def parse_tag_content(self, elem):
        """Parse the content of an element be it text of HTML and return the
        content along with MIME type.
        """
        assert elem is not None, 'unexpected empty element'
        text = elem.text.strip() if elem.text else None
        if text:
            desc, desc_format = unicode(text), u'text/plain'
        else:
            ptag = '{%(eac)s}p' % self.namespaces
            desc = '\n'.join(etree.tostring(child, encoding=unicode,
                                            method='html')
                             for child in elem.iterchildren(ptag))
            if desc:
                desc_format = u'text/html'
            else:
                self.import_log.record_warning(self._(
                    'element %s has no text nor children, no content '
                    'extracted') % elem.tag, line=elem.sourceline)
                desc, desc_format = None, None
        return desc, desc_format

    @elem_maybe_none
    def build_agent_kind(self, elem):
        """Build a AgentKind external entity"""
        # Map EAC entity types to our terminolgy.
        kind = {'corporateBody': u'authority',
                'person': u'person',
                'family': u'family',
                'human': u'person'}.get(elem.text, elem.text)
        agentkind_id = 'agentkind/' + kind
        return ExtEntity('AgentKind', agentkind_id, {'name': set([kind])})

    @elem_maybe_none
    @vocabulary_source('eac:term', 'LegalStatus')
    def build_legal_status(self, elem, **kwargs):
        """Build a `LegalStatus` external entity.

        Extra `kwargs` are passed to `parse_tag_description`.
        """
        values = {}
        term = self._elem_find(elem, 'eac:term')
        if term is not None and term.text:
            values['term'] = set([unicode(term.text)])
        values.update(**self.parse_tag_description(elem, **kwargs))
        dateelem = self._elem_find(elem, 'eac:dateRange')
        dates = self.parse_daterange(dateelem)
        if dates:
            values.update(dates)
        # don't build an entity if it only owns the agent relation
        if values:
            values['legal_status_agent'] = set([self.agent.extid])
            return ExtEntity('LegalStatus', self._gen_extid(), values)

    @elem_maybe_none
    @vocabulary_source('eac:term', 'Mandate')
    def build_mandate(self, elem, **kwargs):
        """Build a `Mandate` external entity.

        Extra `kwargs` are passed to `parse_tag_description`.
        """
        values = {}
        term = self._elem_find(elem, 'eac:term')
        if term is not None and term.text:
            values['term'] = set([unicode(term.text)])
        values.update(**self.parse_tag_description(elem, **kwargs))
        dateelem = self._elem_find(elem, 'eac:dateRange')
        dates = self.parse_daterange(dateelem)
        if dates:
            values.update(dates)
        if values:
            values['mandate_agent'] = set([self.agent.extid])
            return ExtEntity('Mandate', self._gen_extid(), values)

    @elem_maybe_none
    def build_history(self, elem):
        """Build a `History` external entity."""
        desc, desc_format = self.parse_tag_content(elem)
        if desc:
            values = {'history_agent': set([self.agent.extid]),
                      'text': set([desc]),
                      'text_format': set([desc_format])}
            return ExtEntity('History', self._gen_extid(), values)

    @elem_maybe_none
    def build_structure(self, elem):
        """Build a `Structure` external entity."""
        desc, desc_format = self.parse_tag_content(elem)
        if desc:
            values = {'structure_agent': set([self.agent.extid]),
                      'description': set([desc]),
                      'description_format': set([desc_format])}
            return ExtEntity('Structure', self._gen_extid(), values)

    @vocabulary_source('eac:placeEntry', 'AgentPlace')
    def build_place(self, elem):
        """Build a AgentPlace external entity"""
        values = {'place_agent': set([self.agent.extid])}
        role = self._elem_find(elem, 'eac:placeRole')
        if role is not None:
            values['role'] = set([unicode(role.text)])
        entry = self._elem_find(elem, 'eac:placeEntry')
        if entry is not None:
            values['name'] = set([unicode(entry.text)])
        for address in self._elem_findall(elem, 'eac:address'):
            for extentity in self.build_address(address):
                values['place_address'] = set([extentity.extid])
                yield extentity
        yield ExtEntity('AgentPlace', self._gen_extid(), values)

    def build_address(self, elem):
        """Build `PostalAddress`s external entity"""
        address_eac2schema = {'StreetName': 'street',
                              'PostCode': 'postalcode',
                              'CityName': 'city'}
        address_entity = {}
        for line in self._elem_findall(elem, 'eac:addressLine'):
            if 'localType' in line.attrib:
                attr = address_eac2schema.get(line.attrib['localType'])
                if attr:
                    address_entity.setdefault(attr, set()).add(
                        unicode(line.text))
        yield ExtEntity('PostalAddress', self._gen_extid(), address_entity)

    @vocabulary_source('eac:term', 'AgentFunction')
    def build_function(self, elem):
        """Build a `AgentFunction`s external entities"""
        values = {}
        term = self._elem_find(elem, 'eac:term')
        if term is not None:
            values['name'] = set([unicode(term.text)])
        values.update(self.parse_tag_description(elem))
        if values:
            values['function_agent'] = set([self.agent.extid])
            yield ExtEntity('AgentFunction', self._gen_extid(), values)

    @elem_maybe_none
    def parse_daterange(self, elem):
        """Parse a `dateRange` tag and return a dict mapping `start_date` and
        `end_date` to parsed date range.
        """
        values = {}
        for eactag, attrname in zip(('eac:fromDate', 'eac:toDate'),
                                    ('start_date', 'end_date')):
            date = self.parse_date(self._elem_find(elem, eactag))
            if date:
                values[attrname] = set([date])
        return values

    @elem_maybe_none
    def parse_date(self, elem):
        """Parse a date-like element"""
        def record_warning(msg):
            self.import_log.record_warning(msg % {'e': etree.tostring(elem)},
                                           line=elem.sourceline)
        standard_date = elem.attrib.get('standardDate')
        if standard_date:
            date = standard_date
        else:
            for attr in ('notBefore', 'notAfter'):
                if elem.attrib.get(attr):
                    record_warning(self._('found an unsupported %s attribute in date '
                                          'element %%(e)s') % attr)
            # Using element's text.
            date = elem.text
        # Set a default value for month and day; the year should always be
        # given.
        default = datetime.datetime(9999, 1, 1)
        try:
            pdate = parse_date(date, default=default)
        except ValueError as exc:
            record_warning(self._('could not parse date %(e)s'))
            return None
        except Exception as exc:
            # Usually a bug in dateutil.parser.
            record_warning(self._(
                'unexpected error during parsing of date %%(e)s: %s') %
                to_unicode(exc))
            logger = logging.getLogger('cubicweb.saem_ref')
            logger.exception(self._('unhandled exception while parsing date %r'), date)
            return None
        else:
            if pdate.year == default.year:
                record_warning(self._('could not parse a year from date element %(e)s'))
                return None
            return pdate.date()

    def parse_relations(self, cpf_description):
        """Parse the `relations` tag and yield external entities, possibly
        updating agent's `values` dict.
        """
        relations = self._elem_find(cpf_description, 'eac:relations')
        if relations is None:
            return
        # cpfRelation.
        for cpfrel in self._elem_findall(relations, 'eac:cpfRelation'):
            for extentity in self.build_relation(cpfrel):
                yield extentity
        # resourceRelation.
        for rrel in self._elem_findall(relations, 'eac:resourceRelation'):
            for extentity in self.build_resource_relation(rrel):
                yield extentity

    def build_relation(self, elem):
        """Build a relation between agents external entity (with proper type)."""
        relationship = elem.attrib.get('cpfRelationType')
        if relationship is None:
            self.import_log.record_warning(self._(
                'found no cpfRelationType attribute in element %s') % etree.tostring(elem),
                line=elem.sourceline)
            return
        try:
            # "other_role" (resp. "agent_role") role designates the object of the relation (resp.
            # the agent described in the EAC-CPF instance).
            # See: http://eac.staatsbibliothek-berlin.de/fileadmin/user_upload/schema/cpfTagLibrary.html#cpfRelationType # noqa
            # In case the EAC relation is not qualified, we assume the object is the "parent" (or
            # oldest) in the relation.
            etype, other_role, agent_role = {
                'hierarchical': ('HierarchicalRelation',
                                 'hierarchical_parent', 'hierarchical_child'),
                'hierarchical-parent': ('HierarchicalRelation',
                                        'hierarchical_parent', 'hierarchical_child'),
                'hierarchical-child': ('HierarchicalRelation',
                                       'hierarchical_child', 'hierarchical_parent'),
                'temporal': ('ChronologicalRelation',
                             'chronological_predecessor', 'chronological_successor'),
                'temporal-earlier': ('ChronologicalRelation',
                                     'chronological_predecessor', 'chronological_successor'),
                'temporal-later': ('ChronologicalRelation',
                                   'chronological_successor', 'chronological_predecessor'),
                'associative': ('AssociationRelation',
                                'association_to', 'association_from'),
            }[relationship]
        except KeyError:
            self.import_log.record_warning(self._(
                'unsupported cpfRelationType %s in element %s, skipping')
                % (relationship, etree.tostring(elem)),
                line=elem.sourceline)
            return
        obj_uri = elem.attrib.get('{%(xlink)s}href' % self.namespaces)
        if obj_uri is None:
            self.import_log.record_warning(self._('found a cpfRelation without any object (no '
                                                  'xlink attribute), skipping'),
                                           line=elem.sourceline)
            return
        rentry = self._elem_find(elem, 'eac:relationEntry')
        if rentry is not None and rentry.text.strip():
            yield ExtEntity('Agent', obj_uri, {'name': set([unicode(rentry.text)]),
                                               'agent_kind': set(['agentkind/unknown-agent-kind'])})
        else:
            yield external_uri(obj_uri)
        values = {agent_role: set([self.agent.extid]), other_role: set([obj_uri])}
        dates = self.parse_daterange(
            self._elem_find(elem, 'eac:dateRange'))
        if dates:
            if etype == 'ChronologicalRelation':
                self.import_log.record_warning(
                    self._('ignoring dates on %s since chronological relation '
                           'does not support dates') % etree.tostring(elem)
                )
            else:
                values.update(dates)
        values.update(self.parse_tag_description(elem))
        yield ExtEntity(etype, self._gen_extid(), values)

    def build_resource_relation(self, elem):
        """Build a `EACResourceRelation` external entity (along with
        ExternalUri entities).
        """
        obj_uri = elem.attrib.get('{%(xlink)s}href' % self.namespaces)
        if obj_uri is None:
            self.import_log.record_warning(self._(
                'found a resourceRelation without any object (no xlink '
                'attribute), skipping'), line=elem.sourceline)
            return
        yield external_uri(obj_uri)
        values = {
            'resource_relation_resource': set([obj_uri]),
            'resource_relation_agent': set([self.agent.extid]),
        }
        resource_role = elem.attrib.get('{%(xlink)s}role' % self.namespaces)
        if resource_role:
            values['resource_role'] = set([unicode(resource_role)])
        agent_role = elem.attrib.get('resourceRelationType')
        if agent_role:
            values['agent_role'] = set([unicode(agent_role)])
        dates = self.parse_daterange(self._elem_find(elem, 'eac:dateRange'))
        if dates:
            values.update(dates)
        values.update(self.parse_tag_description(elem))
        yield ExtEntity('EACResourceRelation', self._gen_extid(), values)

    @filter_none
    def parse_control(self, control):
        """Parse the `control` tag."""
        record_id = self._elem_find(control, 'eac:recordId')
        if record_id is not None and record_id.text and record_id.text.strip():
            self.agent.extid = record_id.text.strip()
        else:
            self.agent.extid = self._gen_extid()
            self.import_log.record_warning(self._(
                'found no recordId element in control tag, using %s as cwuri') %
                self.agent.extid)
        for elem in control.xpath('eac:sources/eac:source',
                                  namespaces=self.namespaces):
            yield self.parse_source(elem)
        for elem in control.xpath('eac:maintenanceHistory/eac:maintenanceEvent',
                                  namespaces=self.namespaces):
            for extentity in self.parse_maintenance_event(elem):
                yield extentity

    def parse_maintenance_event(self, elem):
        """Parse a `maintenanceEvent` tag, yielding a prov:Activity external
        entity along with necessary Agents.
        """
        values = {'generated': set([self.agent.extid])}
        event_type = self.parse_event_type(self._elem_find(elem, 'eac:eventType'))
        if event_type is not None:
            values['type'] = set([event_type])
        date = self._elem_find(elem, 'eac:eventDateTime')
        if date is not None:
            dtattr = date.attrib.get('standardDateTime')
            if dtattr:
                try:
                    event_date = parse_date(dtattr)
                except ValueError:
                    self.import_log.record_warning(
                        self._('could not parse date from %s') % etree.tostring(date),
                        line=date.sourceline)
                else:
                    values['start'] = set([event_date])
                    values['end'] = set([event_date])
        values.update(self.parse_tag_description(elem, 'eac:eventDescription'))
        agent = self._elem_find(elem, 'eac:agent')
        if agent is not None and agent.text:
            agent_type = self._elem_find(elem, 'eac:agentType')
            agent_kind = self.build_agent_kind(agent_type)
            if agent_kind is not None:
                yield agent_kind
                agent_kind_extid = agent_kind.extid
            else:
                agent_kind_extid = 'agentkind/unknown-agent-kind'
            agent_id = self._gen_extid()
            yield ExtEntity('Agent', agent_id,
                            {'name': set([unicode(agent.text)]),
                             'agent_kind': set([agent_kind_extid])})
            values['associated_with'] = set([agent_id])
        yield ExtEntity('Activity', self._gen_extid(), values)

    @elem_maybe_none
    def parse_event_type(self, elem):
        """Parse an `eventType` element and try to match a prov:type to build a
        prov:Activity.
        """
        event_type = elem.text.strip() if elem.text else None
        if event_type:
            try:
                event_type = {
                    "created": u'create',
                    "derived": u'create',
                    "revised": u'modify',
                    "updated": u'modify',
                }[event_type.lower()]
            except KeyError:
                self.import_log.record_warning(self._(
                    'eventType %s does not match the PROV-O vocabulary, respective Activity will '
                    'not have a `type` attribute set.') % event_type, line=elem.sourceline)
                return None
            return event_type

    def parse_source(self, elem):
        """Parse a `source` tag, yielding EACSource external entities.
        """
        values = {}
        url = elem.attrib.get('{%(xlink)s}href' % self.namespaces)
        if url is not None:
            values['url'] = set([unicode(url)])
        entry = self._elem_find(elem, 'eac:sourceEntry')
        if entry is not None and entry.text:
            values['title'] = set([unicode(entry.text)])
        values.update(self.parse_tag_description(elem))
        if values:
            values['source_agent'] = set([self.agent.extid])
            return ExtEntity('EACSource', self._gen_extid(), values)
