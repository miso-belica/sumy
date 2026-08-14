

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

    @staticmethod
    def _compute_word_freq_array(words, word_to_index):
        """Counts of the given words, in an array indexed by the document's vocabulary."""
        word_freq = numpy.zeros(len(word_to_index))
        for w in words:
            word_freq[word_to_index[w]] += 1

        return word_freq

    @staticmethod
    def _joint_freq(word_freq_1, word_freq_2, total_len):
        """
        Frequency of the words of two word lists merged together.

        :param word_freq_1: word counts of the first word list
        :param word_freq_2: word counts of the second word list
        :param total_len: combined length of both word lists
        """
        # a zero length means that both word lists are empty, and so are their counts,
        # so the divisor only has to stay away from zero to keep every frequency zero
        return (word_freq_1 + word_freq_2) / numpy.maximum(total_len, 1)

    @staticmethod
    def _kl_divergence(summary_freq, doc_freq):
        """
        Note: Could import scipy.stats and use scipy.stats.entropy(doc_freq, summary_freq)
        but this gives equivalent value without the import
        """
        # a word that either side does not have has no frequency to compare, and
        # log(1/1) adds nothing, so give both sides a frequency of one there
        common_words = (doc_freq > 0) & (summary_freq > 0)
        doc_freq = numpy.where(common_words, doc_freq, 1.0)
        summary_freq = numpy.where(common_words, summary_freq, 1.0)

        # the last axis holds the words, so a table of sentences keeps one value per row
        return (doc_freq * numpy.log(doc_freq / summary_freq)).sum(axis=-1)

    @staticmethod
    def _find_index_of_best_sentence(kls):
        """
        the best sentence is the one with the smallest kl_divergence
        """
        return kls.argmin()

    def _compute_ratings(self, sentences):
        word_freq = self.compute_tf(sentences)
        ratings = {}

        # every content word of a sentence is a content word of the document, so the
        # document's vocabulary gives all of them a place in the count arrays below
        word_to_index = {word: index for index, word in enumerate(word_freq)}
        doc_freq = numpy.fromiter(word_freq.values(), dtype=float, count=len(word_freq))

        # make it a list so that a sentence can be looked up by its position
        sentences_list = list(sentences)

        # get all content words once for efficiency
        sentences_as_words = [self._get_content_words_in_sentence(s) for s in sentences]

        # the words of a sentence never change, so count them just once as well, into one
        # row of the table of counts
        sentences_as_freq = numpy.zeros((len(sentences_list), len(word_to_index)))
        for row, words in enumerate(sentences_as_words):
            sentences_as_freq[row] = self._compute_word_freq_array(words, word_to_index)

        sentences_lengths = numpy.array([len(words) for words in sentences_as_words])

        # the summary is empty at the start and grows by one sentence per iteration
        summary_freq = numpy.zeros(len(word_to_index))
        summary_len = 0

        # the sentences that are not in the summary yet, in the order of the document
        candidates = numpy.arange(len(sentences_list))

        # Removes one sentence per iteration by adding to summary
        while len(candidates) > 0:
            # calculates the joint frequency of every candidate with the summary at once
            joint_freq = self._joint_freq(
                sentences_as_freq[candidates],
                summary_freq,
                (sentences_lengths[candidates] + summary_len).reshape(-1, 1),
            )

            # one kl divergence per candidate, in the same order
            kls = self._kl_divergence(joint_freq, doc_freq)

            # to consider and then add it into the summary
            index_to_remove = self._find_index_of_best_sentence(kls)
            best = candidates[index_to_remove]
            best_sentence = sentences_list[best]
            summary_len += sentences_lengths[best]
            summary_freq += sentences_as_freq[best]
            candidates = numpy.delete(candidates, index_to_remove)

            # value is the iteration in which it was removed multiplied by -1 so that
            # the first sentences removed (the most important) have highest values
            ratings[best_sentence] = -1 * len(ratings)

        return ratings
