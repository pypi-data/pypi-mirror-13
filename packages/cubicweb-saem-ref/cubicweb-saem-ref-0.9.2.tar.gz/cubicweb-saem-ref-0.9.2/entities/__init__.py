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
"""cubicweb-saem-ref entity's classes"""

from logilab.common.registry import yes

from cubicweb.view import Adapter, EntityAdapter
from cubicweb.predicates import is_instance


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


class ARKCWIdentifierGenerator(ARKGeneratorMixIn, EntityAdapter):
    """saem_ref.IARKGenerator entity adapter generating ARK like identifier during non-production
    phase.
    """
    __select__ = is_instance('Any')

    def assign_name(self):
        return u'{0:09d}'.format(self.entity.eid)


class ARKExtIdentifierGenerator(ARKGeneratorMixIn, Adapter):
    """Simple adapter for allocation of ark to object which are not (yet) entities."""
    __select__ = yes()

    def assign_name(self):
        """Return a new unique identifier as unicode"""
        dbh = self._cw.repo.system_source.dbhelper
        for sql in dbh.sqls_increment_sequence('ext_ark_count'):
            cu = self._cw.system_sql(sql)
        count = cu.fetchone()[0]
        return u'ext-{0:09d}'.format(count)
