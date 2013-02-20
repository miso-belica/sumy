# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from itertools import chain
from .._object import Object
from .._py3k import to_unicode


class Sentence(Object):
    __slots__ = ("_words", "_is_heading",)

    def __init__(self, words, is_heading=False):
        self._words = tuple(words)
        self._is_heading = bool(is_heading)

    @property
    def words(self):
        return self._words

    @property
    def is_heading(self):
        return self._is_heading

    def _to_string(self):
        words = map(to_unicode, self._words)
        return " ".join(words)
