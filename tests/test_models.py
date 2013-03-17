# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

import unittest

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

    def test_most_frequent_terms(self):
        tokenizer = Tokenizer("english")
        text = "w5 w4 w3 w2 w1 w5 W4 w3 w2 w5 w4 W5 w3 w4 w5"
        model = TfDocumentModel(text, tokenizer)

        self.assertEqual(model.most_frequent_terms(1), ("w5",))
        self.assertEqual(model.most_frequent_terms(2), ("w5", "w4"))
        self.assertEqual(model.most_frequent_terms(3), ("w5", "w4", "w3"))
        self.assertEqual(model.most_frequent_terms(4), ("w5", "w4", "w3", "w2"))
        self.assertEqual(model.most_frequent_terms(5), ("w5", "w4", "w3", "w2", "w1"))
        self.assertEqual(model.most_frequent_terms(), ("w5", "w4", "w3", "w2", "w1"))

    def test_most_frequent_terms_empty(self):
        tokenizer = Tokenizer("english")
        model = TfDocumentModel("", tokenizer)

        self.assertEqual(model.most_frequent_terms(), ())
        self.assertEqual(model.most_frequent_terms(10), ())

    def test_most_frequent_terms_negative_count(self):
        tokenizer = Tokenizer("english")
        model = TfDocumentModel("text", tokenizer)

        self.assertRaises(ValueError, model.most_frequent_terms, -1)
