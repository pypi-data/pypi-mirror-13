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
"""Auto-completion in search widgets."""

from collections import defaultdict

from logilab.mtconverter import xml_escape

from cubicweb import Unauthorized
from cubicweb.uilib import domid
from cubicweb.utils import json_dumps, make_uid
from cubicweb.view import StartupView
from cubicweb.web import facet as facetbase
from cubicweb.web.views.boxes import SearchBox
from cubicweb.web.views.facets import HasTextFacet

__docformat__ = "restructuredtext en"

# XXX The words selection should be done in RQL ::
#     Any X HAVING W=WORDS(%(q)s)
#     or
#     Any W, SIMILARITY(W) HAVING W=WORDS(%(q)s)
#
# However, with WORDS class declared as above::
#
#     class WORDS(FunctionDescr):
#         supported_backends = ('postgres',)
#         rtype = 'String'
#
# the resulting sql for Any X HAVING W=WORDS('toto') states :
#
#       SELECT _W.eid
#       FROM entities AS _W
#       WHERE _W.eid=WORDS(%(140390076097112)s) {'140390076097112': u'toto'}
#
# Some more modifications are needed in `server/sources/rql2sql.py`,
# which we dont't want to do for instance.


def get_results_from_query(cnx, param):
    return cnx.system_sql('''SELECT word, etype, similarity(word, %(q)s) AS sml
FROM words
WHERE similarity(word, %(q)s) > 0.4
AND length(word) > length(%(q)s)-1
ORDER BY sml DESC, word, etype
LIMIT 20;''', param).fetchall()


class AutocompleteSearchView(StartupView):
    """The principal view for autocomplete search
    """
    __regid__ = 'search-autocomplete'
    templatable = False
    binary = True

    def rqlexec(self, rql, args=None):
        """Utility method to execute some rql queries, and simply returning an
        empty list if :exc:`Unauthorized` is raised.
        """
        try:
            return self._cw.execute(rql, args)
        except Unauthorized:
            return []

    def call(self):
        rset = get_results_from_query(self._cw.cnx, {'q': self._cw.form.get('term')})
        if not rset:
            self.w(json_dumps([]))
        results = []
        rql = self._cw.form['facetrql']
        all_words = ' '.join(self._cw.form['all'].split()[:-1])
        if rql:
            res = self._build_results_for_facet(rset, rql, all_words)
        else:
            res = self._build_results_for_search(rset, all_words)
        for word, labels in res:
            results.append({'label': '%s : %s' % (word, ', '.join(sorted(labels))),
                            'value': word})
        self.w(json_dumps(results))

    def _build_results_for_search(self, rset, all_words):
        _ = self._cw._
        processed = defaultdict(list)
        words = []
        for word, etype, score in rset:
            if all_words:
                # test the hole phrase exists
                res = self.rqlexec('Any X ORDERBY FTIRANK(X) DESC WHERE X has_text %(text)s',
                                   {'text': '%s %s' % (all_words, word)})
            if not all_words or res:
                processed[word].append(_(etype))
                if word not in words:
                    words.append(word)
        return [(w, processed[w]) for w in words]

    def _build_results_for_facet(self, rset, rql, all_words):
        _ = self._cw._
        select = self._cw.vreg.parse(self._cw, rql).children[0]
        filtered_variable = facetbase.get_filtered_variable(select)
        processed = defaultdict(list)
        words = []
        for word, etype, score in rset:
            if word in processed:
                processed[word].append(_(etype))
                continue
            if all_words:
                # test the hole phrase exists
                select.save_state()
                try:
                    select.add_constant_restriction(filtered_variable,
                                                    'has_text',
                                                    '%s %s' % (all_words, word),
                                                    'String')
                    res = self.rqlexec(select.as_string())
                finally:
                    select.recover()
            if not all_words or res:
                processed[word].append(_(etype))
                words.append(word)
        return [(w, processed[w]) for w in words]


class AutocompleteSearchBox(SearchBox):
    formdef = '''
<form action="%(action)s" id="search_box" class="navbar-form" role="search">
  <input id="norql" autocomplete="off" type="text" accesskey="q" tabindex="%(tabindex1)s"
    title="search text" value="%(value)s" name="rql"
    class="search-query form-control" placeholder="%(searchlabel)s"/>
  <input type="hidden" name="__fromsearchbox" value="1" />
  <input type="hidden" name="subvid" value="tsearch" />
</form>
'''

    def render_body(self, w):
        self._cw.add_js(('jquery.ui.js', 'cubicweb.autocompletesearch.js'))
        self._cw.add_css(('jquery.ui.css',))
        url = self._cw.build_url('view', vid='search-autocomplete')
        minlength = 2
        limit = 20
        self._cw.add_onload('cw.search_autocomplete($("#norql"), "%s", %s, %s);'
                            % (url, minlength, limit))
        super(AutocompleteSearchBox, self).render_body(w)


class AutocompleteSearchWidget(facetbase.FacetStringWidget):

    def _render(self):
        """ has-hext facet widget with autocomplete"""
        req = self.facet._cw
        facetid = domid(make_uid(self.facet.__regid__))
        input_id = xml_escape('id-%s' % facetid)
        req.add_js(('jquery.ui.js', 'cubicweb.autocompletesearch.js'))
        req.add_css(('jquery.ui.css', ))
        url = req.build_url('view', vid='search-autocomplete')
        minlength = 2
        limit = 20
        req.add_onload('cw.search_autocomplete($("#%s"), "%s", %s, %s);' % (
            input_id, url, minlength, limit))
        w = self.w
        title = xml_escape(self.facet.title)
        w(u'<div id="%s" class="facet">\n' % facetid)
        cssclass = 'facetTitle'
        if self.facet.allow_hide:
            cssclass += ' hideFacetBody'
        w(u'<div class="%s" cubicweb:facetName="%s">%s</div>\n' %
            (cssclass, xml_escape(self.facet.__regid__), title))
        cssclass = 'facetBody'
        if not self.facet.start_unfolded:
            cssclass += ' hidden'
        w(u'<div class="%s">\n' % cssclass)
        w((u'<input autocomplete="off" id="%s" name="%s" '
            'type="text" value="%s" data-facet="1"/>\n') % (
            input_id, xml_escape(self.facet.__regid__),
            self.value or u''))
        w(u'</div>\n')
        w(u'</div>\n')


def registration_callback(vreg):
    try:
        import psycopg2
    except ImportError:
        psycopg2 = None
    if psycopg2:
        vreg.register_all(globals().values(), __name__, [])
        vreg.unregister(SearchBox)
        HasTextFacet.wdgclass = AutocompleteSearchWidget
