# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from itertools import chain


class Document(object):
    def __init__(self, paragraphs):
        self._paragraphs = tuple(paragraphs)

    @property
    def paragraphs(self):
        return self._paragraphs

    @property
    def sentences(self):
        return chain(*(p.sentences for p in self._paragraphs))

    @property
    def words(self):
        words = (p.words for p in self._paragraphs)
        return chain(*words)
