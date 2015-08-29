# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

import re
import nltk

from .._compat import to_string, to_unicode, unicode


class Tokenizer(object):
    """Language dependent tokenizer of text document."""

    _WORD_PATTERN = re.compile(r"^[^\W\d_]+$", re.UNICODE)
    # feel free to contribute if you have better tokenizer for any of these languages :)
    LANGUAGE_ALIASES = {
        "slovak": "czech",
    }
    
    # improve tokenizer by adding specific abbreviations it has issues with
    # note the final point in these items must not be included
    LANGUAGE_EXTRA_ABREVS = {
        "english": ["e.g", "al", "i.e"],
        "german": ["al", "z.B", "Inc", "engl", "z. B", "vgl", "lat", "bzw", "S"],
    }

    def __init__(self, language):
        self._language = language

        tokenizer_language = self.LANGUAGE_ALIASES.get(language, language)
        self._sentence_tokenizer = self._sentence_tokenizer(tokenizer_language)

    @property
    def language(self):
        return self._language

    def _sentence_tokenizer(self, language):
        path = to_string("tokenizers/punkt/%s.pickle") % to_string(language)
        return nltk.data.load(path)

    def to_sentences(self, paragraph):
        extra_abbreviations = self.LANGUAGE_EXTRA_ABREVS.get(self._language, [])
        self._sentence_tokenizer._params.abbrev_types.update(extra_abbreviations)
        sentences = self._sentence_tokenizer.tokenize(to_unicode(paragraph))
        return tuple(map(unicode.strip, sentences))

    def to_words(self, sentence):
        words = nltk.word_tokenize(to_unicode(sentence))
        return tuple(filter(self._is_word, words))

    def _is_word(self, word):
        return bool(Tokenizer._WORD_PATTERN.search(word))
