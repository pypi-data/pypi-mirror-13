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
"""cubicweb-saem-ref predicates"""

from logilab.common.registry import Predicate, objectify_predicate

from cubicweb import Unauthorized


class is_connector(Predicate):
    """Return 1 is entity with specified `connector_eid` is a connector of
    type `connector_type`.
    """
    def __init__(self, connector_type):
        self.connector_type = connector_type

    def __call__(self, cls, req, connector_eid=None, **kwargs):
        if connector_eid is None:
            return 0
        return int(req.entity_metas(connector_eid)['type'] == self.connector_type)


class eid_is_etype(Predicate):
    """Return 1 is entity specified by the `eid` argument is of one of the
    given entity type.
    """
    def __init__(self, *etype):
        self.etypes = set(etype)

    def __call__(self, cls, req, eid=None, **kwargs):
        if eid is None:
            return 0
        return int(req.entity_metas(eid)['type'] in self.etypes)


class etype_exists(Predicate):
    """Return 1 if there exists some entity of the given etype"""
    def __init__(self, etype):
        self.etype = etype

    def __call__(self, cls, req, **kwargs):
        try:
            rset = req.execute('Any COUNT(X) WHERE X is %s' % self.etype)
        except Unauthorized:  # XXX
            return 0
        return rset[0][0]


def entity_has_mirror(entity):
    """Return 1 if the entity has a mirror entity."""
    with entity._cw.security_enabled(read=False):
        if entity.reverse_mirror_of:
            return 1
    return 0


@objectify_predicate
def eid_has_mirror(cls, req, eid=None, **kwargs):
    """Return 1 if the entity with `eid` has a mirror entity."""
    if eid is None:
        return 0
    return entity_has_mirror(req.entity_from_eid(eid))
