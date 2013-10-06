# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from .czech import stem_word as czech_stemmer
from .german import stem_word as german_stemmer
from .english import stem_word as english_stemmer
from ..._compat import to_unicode


def null_stemmer(object):
    "Converts given object to unicode with lower letters."
    return to_unicode(object).lower()


class Stemmer(object):
    NULL = null_stemmer
    _LANGUAGES = {
        "czech": czech_stemmer,
        "slovak": czech_stemmer,
        "german": german_stemmer,
        "english": english_stemmer,
    }

    def __init__(self, language):
        self._stemmer = self._LANGUAGES.get(language, self.NULL)

    def __call__(self, word):
        return self._stemmer(word)
