# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from collections import Counter
from ._utils import null_stemmer
from ._method import AbstractSummarizationMethod


class LuhnMethod(AbstractSummarizationMethod):
    max_gap_size = 4
    significant_percentage = 1

    def __init__(self, document, stopwords=(), stemmer=null_stemmer):
        super(LuhnMethod, self).__init__(document, stemmer)
        self._stopwords = frozenset(stopwords)

    def __call__(self, sentences_count):
        words = self._get_significant_words(self._document.words)

        sentences = []
        for sentence in self._document.sentences:
            rating = self.rate_sentence(sentence, words)
            sentences.append((sentence, rating,))

        return self._get_best_sentences(sentences, sentences_count)

    def _get_significant_words(self, words):
        words = filter(self._is_stopword, words)
        words = tuple(self.stem_word(w) for w in words)

        # sort words by number of occurrences
        words = sorted((c, w) for w, c in Counter(words).items())

        # take only best `significant_percentage` % words
        best_words_count = int(len(words) * self.significant_percentage)
        return tuple(w for _, w in words)[:best_words_count]

    def _is_stopword(self, word):
        return not word.is_stopword(self._stopwords)

    def rate_sentence(self, sentence, significant_stems):
        ratings = self._get_chunk_ratings(sentence, significant_stems)
        return max(ratings) if ratings else 0

    def _get_chunk_ratings(self, sentence, significant_stems):
        chunks = []
        NONSIGNIFICANT_CHUNK = [0]*self.max_gap_size

        in_chunk = False
        for order, word in enumerate(sentence.words):
            stem = self.stem_word(word)
            # new chunk
            if stem in significant_stems and not in_chunk:
                in_chunk = True
                chunks.append([1])
            # append word to chunk
            elif in_chunk:
                is_significant_word = int(stem in significant_stems)
                chunks[-1].append(is_significant_word)

            # end of chunk
            if chunks and chunks[-1][-self.max_gap_size:] == NONSIGNIFICANT_CHUNK:
                in_chunk = False

        return tuple(map(self._get_chunk_rating, chunks))

    def _get_chunk_rating(self, chunk):
        chunk = self.__remove_trailing_zeros(chunk)
        words_count = len(chunk)
        assert words_count > 0

        significant_words = sum(chunk)
        if significant_words == 1:
            return 0
        else:
            return significant_words**2 / words_count

    def __remove_trailing_zeros(self, collection):
        collection = list(collection)
        while collection[-1] == 0:
            collection.pop()

        return collection
