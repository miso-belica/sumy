# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

try:
    import numpy as np
except ImportError:
    numpy = None

from sumy.summarizers._summarizer import AbstractSummarizer


class KLSummarizer(AbstractSummarizer):
    """
    Method that greedily adds sentences to a summary so long as it decreases the
    KL Divergence.
    Source: http://www.aclweb.org/anthology/N09-1041
    """
    MISSING_WORD_VAL = 42.  # placeholder value used for missing words in document
    stop_words = frozenset()

    def __call__(self, document, sentences_count):
        self._ensure_dependencies_installed()

        sentences = document.sentences
        ratings = self._compute_ratings(sentences)

        return self._get_best_sentences(sentences, sentences_count, ratings)

    @staticmethod
    def _ensure_dependencies_installed():
        if np is None:
            raise ValueError("Fast KL-Sum summarizer requires NumPy."
                             "Please, install it by command 'pip install numpy'.")

    @staticmethod
    def _get_all_words_in_doc(sentences):
        return [w for s in sentences for w in s.words]

    def _get_content_words_in_sentence(self, sentence):
        normalized_words = self._normalize_words(sentence.words)
        normalized_content_words = self._filter_out_stop_words(normalized_words)
        return normalized_content_words

    def _normalize_words(self, words):
        return [self.normalize_word(w) for w in words]

    def _filter_out_stop_words(self, words):
        return [w for w in words if w not in self.stop_words]

    @staticmethod
    def _old_compute_word_freq(list_of_words, d=None):
        word_freq = {} if d is None else d
        for w in list_of_words:
            word_freq[w] = word_freq.get(w, 0) + 1
        return word_freq

    @staticmethod
    def _compute_word_freq(list_of_words, word_freq_arr, word_to_ind):
        for w in list_of_words:
            word_freq_arr[word_to_ind[w]] += 1
        return word_freq_arr

    def _get_all_content_words_in_doc(self, sentences):
        all_words = self._get_all_words_in_doc(sentences)
        normalized_words = self._normalize_words(all_words)
        normalized_content_words = self._filter_out_stop_words(normalized_words)
        return normalized_content_words

    def compute_tf(self, sentences):
        """
        Computes the normalized term frequency as explained in http://www.tfidf.com/

        :type sentences: [sumy.models.dom.Sentence]
        """
        content_words = self._get_all_content_words_in_doc(sentences)
        content_words_count = len(content_words)
        content_words_freq = self._old_compute_word_freq(content_words)
        content_word_tf = dict((w, f / content_words_count) for w, f in content_words_freq.items())
        return content_word_tf

    @staticmethod
    def _joint_freq(wc1, wc2, total_len):
        if total_len == 0:
            return np.zeros_like(wc1)
        joint_sum = wc1 + wc2
        return joint_sum / total_len

    @staticmethod
    def _kl_divergence(summary_freq, doc_freq, doc_missing_word_mask):
        summary_freq = np.where((summary_freq != 0.) & doc_missing_word_mask, summary_freq, doc_freq)
        return (doc_freq * np.log(doc_freq / summary_freq)).sum()

    @staticmethod
    def _find_index_of_best_sentence(kls):
        """
        the best sentence is the one with the smallest kl_divergence
        """
        return kls.index(min(kls))

    def _compute_ratings(self, sentences):
        word_to_freq = self.compute_tf(sentences)

        vocabulary = set(self._get_all_words_in_doc(sentences)).union(word_to_freq.keys())
        word_to_ind = {word: index for index, word in enumerate(vocabulary)}

        word_freq = np.repeat(self.MISSING_WORD_VAL, len(vocabulary))
        for k, v in word_to_freq.items():
            word_freq[word_to_ind[k]] = v
        missing_word_mask = word_freq != self.MISSING_WORD_VAL

        ratings = {}

        # Keep track of number of words in summary and word frequency
        summary_word_list_len = 0
        summary_word_freq = np.repeat(0., len(vocabulary))

        # make it a list so that it can be modified
        sentences_list = list(sentences)

        # get all content words once for efficiency
        sentences_as_words = [self._get_content_words_in_sentence(s) for s in sentences]

        # calculate all sentence lengths and word frequencies once for efficiency
        i_to_sent_word_freq = {}
        i_to_sent_len = {}
        for i, s in enumerate(sentences_as_words):
            sent_word_freq = np.zeros_like(word_freq)
            sent_word_freq = self._compute_word_freq(s, sent_word_freq, word_to_ind)
            i_to_sent_word_freq[i] = sent_word_freq
            i_to_sent_len[i] = len(s)

        iterations = 0
        indices = list(range(len(sentences_as_words)))
        # Removes one sentence per iteration by adding to summary
        while len(indices) > 0:
            iterations += 1
            # will store all the kls values for this pass
            kls = []

            for i in indices:
                # calculates the joint frequency
                joint_freq = self._joint_freq(i_to_sent_word_freq[i], summary_word_freq,
                                              i_to_sent_len[i] + summary_word_list_len)

                # adds the calculated kl divergence to the list in index = sentence used
                kls.append(self._kl_divergence(joint_freq, word_freq, missing_word_mask))

            # to consider and then add it into the summary
            index_to_remove = self._find_index_of_best_sentence(kls)
            best_sentence = sentences_list[indices[index_to_remove]]
            del indices[index_to_remove]
            best_sentence_word_list = self._get_all_words_in_doc([best_sentence])
            # update summary length and word frequencies
            summary_word_list_len += len(best_sentence_word_list)
            summary_word_freq = self._compute_word_freq(best_sentence_word_list, summary_word_freq, word_to_ind)

            # value is the iteration in which it was removed multiplied by -1 so that
            # the first sentences removed (the most important) have highest values
            ratings[best_sentence] = -1 * len(ratings)
        print(f"Num interations: {iterations}")
        return ratings
