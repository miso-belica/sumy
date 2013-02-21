# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from collections import Counter
from operator import attrgetter
from itertools import chain
from ._utils import null_stemmer
from ._method import AbstractSummarizationMethod

try:
    from itertools import ifilterfalse as ffilter
except ImportError:
    from itertools import filterfalse as ffilter


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

    def key_method(self, sentences_count, weight=0.5):
        self.__check_bonus_words()

        words = map(self.stem_word, self._document.words)
        words = filter(self._is_bonus_word, words)
        word_counts = Counter(self.stem_word(w) for w in words)
        word_frequencies = word_counts.values()
        max_word_frequency = 1 if not word_frequencies else max(word_frequencies)
        significant_words = tuple(w for w, c in word_counts.items()
            if c/max_word_frequency > weight)

        sentences = []
        for sentence in self._document.sentences:
            rating = self._rate_sentence_by_key_method(sentence, significant_words)
            sentences.append((sentence, rating,))

        return self._get_best_sentences(sentences, sentences_count)

    def _is_bonus_word(self, word):
        return word in self._bonus_words

    def _rate_sentence_by_key_method(self, sentence, significant_words):
        words = map(self.stem_word, sentence.words)
        return sum(w in significant_words for w in words)

    def title_method(self, sentences_count):
        self.__check_null_words()

        headings, sentences = self._split_sentences(self._document.sentences)

        significant_words = chain(*map(attrgetter("words"), headings))
        significant_words = map(self.stem_word, significant_words)
        significant_words = ffilter(self._is_null_word, significant_words)
        significant_words = frozenset(significant_words)

        rated_sentences = []
        for sentence in sentences:
            rating = self._rate_sentence_by_title_method(sentence, significant_words)
            rated_sentences.append((sentence, rating,))

        return self._get_best_sentences(rated_sentences, sentences_count)

    def _split_sentences(self, sentences):
        headings = []
        common_sentences = []

        for sentence in sentences:
            if sentence.is_heading:
                headings.append(sentence)
            else:
                common_sentences.append(sentence)

        return tuple(headings), tuple(common_sentences)

    def _is_null_word(self, word):
        return word in self._null_words

    def _rate_sentence_by_title_method(self, sentence, significant_words):
        words = map(self.stem_word, sentence.words)
        return sum(w in significant_words for w in words)

    def location_method(self, sentences_count, w_h=1, w_p1=1, w_p2=1, w_s1=1, w_s2=1):
        self.__check_null_words()

        headings = filter(attrgetter("is_heading"), self._document.sentences)
        significant_words = chain(*map(attrgetter("words"), headings))
        significant_words = map(self.stem_word, significant_words)
        significant_words = ffilter(self._is_null_word, significant_words)
        significant_words = frozenset(significant_words)

        rated_sentences = []
        paragraphs = self._document.paragraphs
        for paragraph_order, paragraph in enumerate(paragraphs):
            sentences = tuple(ffilter(attrgetter("is_heading"), paragraph.sentences))
            for sentence_order, sentence in enumerate(sentences):
                rating = self._rate_sentence_by_location_method(sentence,
                    significant_words)
                rating *= w_h

                if paragraph_order == 0:
                    rating += w_p1
                elif paragraph_order == len(paragraphs) - 1:
                    rating += w_p2

                if sentence_order == 0:
                    rating += w_s1
                elif sentence_order == len(sentences) - 1:
                    rating += w_s2

                rated_sentences.append((sentence, rating,))

        return self._get_best_sentences(rated_sentences, sentences_count)

    def _rate_sentence_by_location_method(self, sentence, significant_words):
        words = map(self.stem_word, sentence.words)
        return sum(w in significant_words for w in words)

    def __check_bonus_words(self):
        if not self._bonus_words:
            raise ValueError("Set of bonus words is empty. Please set attribute 'bonus_words' with collection of words.")

    def __check_stigma_words(self):
        if not self._stigma_words:
            raise ValueError("Set of stigma words is empty. Please set attribute 'stigma_words' with collection of words.")

    def __check_null_words(self):
        if not self._null_words:
            raise ValueError("Set of null words is empty. Please set attribute 'null_words' with collection of words.")
