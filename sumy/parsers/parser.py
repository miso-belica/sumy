# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals


class DocumentParser(object):
    """Abstract parser of input format into DOM."""

    SIGNIFICANT_WORDS = (
        "významný",
        "vynikající",
        "podstatný",
        "význačný",
        "důležitý",
        "slavný",
        "zajímavý",
        "eminentní",
        "vlivný",
        "supr",
        "super",
        "nejlepší",
        "dobrý",
        "kvalitní",
        "optimální",
        "relevantní",
    )
    STIGMA_WORDS = (
        "nejhorší",
        "zlý",
        "šeredný",
    )

    def __init__(self, tokenizer):
        self._tokenizer = tokenizer

    def tokenize_sentences(self, paragraph):
        return [s for s in self._tokenizer.to_sentences(paragraph) if s.strip()]

    def tokenize_words(self, sentence):
        return self._tokenizer.to_words(sentence)
