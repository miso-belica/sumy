# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from itertools import chain
from .._compat import to_unicode, to_string, unicode_compatible


@unicode_compatible
class Sentence(object):
    __slots__ = ("_words", "_is_heading",)

    def __init__(self, words, is_heading=False):
        self._words = tuple(map(to_unicode, words))
        self._is_heading = bool(is_heading)

    @property
    def words(self):
        return self._words

    @property
    def is_heading(self):
        return self._is_heading

    def __unicode__(self):
        return " ".join(self._words)

    def __repr__(self):
        return to_string("<Sentence: %s>") % self.__str__()
