# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals


class DocumentParser(object):
    """Abstract parser of input format into DOM."""

    def __init__(self, tokenizer):
        self._tokenizer = tokenizer

    def tokenize_sentences(self, paragraph):
        return self._tokenizer.to_sentences(paragraph)

    def tokenize_words(self, sentence):
        return self._tokenizer.to_words(sentence)
