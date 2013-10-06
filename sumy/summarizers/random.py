# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

import random

from ._summarizer import AbstractSummarizer


class RandomSummarizer(AbstractSummarizer):
    """Summarizer that picks sentences randomly."""

    def __call__(self, document, sentences_count):
        sentences = document.sentences
        ratings = self._get_random_ratings(sentences)

        return self._get_best_sentences(sentences, sentences_count, ratings)

    def _get_random_ratings(self, sentences):
        ratings = list(range(len(sentences)))
        random.shuffle(ratings)

        return dict((s, r) for s, r in zip(sentences, ratings))
