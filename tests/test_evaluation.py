# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from case import unittest
from sumy.evaluation import precision, recall


class TestEvaluation(unittest.TestCase):
    def test_precision_empty_evaluated(self):
        result = precision((), ("s1", "s2", "s3", "s4", "s5"))

        self.assertTrue(0.0 <= result <= 1.0)
        self.assertEqual(result, 0.0)

    def test_precision_empty_reference(self):
        result = precision(("s1", "s2", "s3", "s4", "s5"), ())

        self.assertTrue(0.0 <= result <= 1.0)
        self.assertEqual(result, 0.0)

    def test_precision_no_match(self):
        result = precision(("s1", "s2", "s3", "s4", "s5"), ("s6", "s7", "s8"))

        self.assertTrue(0.0 <= result <= 1.0)
        self.assertEqual(result, 0.0)

    def test_precision_reference_smaller(self):
        result = precision(("s1", "s2", "s3", "s4", "s5"), ("s1",))

        self.assertTrue(0.0 <= result <= 1.0)
        self.assertAlmostEqual(result, 0.2)

    def test_precision_evaluated_smaller(self):
        result = precision(("s1",), ("s1", "s2", "s3", "s4", "s5"))

        self.assertTrue(0.0 <= result <= 1.0)
        self.assertAlmostEqual(result, 1.0)

    def test_precision_equals(self):
        sentences = ("s1", "s2", "s3", "s4", "s5")
        result = precision(sentences, sentences)

        self.assertTrue(0.0 <= result <= 1.0)
        self.assertAlmostEqual(result, 1.0)

    def test_recall_empty_evaluated(self):
        result = recall((), ("s1", "s2", "s3", "s4", "s5"))

        self.assertTrue(0.0 <= result <= 1.0)
        self.assertEqual(result, 0.0)

    def test_recall_empty_reference(self):
        result = recall(("s1", "s2", "s3", "s4", "s5"), ())

        self.assertTrue(0.0 <= result <= 1.0)
        self.assertEqual(result, 0.0)

    def test_recall_no_match(self):
        result = recall(("s1", "s2", "s3", "s4", "s5"), ("s6", "s7", "s8"))

        self.assertTrue(0.0 <= result <= 1.0)
        self.assertEqual(result, 0.0)

    def test_recall_reference_smaller(self):
        result = recall(("s1", "s2", "s3", "s4", "s5"), ("s1",))

        self.assertTrue(0.0 <= result <= 1.0)
        self.assertAlmostEqual(result, 1.0)

    def test_recall_evaluated_smaller(self):
        result = recall(("s1",), ("s1", "s2", "s3", "s4", "s5"))

        self.assertTrue(0.0 <= result <= 1.0)
        self.assertAlmostEqual(result, 0.20)

    def test_recall_equals(self):
        sentences = ("s1", "s2", "s3", "s4", "s5")
        result = recall(sentences, sentences)

        self.assertTrue(0.0 <= result <= 1.0)
        self.assertAlmostEqual(result, 1.0)
