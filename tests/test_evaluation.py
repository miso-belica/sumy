# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from case import unittest
from sumy.evaluation import precision, recall, f_score


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

    def test_basic_f_score_empty_evaluated(self):
        result = f_score((), ("s1", "s2", "s3", "s4", "s5"))

        self.assertTrue(0.0 <= result <= 1.0)
        self.assertEqual(result, 0.0)

    def test_basic_f_score_empty_reference(self):
        result = f_score(("s1", "s2", "s3", "s4", "s5"), ())

        self.assertTrue(0.0 <= result <= 1.0)
        self.assertEqual(result, 0.0)

    def test_basic_f_score_no_match(self):
        result = f_score(("s1", "s2", "s3", "s4", "s5"), ("s6", "s7", "s8"))

        self.assertTrue(0.0 <= result <= 1.0)
        self.assertEqual(result, 0.0)

    def test_basic_f_score_reference_smaller(self):
        result = f_score(("s1", "s2", "s3", "s4", "s5"), ("s1",))

        self.assertTrue(0.0 <= result <= 1.0)
        self.assertAlmostEqual(result, 1/3)

    def test_basic_f_score_evaluated_smaller(self):
        result = f_score(("s1",), ("s1", "s2", "s3", "s4", "s5"))

        self.assertTrue(0.0 <= result <= 1.0)
        self.assertAlmostEqual(result, 1/3)

    def test_basic_f_score_equals(self):
        sentences = ("s1", "s2", "s3", "s4", "s5")
        result = f_score(sentences, sentences)

        self.assertTrue(0.0 <= result <= 1.0)
        self.assertAlmostEqual(result, 1.0)

    def test_f_score_1(self):
        sentences = (("s1",), ("s1", "s2", "s3", "s4", "s5"))
        result = f_score(*sentences, weight=2.0)

        self.assertTrue(0.0 <= result <= 1.0)
        p = 1/1
        r = 1/5
        # ( (W^2 + 1) * P * R ) / ( W^2 * P + R )
        expected = (5 * p * r) / (4 * p + r)

        self.assertAlmostEqual(result, expected)

    def test_f_score_2(self):
        sentences = (("s1", "s3", "s6"), ("s1", "s2", "s3", "s4", "s5"))
        result = f_score(*sentences, weight=0.5)

        self.assertTrue(0.0 <= result <= 1.0)
        p = 2/3
        r = 2/5
        # ( (W^2 + 1) * P * R ) / ( W^2 * P + R )
        expected = (1.25 * p * r) / (0.25 * p + r)

        self.assertAlmostEqual(result, expected)
