# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

import nltk

from os import path
from .utils import expand_resource_path
from ._py3k import to_string


class Tokenizer(object):
    """Language dependent tokenizer of text document."""
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
        return self._sentence_tokenizer.tokenize(paragraph)

    def to_words(self, sentence):
        return nltk.word_tokenize(sentence)
