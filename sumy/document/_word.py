# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from .._object import Object
from .._py3k import to_unicode, string_types


class Word(Object):
    __slots__ = ("_word",)

    def __init__(self, word):
        self._word = to_unicode(word)

    def is_stopword(self, stopwords):
        return self._word.lower() in stopwords

    def _to_string(self):
        return self._word

    def __hash__(self):
        return hash(self._word)

    def __eq__(self, word):
        return self._word == to_unicode(word)

    def __ne__(self, word):
        return self._word != to_unicode(word)

    def __lt__(self, word):
        return self._word < to_unicode(word)

    def __le__(self, word):
        return self._word <= to_unicode(word)

    def __gt__(self, word):
        return self._word > to_unicode(word)

    def __ge__(self, word):
        return self._word >= to_unicode(word)
