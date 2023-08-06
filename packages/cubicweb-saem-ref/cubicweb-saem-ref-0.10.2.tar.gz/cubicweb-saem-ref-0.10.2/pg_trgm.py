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
"""Support for search auto-completion based on postgres'pg_trgm extension."""

from collections import defaultdict

from logilab.common.decorators import monkeypatch
from logilab.database.fti import normalize_words
from logilab.database.postgres import _PGAdvFuncHelper

from cubicweb.server import hook
from cubicweb.server.sources import native


old_sql_init_fti = _PGAdvFuncHelper.sql_init_fti


@monkeypatch(_PGAdvFuncHelper)
def sql_init_fti(self):
    """
    this monkeypatch create `words` table and `pg_trgm` extension
    """
    schema = old_sql_init_fti(self)
    schema += ''';
CREATE EXTENSION  pg_trgm;
CREATE TABLE words (
  etype VARCHAR(64) NOT NULL,
  word VARCHAR(100) NOT NULL,
  count INT DEFAULT 1
);

CREATE UNIQUE INDEX words_unique_idx ON words (etype, word);

CREATE INDEX words_word_idx ON words USING gin(word gin_trgm_ops);

ALTER TABLE appears ADD pwords text ARRAY;

'''
    return schema

old_sql_drop_fti = _PGAdvFuncHelper.sql_drop_fti


@monkeypatch(_PGAdvFuncHelper)
def sql_drop_fti(self):
    """this monkeypatch drop `words` table and `pg_trgm` extension
    """
    schema = sql_drop_fti(self)
    schema += ''';
    DROP TABLE words;
    DROP EXTENSION  pg_trgm;
    DROP INDEX words_unique_idx ON words (etype, word);
    '''
    return schema


class HandleWordsIdxOp(hook.DataOperationMixIn, hook.LateOperation):
    containercls = dict

    def add_data(self, etype, words, offset):
        etype_words = self._container.setdefault(etype, defaultdict(int))
        for word in words:
            etype_words[word] += offset

    def precommit_event(self):
        cursor = self.cnx.cnxset.cu
        args = []
        for etype, words in self.get_data().iteritems():
            for word, offset in words.iteritems():
                if offset != 0:
                    args.append({'etype': etype, 'word': word, 'offset': offset})
        if not args:
            return
        cursor.executemany("UPDATE words SET count=count+%(offset)s "
                           "WHERE word=%(word)s AND etype=%(etype)s;",
                           args)
        # remove columns with count < 1
        cursor.execute("DELETE FROM words WHERE count < 1")
        args = (arg for arg in args if arg['offset'] > 0)
        cursor.executemany("INSERT INTO words(word, etype, count) "
                           "SELECT %(word)s, %(etype)s, %(offset)s "
                           "WHERE NOT EXISTS (SELECT 1 FROM words "
                           "                  WHERE word=%(word)s AND etype=%(etype)s)",
                           args)


orig_fti_unindex_entities = native.NativeSQLSource.fti_unindex_entities


@monkeypatch(native.NativeSQLSource)
def fti_unindex_entities(self, cnx, entities):
    """this monkeypatch register removal of words for synchronization of the`words ` table."""
    if self.dbdriver == 'postgres':
        words_op = HandleWordsIdxOp.get_instance(cnx)
        cursor = cnx.cnxset.cu
        for entity in entities:
            cursor.execute("SELECT pwords FROM appears WHERE uid=%s;" % entity.eid)
            words = cursor.fetchone()
            if words and words[0]:
                words_op.add_data(entity.cw_etype, words[0], -1)
    orig_fti_unindex_entities(self, cnx, entities)


orig_fti_index_entities = native.NativeSQLSource.fti_index_entities


@monkeypatch(native.NativeSQLSource)
def fti_index_entities(self, cnx, entities):
    """this monkeypatch register addition of words for synchronization of the`words ` table."""
    if self.dbdriver == 'postgres':
        words_op = HandleWordsIdxOp.get_instance(cnx)
        cursor = cnx.cnxset.cu
        try:
            for entity in entities:
                words = cursor_index_object(self.dbhelper, entity.eid,
                                            entity.cw_adapt_to('IFTIndexable'), cursor)
                if words:
                    words_op.add_data(entity.cw_etype, words, +1)
        except Exception:  # pylint: disable=broad-except
            self.exception('error while indexing %s', entity)
    else:
        orig_fti_index_entities(self, cnx, entities)


def cursor_index_object(self, uid, obj, cursor):
    """this monkeypatch populates the `words` table"""
    ctx = {'config': self.config, 'uid': int(uid)}
    tsvectors, size, oversized = [], 0, False
    # set of words in their original spelling (monkeypatch)
    plain_words = set()
    # sort for test predictability
    for (weight, words) in sorted(obj.get_words().items()):
        normalized_words = normalize_words(words)
        for i, word in enumerate(normalized_words):
            size += len(word) + 1
            if size > self.max_indexed:
                normalized_words = normalized_words[:i]
                oversized = True
                break
        if normalized_words:
            for word in words:
                if len(word) > 1:
                    plain_words.add(word.lower())  # (monkeypatch)
            tsvectors.append("setweight(to_tsvector(%%(config)s, "
                             "%%(wrds_%(w)s)s), '%(w)s')"
                             % {'w': weight})
            ctx['wrds_%s' % weight] = ' '.join(normalized_words)
        if oversized:
            break
    if tsvectors:
        # monkeypatch
        ctx['words'] = list(plain_words)
        cursor.execute("INSERT INTO appears(uid, words, weight, pwords) "
                       "VALUES (%%(uid)s, %s, %s, %%(words)s);"
                       % ('||'.join(tsvectors), obj.entity_weight), ctx)
        # monkeypatch end
    else:
        plain_words = plain_words.clear()
    return plain_words
