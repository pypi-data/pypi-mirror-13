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
"""cubicweb-saem-ref entity's classes"""

from lxml import etree

from logilab.common.registry import yes

from cubicweb.view import Adapter, EntityAdapter
from cubicweb.predicates import match_kwargs
from cubicweb.entities import AnyEntity, fetch_config


class ARKGeneratorMixIn(object):
    """Entity adapter for ARK unique identifier generation"""
    __abstract__ = True
    __regid__ = 'IARKGenerator'
    naan = 'saemref-test'  # name assigning authority number

    def generate_ark(self):
        """Return a new ARK identifier as unicode"""
        return u'{0}/{1}'.format(self.naan, self.assign_name())

    def assign_name(self):
        """Assign and return a new name part of the ARK identifier"""
        raise NotImplementedError()


class ARKExtIdentifierGenerator(ARKGeneratorMixIn, Adapter):
    """Simple adapter for allocation of ark to object which are not (yet) entities."""
    __select__ = yes(.5)

    def assign_name(self):
        """Return a new unique identifier as unicode"""
        dbh = self._cw.repo.system_source.dbhelper
        for sql in dbh.sqls_increment_sequence('ext_ark_count'):
            cu = self._cw.system_sql(sql)
        count = cu.fetchone()[0]
        return u'ext-{0:09d}'.format(count)


class ARKCWIdentifierGenerator(ARKGeneratorMixIn, Adapter):
    """saem_ref.IARKGenerator entity adapter generating ARK like identifier during non-production
    phase.
    """
    __select__ = match_kwargs('eid')

    def assign_name(self):
        return u'{0:09d}'.format(self.cw_extra_kwargs['eid'])


class ExternalUri(AnyEntity):
    __regid__ = 'ExternalUri'
    fetch_attrs, cw_fetch_order = fetch_config(('uri',))


def substitute_xml_prefix(prefix_name, namespaces):
    """Given an XML prefixed name in the form `'ns:name'`, return the string `'{<ns_uri>}name'`
    where `<ns_uri>` is the URI for the namespace prefix found in `namespaces`.

    This new string is then suitable to build an LXML etree.Element object.

    Example::

        >>> substitude_xml_prefix('xlink:href', {'xlink': 'http://wwww.w3.org/1999/xlink'})
        '{http://www.w3.org/1999/xlink}href'

    """
    try:
        prefix, name = prefix_name.split(':', 1)
    except ValueError:
        return prefix_name
    assert prefix in namespaces, 'Unknown namespace prefix: {0}'.format(prefix)
    return '{{{0}}}'.format(namespaces[prefix]) + name


class AbstractXmlAdapter(EntityAdapter):
    """Abstract adapter to produce XML documents."""

    content_type = 'text/xml'
    encoding = 'utf-8'
    namespaces = {}

    @property
    def file_name(self):
        """Return a file name for the dump."""
        raise NotImplementedError

    def dump(self):
        """Return an XML string for the adapted entity."""
        raise NotImplementedError

    def element(self, tag, parent=None, attributes=None, text=None):
        """Generic function to build a XSD element tag.

        Params:

        * `name`, value for the 'name' attribute of the xsd:element

        * `parent`, the parent etree node

        * `attributes`, dictionary of attributes
        """
        attributes = attributes or {}
        tag = substitute_xml_prefix(tag, self.namespaces)
        for attr, value in attributes.items():
            newattr = substitute_xml_prefix(attr, self.namespaces)
            attributes[newattr] = value
            if newattr != attr:
                attributes.pop(attr)
        if parent is None:
            elt = etree.Element(tag, attributes, nsmap=self.namespaces)
        else:
            elt = etree.SubElement(parent, tag, attributes)
        if text is not None:
            elt.text = text
        return elt
