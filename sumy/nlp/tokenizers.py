# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

import re
import nltk

from os import path
from ..utils import expand_resource_path
from .._compat import to_string, to_unicode, unicode


class Tokenizer(object):
    """Language dependent tokenizer of text document."""

    _WORD_PATTERN = re.compile(r"^[^\W\d_]+$", re.UNICODE)

    def __init__(self, language):
        self._language = language
        self._sentence_tokenizer = self._sentence_tokenizer(language)

    @property
    def language(self):
        return self._language

    def _sentence_tokenizer(self, language):
        file_path = expand_resource_path("tokenizers/%s.pickle" % language)
        if not path.exists(file_path):
            raise ValueError("Sentence tokenizer for language '%s' not available." % language)

        return nltk.data.load(to_string("file:") + file_path)

    def to_sentences(self, paragraph):
        sentences = self._sentence_tokenizer.tokenize(to_unicode(paragraph))
        return tuple(map(unicode.strip, sentences))

    def to_words(self, sentence):
        words = nltk.word_tokenize(to_unicode(sentence))
        return tuple(filter(self._is_word, words))

    def _is_word(self, word):
        return bool(Tokenizer._WORD_PATTERN.search(word))
