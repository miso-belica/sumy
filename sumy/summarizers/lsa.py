# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

import math

from warnings import warn

try:
    import numpy
except ImportError:
    numpy = None

try:
    from numpy.linalg import svd as singular_value_decomposition
except ImportError:
    singular_value_decomposition = None
from ._summarizer import AbstractSummarizer


class LsaSummarizer(AbstractSummarizer):
    MIN_DIMENSIONS = 3
    REDUCTION_RATIO = 1/1
    _stop_words = frozenset()

    @property
    def stop_words(self):
        return self._stop_words

    @stop_words.setter
    def stop_words(self, words):
        self._stop_words = frozenset(map(self.normalize_word, words))

    def __call__(self, document, sentences_count):
        self._ensure_dependecies_installed()

        dictionary = self._create_dictionary(document)
        # empty document
        if not dictionary:
            return ()

        matrix = self._create_matrix(document, dictionary)
        matrix = self._compute_term_frequency(matrix)
        u, sigma, v = singular_value_decomposition(matrix, full_matrices=False)

        ranks = iter(self._compute_ranks(sigma, v))
        return self._get_best_sentences(document.sentences, sentences_count,
            lambda s: next(ranks))

    def _ensure_dependecies_installed(self):
        if numpy is None:
            raise ValueError("LSA summarizer requires NumPy. Please, install it by command 'pip install numpy'.")

    def _create_dictionary(self, document):
        """Creates mapping key = word, value = row index"""
        words = map(self.normalize_word, document.words)
        unique_words = frozenset(self.stem_word(w) for w in words if w not in self._stop_words)

        return dict((w, i) for i, w in enumerate(unique_words))

    def _create_matrix(self, document, dictionary):
        """
        Creates matrix of shape |unique words|×|sentences| where cells
        contains number of occurrences of words (rows) in sentences (cols).
        """
        sentences = document.sentences

        words_count = len(dictionary)
        sentences_count = len(sentences)
        if words_count < sentences_count:
            message = (
                "Number of words (%d) is lower than number of sentences (%d). "
                "LSA algorithm may not work properly."
            )
            warn(message % (words_count, sentences_count))

        # create matrix |unique words|×|sentences| filled with zeroes
        matrix = numpy.zeros((words_count, sentences_count))
        for col, sentence in enumerate(sentences):
            for word in map(self.stem_word, sentence.words):
                # only valid words is counted (not stop-words, ...)
                if word in dictionary:
                    row = dictionary[word]
                    matrix[row, col] += 1

        return matrix

    def _compute_term_frequency(self, matrix, smooth=0.4):
        """
        Computes TF metrics for each sentence (column) in the given matrix.
        You can read more about smoothing parameter at URL below:
        http://nlp.stanford.edu/IR-book/html/htmledition/maximum-tf-normalization-1.html
        """
        assert 0.0 <= smooth < 1.0

        max_word_frequencies = numpy.max(matrix, axis=0)
        rows, cols = matrix.shape
        for row in range(rows):
            for col in range(cols):
                max_word_frequency = max_word_frequencies[col]
                if max_word_frequency != 0:
                    frequency = matrix[row, col]/max_word_frequency
                    matrix[row, col] = smooth + (1.0 - smooth)*frequency

        return matrix

    def _compute_ranks(self, sigma, v_matrix):
        assert len(sigma) == v_matrix.shape[0], "Matrices should be multiplicable"

        dimensions = max(LsaSummarizer.MIN_DIMENSIONS,
            int(len(sigma)*LsaSummarizer.REDUCTION_RATIO))
        powered_sigma = tuple(s**2 if i < dimensions else 0.0
            for i, s in enumerate(sigma))

        ranks = []
        # iterate over columns of matrix (rows of transposed matrix)
        for column_vector in v_matrix.T:
            rank = sum(s*v**2 for s, v in zip(powered_sigma, column_vector))
            ranks.append(math.sqrt(rank))

        return ranks
