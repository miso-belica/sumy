# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals


def stem_word(word):
    """
    Stemmer for Polish language using pystempel.
    The import is done lazily to avoid requiring pystempel for users who don't need Polish.
    """
    # Cache the stemmer instance to avoid recreating it on every call
    if not hasattr(stem_word, '_stemmer'):
        try:
            from pystempel import Stemmer as PystempelStemmer
        except ImportError:
            raise ValueError("Polish stemmer requires pystempel. Please, install it by command 'pip install pystempel'.")
        stem_word._stemmer = PystempelStemmer.polimorf()

    stemmed_word = stem_word._stemmer(word)
    return stemmed_word if stemmed_word is not None else word
