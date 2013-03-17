# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from case import unittest
from sumy.tokenizers import Tokenizer
from sumy.models import TfDocumentModel


class TestTfModel(unittest.TestCase):
    def test_magnitude(self):
        tokenizer = Tokenizer("english")
        text = "w1 w2 w3 w4"
        model = TfDocumentModel(text, tokenizer)

        self.assertAlmostEqual(model.magnitude, 2.0)

    def test_terms(self):
        tokenizer = Tokenizer("english")
        text = "w1 w2 w3 w4 w2 w4 w5"
        model = TfDocumentModel(text, tokenizer)

        terms = tuple(sorted(model.terms))
        self.assertEqual(terms, ("w1", "w2", "w3", "w4", "w5"))

    def test_term_frequency(self):
        tokenizer = Tokenizer("english")
        text = "w1 w2 w3 w1 w1 w3 w4 w3w2"
        model = TfDocumentModel(text, tokenizer)

        self.assertEqual(model.term_frequency("w1"), 3)
        self.assertEqual(model.term_frequency("w2"), 1)
        self.assertEqual(model.term_frequency("w3"), 2)
        self.assertEqual(model.term_frequency("w4"), 1)
        self.assertEqual(model.term_frequency("w3w2"), 1)
        self.assertEqual(model.term_frequency("w5"), 0)
        self.assertEqual(model.term_frequency("missing"), 0)
