# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from itertools import chain


class Paragraph(object):
    def __init__(self, sentences):
        self._sentences = tuple(sentences)

    @property
    def sentences(self):
        return self._sentences

    @property
    def words(self):
        return tuple(chain(*(s.words for s in self._sentences)))
