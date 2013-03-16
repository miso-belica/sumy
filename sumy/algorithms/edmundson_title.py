# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from operator import attrgetter
from itertools import chain
from .._compat import ffilter
from ._method import AbstractSummarizationMethod


class EdmundsonTitleMethod(AbstractSummarizationMethod):
    def __init__(self, document, stemmer, null_words):
        super(EdmundsonTitleMethod, self).__init__(document, stemmer)
        self._null_words = null_words

    def __call__(self, sentences_count):
        sentences = self._document.sentences
        significant_words = self._compute_significant_words()

        return self._get_best_sentences(sentences, sentences_count,
            self._rate_sentence, significant_words)

    def _compute_significant_words(self):
        heading_words = map(attrgetter("words"), self._document.headings)

        significant_words = chain(*heading_words)
        significant_words = map(self.stem_word, significant_words)
        significant_words = ffilter(self._is_null_word, significant_words)

        return frozenset(significant_words)

    def _is_null_word(self, word):
        return word in self._null_words

    def _rate_sentence(self, sentence, significant_words):
        words = map(self.stem_word, sentence.words)
        return sum(w in significant_words for w in words)

    def rate_sentences(self):
        significant_words = self._compute_significant_words()

        rated_sentences = {}
        for sentence in self._document.sentences:
            rated_sentences[sentence] = self._rate_sentence(sentence,
                significant_words)

        return rated_sentences
