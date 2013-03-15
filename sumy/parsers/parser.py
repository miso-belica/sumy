# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

import nltk

from ..utils import expand_resource_path, cached_property
from .._py3k import to_string


class DocumentParser(object):
    """Abstract parser of input format into DOM."""

    def __init__(self, language):
        self._language = language

    @property
    def language(self):
        return self._language

    @cached_property
    def _sentence_tokenizer(self):
        path = expand_resource_path("tokenizers/%s.pickle" % self._language)
        return nltk.data.load(to_string("file:") + path)

    def tokenize_sentences(self, paragraph):
        return self._sentence_tokenizer.tokenize(paragraph)

    def tokenize_words(self, sentence):
        return nltk.word_tokenize(sentence)
