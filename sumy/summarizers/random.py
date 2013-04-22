# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

import random

from ._summarizer import AbstractSummarizer


class RandomSummarizer(AbstractSummarizer):
    """Summarizer that picks sentences randomly."""

    def __call__(self, sentences_count):
        ratings = self._get_random_ratings(self._document.sentences)
        return self._get_best_sentences(self._document.sentences,
            sentences_count, self.rate_sentence, ratings)

    def _get_random_ratings(self, sentences):
        ratings = list(range(len(sentences)))
        random.shuffle(ratings)

        return dict((s, r) for s, r in zip(sentences, ratings))

    def rate_sentence(self, sentence, ratings):
        return ratings[sentence]
