

import math

try:
    import numpy
except ImportError:
    numpy = None

from ._summarizer import AbstractSummarizer


class KLSummarizer(AbstractSummarizer):
    """
    Method that greedily adds sentences to a summary so long as it decreases the
    KL Divergence.
    Source: http://www.aclweb.org/anthology/N09-1041
    """

    stop_words = frozenset()

    def __call__(self, document, sentences_count):
        self._ensure_dependencies_installed()

        sentences = document.sentences
        ratings = self._compute_ratings(sentences)

        return self._get_best_sentences(sentences, sentences_count, ratings)

    @staticmethod
    def _ensure_dependencies_installed():
        if numpy is None:
            raise ValueError("KL summarizer requires NumPy. Please, install it by command 'pip install numpy'.")

    @staticmethod
    def _get_all_words_in_doc(sentences):
        return [w for s in sentences for w in s.words]

    def _get_content_words_in_sentence(self, sentence):
        return self._get_content_words(sentence.words)

    def _normalize_words(self, words):
        return [self.normalize_word(w) for w in words]

    def _filter_out_stop_words(self, words):
        return [w for w in words if w not in self.stop_words]

    @staticmethod
    def _compute_word_freq(list_of_words):
        word_freq = {}
        for w in list_of_words:
            word_freq[w] = word_freq.get(w, 0) + 1
        return word_freq

    def _get_all_content_words_in_doc(self, sentences):
        all_words = self._get_all_words_in_doc(sentences)
        return self._get_content_words(all_words)

    def _get_content_words(self, words):
        normalized_words = self._normalize_words(words)
        normalized_content_words = self._filter_out_stop_words(normalized_words)
        return normalized_content_words

    def compute_tf(self, sentences):
        """
        Computes the normalized term frequency as explained in http://www.tfidf.com/

        :type sentences: [sumy.models.dom.Sentence]
        """
        content_words = self._get_all_content_words_in_doc(sentences)
        content_words_count = len(content_words)
        content_words_freq = self._compute_word_freq(content_words)
        content_word_tf = {w: f / content_words_count for w, f in content_words_freq.items()}
        return content_word_tf

    def _joint_freq(self, word_freq_1, word_freq_2, total_len):
        """
        Frequency of the words of two word lists merged together.

        :param word_freq_1: word counts of the first word list
        :param word_freq_2: word counts of the second word list
        :param total_len: combined length of both word lists
        """
        # copying the bigger table and adding the smaller one into it keeps the
        # word by word work proportional to the smaller of the two
        if len(word_freq_1) > len(word_freq_2):
            joint = self._add_word_freq(word_freq_1.copy(), word_freq_2)
        else:
            joint = self._add_word_freq(word_freq_2.copy(), word_freq_1)

        # divides total counts by the combined length
        return {word: count / total_len for word, count in joint.items()}

    @staticmethod
    def _add_word_freq(word_freq, added_word_freq):
        """Adds the counts of the second table into the first one, which is modified."""
        for word, count in added_word_freq.items():
            word_freq[word] = word_freq.get(word, 0) + count

        return word_freq

    @staticmethod
    def _kl_divergence(summary_freq, doc_freq):
        """
        Note: Could import scipy.stats and use scipy.stats.entropy(doc_freq, summary_freq)
        but this gives equivalent value without the import
        """
        sum_val = 0
        for w in summary_freq:
            frequency = doc_freq.get(w)
            if frequency:  # missing or zero = no frequency
                sum_val += frequency * math.log(frequency / summary_freq[w])

        return sum_val

    @staticmethod
    def _find_index_of_best_sentence(kls):
        """
        the best sentence is the one with the smallest kl_divergence
        """
        return kls.index(min(kls))

    def _compute_ratings(self, sentences):
        word_freq = self.compute_tf(sentences)
        ratings = {}

        # make it a list so that it can be modified
        sentences_list = list(sentences)

        # get all content words once for efficiency
        sentences_as_words = [self._get_content_words_in_sentence(s) for s in sentences]

        # the words of a sentence never change, so count them just once as well
        sentences_as_freq = [self._compute_word_freq(words) for words in sentences_as_words]
        sentences_lengths = [len(words) for words in sentences_as_words]

        # the summary is empty at the start and grows by one sentence per iteration
        summary_freq = {}
        summary_len = 0

        # Removes one sentence per iteration by adding to summary
        while len(sentences_list) > 0:
            # will store all the kls values for this pass
            kls = []

            for sentence_len, sentence_freq in zip(sentences_lengths, sentences_as_freq):
                # calculates the joint frequency through combining the word counts
                joint_freq = self._joint_freq(sentence_freq, summary_freq, sentence_len + summary_len)

                # adds the calculated kl divergence to the list in index = sentence used
                kls.append(self._kl_divergence(joint_freq, word_freq))

            # to consider and then add it into the summary
            index_to_remove = self._find_index_of_best_sentence(kls)
            best_sentence = sentences_list.pop(index_to_remove)
            summary_len += sentences_lengths.pop(index_to_remove)
            self._add_word_freq(summary_freq, sentences_as_freq.pop(index_to_remove))

            # value is the iteration in which it was removed multiplied by -1 so that
            # the first sentences removed (the most important) have highest values
            ratings[best_sentence] = -1 * len(ratings)

        return ratings
