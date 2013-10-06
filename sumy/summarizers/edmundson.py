# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from collections import defaultdict
from ..nlp.stemmers import null_stemmer
from ._summarizer import AbstractSummarizer
from .edmundson_cue import EdmundsonCueMethod
from .edmundson_key import EdmundsonKeyMethod
from .edmundson_title import EdmundsonTitleMethod
from .edmundson_location import EdmundsonLocationMethod


_EMPTY_SET = frozenset()


class EdmundsonSummarizer(AbstractSummarizer):
    _bonus_words = _EMPTY_SET
    _stigma_words = _EMPTY_SET
    _null_words = _EMPTY_SET

    def __init__(self, stemmer=null_stemmer, cue_weight=1.0, key_weight=0.0,
            title_weight=1.0, location_weight=1.0):
        super(EdmundsonSummarizer, self).__init__(stemmer)

        self._ensure_correct_weights(cue_weight, key_weight, title_weight,
            location_weight)

        self._cue_weight = float(cue_weight)
        self._key_weight = float(key_weight)
        self._title_weight = float(title_weight)
        self._location_weight = float(location_weight)

    def _ensure_correct_weights(self, *weights):
        for w in weights:
            if w < 0.0:
                raise ValueError("Negative wights are not allowed.")

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

    def __call__(self, document, sentences_count):
        ratings = defaultdict(int)

        if self._cue_weight > 0.0:
            method = self._build_cue_method_instance()
            ratings = self._update_ratings(ratings, method.rate_sentences(document))
        if self._key_weight > 0.0:
            method = self._build_key_method_instance()
            ratings = self._update_ratings(ratings, method.rate_sentences(document))
        if self._title_weight > 0.0:
            method = self._build_title_method_instance()
            ratings = self._update_ratings(ratings, method.rate_sentences(document))
        if self._location_weight > 0.0:
            method = self._build_location_method_instance()
            ratings = self._update_ratings(ratings, method.rate_sentences(document))

        return self._get_best_sentences(document.sentences, sentences_count, ratings)

    def _update_ratings(self, ratings, new_ratings):
        assert len(ratings) == 0 or len(ratings) == len(new_ratings)

        for sentence, rating in new_ratings.items():
            ratings[sentence] += rating

        return ratings

    def cue_method(self, document, sentences_count, bunus_word_value=1, stigma_word_value=1):
        summarization_method = self._build_cue_method_instance()
        return summarization_method(document, sentences_count, bunus_word_value,
            stigma_word_value)

    def _build_cue_method_instance(self):
        self.__check_bonus_words()
        self.__check_stigma_words()

        return EdmundsonCueMethod(self._stemmer, self._bonus_words, self._stigma_words)

    def key_method(self, document, sentences_count, weight=0.5):
        summarization_method = self._build_key_method_instance()
        return summarization_method(document, sentences_count, weight)

    def _build_key_method_instance(self):
        self.__check_bonus_words()

        return  EdmundsonKeyMethod(self._stemmer, self._bonus_words)

    def title_method(self, document, sentences_count):
        summarization_method = self._build_title_method_instance()
        return summarization_method(document, sentences_count)

    def _build_title_method_instance(self):
        self.__check_null_words()

        return EdmundsonTitleMethod(self._stemmer, self._null_words)

    def location_method(self, document, sentences_count, w_h=1, w_p1=1, w_p2=1, w_s1=1, w_s2=1):
        summarization_method = self._build_location_method_instance()
        return summarization_method(document, sentences_count, w_h, w_p1, w_p2, w_s1, w_s2)

    def _build_location_method_instance(self):
        self.__check_null_words()

        return EdmundsonLocationMethod(self._stemmer, self._null_words)

    def __check_bonus_words(self):
        if not self._bonus_words:
            raise ValueError("Set of bonus words is empty. Please set attribute 'bonus_words' with collection of words.")

    def __check_stigma_words(self):
        if not self._stigma_words:
            raise ValueError("Set of stigma words is empty. Please set attribute 'stigma_words' with collection of words.")

    def __check_null_words(self):
        if not self._null_words:
            raise ValueError("Set of null words is empty. Please set attribute 'null_words' with collection of words.")
