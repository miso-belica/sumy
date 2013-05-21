# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from ._summarizer import AbstractSummarizer


class EdmundsonCueMethod(AbstractSummarizer):
    def __init__(self, stemmer, bonus_words, stigma_words):
        super(EdmundsonCueMethod, self).__init__(stemmer)
        self._bonus_words = bonus_words
        self._stigma_words = stigma_words

    def __call__(self, document, sentences_count, bunus_word_weight, stigma_word_weight):
        return self._get_best_sentences(document.sentences,
            sentences_count, self._rate_sentence, bunus_word_weight,
            stigma_word_weight)

    def _rate_sentence(self, sentence, bunus_word_weight, stigma_word_weight):
        # count number of bonus/stigma words in sentece
        words = map(self.stem_word, sentence.words)
        bonus_words_count, stigma_words_count = self._count_words(words)

        # compute positive & negative rating
        bonus_rating = bonus_words_count*bunus_word_weight
        stigma_rating = stigma_words_count*stigma_word_weight

        # rating of sentence is (positive - negative) rating
        return bonus_rating - stigma_rating

    def _count_words(self, words):
        """
        Counts number of bonus/stigma words.

        :param iterable words:
            Collection of words.
        :returns pair:
            Tuple with number of words (bonus words, stigma words).
        """
        bonus_words_count = 0
        stigma_words_count = 0

        for word in words:
            if word in self._bonus_words:
                bonus_words_count +=1
            if word in self._stigma_words:
                stigma_words_count += 1

        return bonus_words_count, stigma_words_count

    def rate_sentences(self, document, bunus_word_weight=1, stigma_word_weight=1):
        rated_sentences = {}
        for sentence in document.sentences:
            rated_sentences[sentence] = self._rate_sentence(sentence,
                bunus_word_weight, stigma_word_weight)

        return rated_sentences
