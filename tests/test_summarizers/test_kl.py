# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

import unittest
import scipy.stats

from sumy.models.dom._sentence import Sentence
from sumy.summarizers.kl import KLSummarizer
from sumy._compat import to_unicode
from ..utils import build_document, build_document_from_string
from sumy.nlp.tokenizers import Tokenizer


class TestKL(unittest.TestCase):
    EMPTY_STOP_WORDS = []
    COMMON_STOP_WORDS = ["the", "and", "i"]

    def _build_summarizer(self, stop_words):
        summarizer = KLSummarizer()
        summarizer.stop_words = stop_words
        return summarizer

    def test_empty_document(self):
        document = build_document()
        summarizer = self._build_summarizer(self.EMPTY_STOP_WORDS)

        returned = summarizer(document, 10)
        self.assertEqual(len(returned), 0)

    def test_single_sentence(self):

        s = Sentence("I am one slightly longer sentence.", Tokenizer("english"))
        document = build_document([s])
        summarizer = self._build_summarizer(self.EMPTY_STOP_WORDS)

        returned = summarizer(document, 10)
        self.assertEqual(len(returned), 1)

    def test_compute_word_freq(self):
        
        summarizer = self._build_summarizer(self.EMPTY_STOP_WORDS)
        
        words = ["one", "two", "three", "four"]
        freq = summarizer._compute_word_freq(words)
        self.assertEqual(freq.get("one", 0), 1)
        self.assertEqual(freq.get("two", 0), 1)
        self.assertEqual(freq.get("three", 0), 1)
        self.assertEqual(freq.get("four", 0), 1)
        
        words = ["one", "one", "two", "two"]
        freq = summarizer._compute_word_freq(words)
        self.assertEqual(freq.get("one", 0), 2)
        self.assertEqual(freq.get("two", 0), 2)
        self.assertEqual(freq.get("three", 0), 0)

    def test_joint_freq(self):
        summarizer = self._build_summarizer(self.EMPTY_STOP_WORDS)
        w1 = ["one", "two", "three", "four"]
        w2 = ["one", "two", "three", "four"]
        freq = summarizer._joint_freq(w1, w2)
        self.assertEqual(freq["one"], 1.0/4)
        self.assertEqual(freq["two"], 1.0/4)
        self.assertEqual(freq["three"], 1.0/4)
        self.assertEqual(freq["four"], 1.0/4)

        w1 = ["one", "two", "three", "four"]
        w2 = ["one", "one", "three", "five"]
        freq = summarizer._joint_freq(w1, w2)
        self.assertEqual(freq["one"], 3.0/8)
        self.assertEqual(freq["two"], 1.0/8)
        self.assertEqual(freq["three"], 1.0/4)
        self.assertEqual(freq["four"], 1.0/8)
        self.assertEqual(freq["five"], 1.0/8)

    def test_kl_divergence(self):
        summarizer = self._build_summarizer(self.EMPTY_STOP_WORDS)
        EPS = 0.00001


        w1 = {"one":.35, "two":.5, "three":.15}
        w2 = {"one":1.0/3.0, "two":1.0/3.0, "three":1.0/3.0}

        w1_ = [.35, .5, .15]
        w2_ = [1.0/3.0, 1.0/3.0, 1.0/3.0]

        # This value comes from scipy.stats.entropy(w2_, w1_)
        # Note: the order of params is different
        kl_correct = 0.11475080798005841
        self.assertTrue(abs(summarizer._kl_divergence(w1, w2) - kl_correct < EPS))

        w1 = {"one":.1, "two":.2, "three":.7}
        w2 = {"one":.2, "two":.4, "three":.4}

        w1_ = [.1, .2, .7]
        w2_ = [.2, .4, .4]
        
        # This value comes from scipy.stats.entropy(w2_, w1_)
        # Note: the order of params is different
        kl_correct = 0.1920419931617981
        self.assertTrue(abs(summarizer._kl_divergence(w1, w2) - kl_correct) < EPS)


