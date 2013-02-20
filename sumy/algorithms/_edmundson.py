# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from ._utils import null_stemmer
from ._method import AbstractSummarizationMethod


_EMPTY_SET = frozenset()


class EdmundsonMethod(AbstractSummarizationMethod):
    _bonus_words = _EMPTY_SET
    _stigma_words = _EMPTY_SET
    _null_words = _EMPTY_SET

    def __init__(self, document, stemmer=null_stemmer):
        super(EdmundsonMethod, self).__init__(document, stemmer)

    @property
    def bonus_words(self):
        return self._bonus_words

    @bonus_words.setter
    def bonus_words(self, collection):
        self._bonus_words = frozenset(map(self.stem_word, collection))

    @property
    def stigma_words(self):
        return self._stigma_words

    @stigma_words.setter
    def stigma_words(self, collection):
        self._stigma_words = frozenset(map(self.stem_word, collection))

    @property
    def null_words(self):
        return self._null_words

    @null_words.setter
    def null_words(self, collection):
        self._null_words = frozenset(map(self.stem_word, collection))

    def __call__(self, sentences_count):
        return self._get_best_sentences((), sentences_count)

    def cue_method(self, sentences_count, bunus_word_value=1, stigma_word_value=1):
        self.__check_bonus_words()
        self.__check_stigma_words()

        sentences = []
        for sentence in self._document.sentences:
            rating = self._rate_sentence_by_cue_method(sentence,
                bunus_word_value, stigma_word_value)
            sentences.append((sentence, rating,))

        return self._get_best_sentences(sentences, sentences_count)

    def _rate_sentence_by_cue_method(self, sentence, bunus_word_value,
            stigma_word_value):
        words = tuple(map(self.stem_word, sentence.words))
        bonus_words_count = sum(w in self._bonus_words for w in words)
        stigma_words_count = sum(w in self._stigma_words for w in words)

        return bonus_words_count*bunus_word_value - stigma_words_count*stigma_word_value

    def __check_bonus_words(self):
        if not self._bonus_words:
            raise ValueError("Set of bonus words is empty. Please set attribute 'bonus_words' with collection of words.")

    def __check_stigma_words(self):
        if not self._stigma_words:
            raise ValueError("Set of stigma words is empty. Please set attribute 'stigma_words' with collection of words.")

    def __check_null_words(self):
        if not self._null_words:
            raise ValueError("Set of null words is empty. Please set attribute 'null_words' with collection of words.")
