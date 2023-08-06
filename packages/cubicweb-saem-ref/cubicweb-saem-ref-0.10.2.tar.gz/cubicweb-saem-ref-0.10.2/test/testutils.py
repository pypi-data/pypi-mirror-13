"""cubicweb-saem_ref common test tools"""

import unittest
from doctest import Example

from lxml import etree
from lxml.doctestcompare import LXMLOutputChecker


def agent(cnx, name, kind=u'person', archival_roles=(), **kwargs):
    """Return an Agent with specified kind, name and archival roles."""
    kind_eid = cnx.find('AgentKind', name=kind)[0][0]
    if archival_roles:
        if len(archival_roles) > 1:
            rset = cnx.execute('Any X WHERE X is ArchivalRole, X name IN (%s)' %
                               ','.join('"%s"' % r for r in archival_roles))
        else:
            rset = cnx.execute('Any X WHERE X is ArchivalRole, X name "%s"' %
                               archival_roles[0])
        roles_eid = [x for x, in rset.rows]
    else:
        roles_eid = ()
    return cnx.create_entity('Agent', name=name, agent_kind=kind_eid,
                             archival_role=roles_eid, **kwargs)


def setup_seda_agents(cnx):
    """Return two agents, one with the 'deposit' archival role, another with
    the 'archival' archival role.
    """
    alice = agent(cnx, u'alice')
    city = agent(cnx, u'New York city', kind=u'authority',
                 archival_roles=[u'archival'], contact_point=alice)
    bob = agent(cnx, u'bob', archival_roles=['deposit'], archival_agent=city)
    return bob, city


def setup_seda_profile(cnx, complete_archive=True, **kwargs):
    """Return a minimal SEDA profile with agents and a profile archive (with or without content
    description and access restriction code according to the `complete_archive` flag).
    """
    transferring_agent, archival_agent = setup_seda_agents(cnx)
    create_entity = cnx.create_entity
    profile = create_entity('SEDAProfile', seda_transferring_agent=transferring_agent, **kwargs)
    kwargs = {}
    if complete_archive:
        kwargs['seda_content_description'] = create_entity(
            'SEDAContentDescription',
            seda_description_level=create_entity('SEDADescriptionLevel'))
        kwargs['seda_access_restriction_code'] = create_entity('SEDAAccessRestrictionCode')
    create_entity('ProfileArchiveObject', seda_name=create_entity('SEDAName'),
                  seda_parent=profile, **kwargs)
    return profile


def publishable_profile(cnx, **kwargs):
    """Return a minimal SEDA profile that may be published."""
    create_entity = cnx.create_entity
    profile = create_entity('SEDAProfile', **kwargs)
    create_entity('ProfileArchiveObject',
                  seda_parent=profile,
                  seda_name=create_entity('SEDAName'),
                  seda_content_description=create_entity(
                      'SEDAContentDescription',
                      seda_description_level=create_entity('SEDADescriptionLevel')),
                  seda_access_restriction_code=create_entity('SEDAAccessRestrictionCode'))
    return profile


def concept(cnx, label):
    """Return concept entity with the given preferred label (expected to be unique)."""
    return cnx.execute('Concept X WHERE X preferred_label L, L label %(label)s',
                       {'label': label}).one()


#
# XML helpers
#

def xmlpp(string):
    """Parse and pretty-print XML data from `string`."""
    print etree.tostring(etree.fromstring(string), pretty_print=True)


class XmlTestMixin(unittest.TestCase):
    """Mixin class provinding additional assertion methods for checking XML data."""

    def assertXmlEqual(self, actual, expected):
        """Check that both XML strings represent the same XML tree."""
        checker = LXMLOutputChecker()
        if not checker.check_output(expected, actual, 0):
            message = checker.output_difference(Example("", expected), actual, 0)
            self.fail(message)

    def assertXmlValid(self, xml_data, xsd_filename, debug=False):
        """Validate an XML file (.xml) according to an XML schema (.xsd)."""
        with open(xsd_filename) as xsd:
            xmlschema = etree.XMLSchema(etree.parse(xsd))
        # Pretty-print xml_data to get meaningfull line information.
        xml_data = etree.tostring(etree.fromstring(xml_data), pretty_print=True)
        xml_data = etree.fromstring(xml_data)
        if debug and not xmlschema.validate(xml_data):
            xmlpp(xml_data)
        xmlschema.assertValid(xml_data)
