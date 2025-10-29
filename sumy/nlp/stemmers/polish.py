# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from pystempel import Stemmer as PystempelStemmer


class PolishStemmer(object):
    """
    Stemmer for Polish language using pystempel.
    """
    def __init__(self):
        self._stemmer = PystempelStemmer.polimorf()

    def stem(self, word):
        stemmed_word = self._stemmer(word)
        return stemmed_word if stemmed_word is not None else word


_stemmer = PolishStemmer()


def stem_word(word):
    return _stemmer.stem(word)
