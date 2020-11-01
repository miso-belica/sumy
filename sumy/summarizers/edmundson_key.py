# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from collections import Counter
from ._summarizer import AbstractSummarizer


class EdmundsonKeyMethod(AbstractSummarizer):
    def __init__(self, stemmer, bonus_words):
        super(EdmundsonKeyMethod, self).__init__(stemmer)
        self._bonus_words = bonus_words

    def __call__(self, document, sentences_count, weight):
        significant_words = self._compute_significant_words(document, weight)

        return self._get_best_sentences(document.sentences,
            sentences_count, self._rate_sentence, significant_words)

    def _compute_significant_words(self, document, weight):
        # keep only stems contained in bonus words
        words = map(self.stem_word, document.words)
        words = filter(self._is_bonus_word, words)

        # compute frequencies of bonus words in document
        word_counts = Counter(words)
        word_frequencies = word_counts.values()

        # no frequencies means no significant words
        if not word_frequencies:
            return ()

        # return only words greater than weight
        max_word_frequency = max(word_frequencies)
        return tuple(word for word, frequency in word_counts.items()
            if frequency/max_word_frequency > weight)

    def _is_bonus_word(self, word):
        return word in self._bonus_words

    def _rate_sentence(self, sentence, significant_words):
        words = map(self.stem_word, sentence.words)
        return sum(w in significant_words for w in words)

    def rate_sentences(self, document, weight=0.5):
        significant_words = self._compute_significant_words(document, weight)

        rated_sentences = {}
        for sentence in document.sentences:
            rated_sentences[sentence] = self._rate_sentence(sentence,
                significant_words)

        return rated_sentences
