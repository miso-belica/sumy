

import math

try:
    import numpy
except ImportError:
    numpy = None
from collections import Counter, defaultdict

from ._summarizer import AbstractSummarizer


class LexRankSummarizer(AbstractSummarizer):
    """
    LexRank: Graph-based Centrality as Salience in Text Summarization
    Source: http://tangra.si.umich.edu/~radev/lexrank/lexrank.pdf
    """
    threshold = 0.1
    epsilon = 0.1
    _stop_words = frozenset()

    @property
    def stop_words(self):
        return self._stop_words

    @stop_words.setter
    def stop_words(self, words):
        self._stop_words = frozenset(map(self.normalize_word, words))

    def __call__(self, document, sentences_count):
        self._ensure_dependencies_installed()

        sentences_words = [self._to_words_set(s) for s in document.sentences]
        if not sentences_words:
            return ()

        tf_metrics = self._compute_tf(sentences_words)
        idf_metrics = self._compute_idf(sentences_words)

        matrix = self._create_matrix(sentences_words, self.threshold, tf_metrics, idf_metrics)
        scores = self.power_method(matrix, self.epsilon)
        ratings = dict(zip(document.sentences, scores))

        return self._get_best_sentences(document.sentences, sentences_count, ratings)

    @staticmethod
    def _ensure_dependencies_installed():
        if numpy is None:
            raise ValueError("LexRank summarizer requires NumPy. Please, install it by command 'pip install numpy'.")

    def _to_words_set(self, sentence):
        words = map(self.normalize_word, sentence.words)
        return [self.stem_word(w) for w in words if w not in self._stop_words]

    def _compute_tf(self, sentences):
        tf_values = map(Counter, sentences)

        tf_metrics = []
        for sentence in tf_values:
            metrics = {}
            max_tf = self._find_tf_max(sentence)

            for term, tf in sentence.items():
                metrics[term] = tf / max_tf

            tf_metrics.append(metrics)

        return tf_metrics

    @staticmethod
    def _find_tf_max(terms):
        return max(terms.values()) if terms else 1

    @staticmethod
    def _compute_idf(sentences):
        sentences_count = len(sentences)
        # each sentence counts once per term, however often the term repeats in it
        document_frequencies = Counter(term for sentence in sentences for term in dict.fromkeys(sentence))

        return {term: math.log(sentences_count / n_j) for term, n_j in document_frequencies.items()}

    def _create_matrix(self, sentences, threshold, tf_metrics, idf_metrics):
        """
        Creates matrix of shape |sentences|×|sentences|.
        """
        # list the sentences of every term with the term's TF-IDF weight scaled to a unit length sentence,
        # skipping zero weights, so a sentence without weighted words keeps similarity 0 to every sentence
        sentences_of_term = defaultdict(lambda: ([], []))
        for row, tf in enumerate(tf_metrics):
            weights = {term: value * idf_metrics[term] for term, value in tf.items() if idf_metrics[term]}
            norm = math.sqrt(sum(weight * weight for weight in weights.values()))
            for term, weight in weights.items():
                rows, term_weights = sentences_of_term[term]
                rows.append(row)
                term_weights.append(weight / norm)

        # the cosine similarity of two sentences is the sum over their shared terms,
        # so every term adds to the pairs of its own sentences only
        matrix = numpy.zeros((len(sentences), len(sentences)))
        for rows, term_weights in sentences_of_term.values():
            term_weights = numpy.array(term_weights)
            matrix[numpy.ix_(rows, rows)] += numpy.outer(term_weights, term_weights)

        # threshold and normalize in place, so only one |sentences|×|sentences| matrix is ever allocated
        numpy.greater(matrix, threshold, out=matrix)
        degrees = matrix.sum(axis=1)
        degrees[degrees == 0] = 1
        matrix /= degrees[:, numpy.newaxis]

        return matrix

    @staticmethod
    def cosine_similarity(sentence1, sentence2, tf1, tf2, idf_metrics):
        """
        We compute idf-modified-cosine(sentence1, sentence2) here.
        It's cosine similarity of these two sentences (vectors) A, B computed as cos(x, y) = A . B / (|A| . |B|)
        Sentences are represented as vector TF*IDF metrics.

        :param sentence1:
            Iterable object where every item represents word of 1st sentence.
        :param sentence2:
            Iterable object where every item represents word of 2nd sentence.
        :type tf1: dict
        :param tf1:
            Term frequencies of words from 1st sentence.
        :type tf2: dict
        :param tf2:
            Term frequencies of words from 2nd sentence
        :type idf_metrics: dict
        :param idf_metrics:
            Inverted document metrics of the sentences. Every sentence is treated as document for this algorithm.
        :rtype: float
        :return:
            Returns -1.0 for opposite similarity, 1.0 for the same sentence and zero for no similarity between sentences.
        """
        unique_words1 = frozenset(sentence1)
        unique_words2 = frozenset(sentence2)
        common_words = unique_words1 & unique_words2

        numerator = 0.0
        for term in common_words:
            numerator += tf1[term]*tf2[term] * idf_metrics[term]**2

        denominator1 = sum((tf1[t]*idf_metrics[t])**2 for t in unique_words1)
        denominator2 = sum((tf2[t]*idf_metrics[t])**2 for t in unique_words2)

        if denominator1 > 0 and denominator2 > 0:
            return numerator / (math.sqrt(denominator1) * math.sqrt(denominator2))
        else:
            return 0.0

    @staticmethod
    def power_method(matrix, epsilon):
        transposed_matrix = matrix.T
        sentences_count = len(matrix)
        p_vector = numpy.array([1.0 / sentences_count] * sentences_count)
        lambda_val = 1.0

        while lambda_val > epsilon:
            next_p = numpy.dot(transposed_matrix, p_vector)
            norm = numpy.linalg.norm(next_p)
            if norm == 0:
                # all similarities are 0, e.g. every word is in every sentence so its IDF is 0
                return p_vector
            next_p /= norm
            lambda_val = numpy.linalg.norm(numpy.subtract(next_p, p_vector))
            p_vector = next_p

        return p_vector
