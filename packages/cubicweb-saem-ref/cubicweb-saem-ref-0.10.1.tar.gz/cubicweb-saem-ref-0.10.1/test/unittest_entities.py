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

from cubicweb.devtools.testlib import CubicWebTC


class ArkGeneratorTC(CubicWebTC):
    def test_eid(self):
        with self.admin_access.repo_cnx() as cnx:
            generator = self.vreg['adapters'].select('IARKGenerator', cnx, eid=12)
            self.assertEqual(generator.generate_ark(), 'saemref-test/000000012')

    def test_ext_identifier(self):
        with self.admin_access.repo_cnx() as cnx:
            generator = self.vreg['adapters'].select('IARKGenerator', cnx)
            self.assertEqual(generator.generate_ark(), 'saemref-test/ext-000000001')


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
