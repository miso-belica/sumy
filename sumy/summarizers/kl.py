# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals
import math

from ._summarizer import AbstractSummarizer
from ..utils import get_stop_words


class KLSummarizer(AbstractSummarizer):
    """
    Method that greedily adds sentences to a summary so long as it decreases the 
    KL Divergence.
    Source: http://www.aclweb.org/anthology/N09-1041
    """

    def __call__(self, document, sentences_count):
        ratings = self._get_ratings(document)
        return self._get_best_sentences(document.sentences, sentences_count, ratings)

    def _get_ratings(self, document):
        sentences = document.sentences

        ratings = self._compute_ratings(sentences)
        return ratings

    def _get_all_words_in_doc(self, sentences):
        return [w for s in sentences for w in s.words]

    def _get_content_words_in_sentence(self, sentence):
        normalized_words = self._normalize_words(sentence.words)   
        normalized_content_words = self._filter_out_stop_words(normalized_words)
        return normalized_content_words

    def _normalize_words(self, words):
        return [self.normalize_word(w) for w in words]

    def _filter_out_stop_words(self, words):
        return [w for w in words if w not in self.stop_words]

    def _compute_word_freq(self, list_of_words):
        word_freq = {}
        for w in list_of_words:
            word_freq[w] = word_freq.get(w, 0) + 1
        return word_freq

    def _get_all_content_words_in_doc(self, sentences):
        all_words = self._get_all_words_in_doc(sentences)
        content_words = self._filter_out_stop_words(all_words)
        normalized_content_words = self._normalize_words(content_words)
        return normalized_content_words
        
    def _compute_tf(self, sentences):
        '''
        Computes the normalized term frequency as explained in http://www.tfidf.com/
        '''
        content_words = self._get_all_content_words_in_doc(sentences)
        content_words_count = len(content_words)
        content_words_freq = self._compute_word_freq(content_words)
        content_word_tf = dict((k, v / content_words_count) for (k, v) in content_words_freq.items())
        return content_word_tf

    def _joint_freq(self, word_list_1, word_list_2):
        # combined length of the word lists
        total_len = len(word_list_1) + len(word_list_2)

        # word frequencies within each list
        wc1 = self._compute_word_freq(word_list_1)
        wc2 = self._compute_word_freq(word_list_2)

        # inputs the counts from the first list
        joint = wc1.copy()

        # adds in the counts of the second list
        for k in wc2:
            if k in joint: 
                joint[k] += wc2[k]
            else: joint[k] = wc2[k]

        # divides total counts by the combined length
        for k in joint:
            joint[k] /= float(total_len)

        return joint

    def _kl_divergence(self, summary_freq, doc_freq):
        '''
        Note: Could import scipy.stats and use scipy.stats.entropy(doc_freq, summary_freq)
        but this gives equivalent value without the import
        '''
        sum_val = 0
        for w in summary_freq:
            sum_val += doc_freq[w] * math.log(doc_freq[w] / summary_freq[w])
        return sum_val

    def _find_index_of_best_sentence(self, kls):
        '''
        the best sentence is the one with the smallest kl_divergence
        '''
        indexToRemove = kls.index(min(kls))
        return indexToRemove

    def _compute_ratings(self, sentences):
        word_freq = self._compute_tf(sentences)
        ratings = {}
        summary = []

        # make it a list so that it can be modified
        sentences_list = list(sentences)

        # get all content words once for efficiency
        sentences_as_words = [self._get_content_words_in_sentence(s) for s in sentences]
        
        # Removes one sentence per iteration by adding to summary
        while len(sentences_list) > 0:
            # will store all the kls values for this pass
            kls = []
            
            # converts summary to word list
            summary_as_word_list = self._get_all_words_in_doc(summary)
            
            for s in sentences_as_words:
                # calculates the joint frequency through combining the word lists
                joint_freq = self._joint_freq(s, summary_as_word_list)

                # adds the calculated kl divergence to the list in index = sentence used
                kls.append(self._kl_divergence(joint_freq, word_freq))

            # to consider and then add it into the summary
            indexToRemove = self._find_index_of_best_sentence(kls)
            best_sentence = sentences_list.pop(indexToRemove)
            del sentences_as_words[indexToRemove]
            summary.append(best_sentence)

            # value is the iteration in which it was removed multiplied by -1 so that the first sentences removed (the most important) have highest values
            ratings[best_sentence] =  -1 * len(ratings)

        return ratings

