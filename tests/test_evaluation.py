# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from case import unittest
from sumy.tokenizers import Tokenizer
from sumy.models import TfDocumentModel
from sumy.evaluation import precision, recall, f_score
from sumy.evaluation import cosine_similarity


class TestCoselectionEvaluation(unittest.TestCase):
    def test_precision_empty_evaluated(self):
        self.assertRaises(ValueError, precision, (), ("s1", "s2", "s3", "s4", "s5"))

    def test_precision_empty_reference(self):
        self.assertRaises(ValueError, precision, ("s1", "s2", "s3", "s4", "s5"), ())

    def test_precision_no_match(self):
        result = precision(("s1", "s2", "s3", "s4", "s5"), ("s6", "s7", "s8"))

        self.assertEqual(result, 0.0)

    def test_precision_reference_smaller(self):
        result = precision(("s1", "s2", "s3", "s4", "s5"), ("s1",))

        self.assertAlmostEqual(result, 0.2)

    def test_precision_evaluated_smaller(self):
        result = precision(("s1",), ("s1", "s2", "s3", "s4", "s5"))

        self.assertAlmostEqual(result, 1.0)

    def test_precision_equals(self):
        sentences = ("s1", "s2", "s3", "s4", "s5")
        result = precision(sentences, sentences)

        self.assertAlmostEqual(result, 1.0)

    def test_recall_empty_evaluated(self):
        self.assertRaises(ValueError,  recall, (), ("s1", "s2", "s3", "s4", "s5"))

    def test_recall_empty_reference(self):
        self.assertRaises(ValueError,  recall, ("s1", "s2", "s3", "s4", "s5"), ())

    def test_recall_no_match(self):
        result = recall(("s1", "s2", "s3", "s4", "s5"), ("s6", "s7", "s8"))

        self.assertEqual(result, 0.0)

    def test_recall_reference_smaller(self):
        result = recall(("s1", "s2", "s3", "s4", "s5"), ("s1",))

        self.assertAlmostEqual(result, 1.0)

    def test_recall_evaluated_smaller(self):
        result = recall(("s1",), ("s1", "s2", "s3", "s4", "s5"))

        self.assertAlmostEqual(result, 0.20)

    def test_recall_equals(self):
        sentences = ("s1", "s2", "s3", "s4", "s5")
        result = recall(sentences, sentences)

        self.assertAlmostEqual(result, 1.0)

    def test_basic_f_score_empty_evaluated(self):
        self.assertRaises(ValueError, f_score, (), ("s1", "s2", "s3", "s4", "s5"))

    def test_basic_f_score_empty_reference(self):
        self.assertRaises(ValueError, f_score, ("s1", "s2", "s3", "s4", "s5"), ())

    def test_basic_f_score_no_match(self):
        result = f_score(("s1", "s2", "s3", "s4", "s5"), ("s6", "s7", "s8"))

        self.assertEqual(result, 0.0)

    def test_basic_f_score_reference_smaller(self):
        result = f_score(("s1", "s2", "s3", "s4", "s5"), ("s1",))

        self.assertAlmostEqual(result, 1/3)

    def test_basic_f_score_evaluated_smaller(self):
        result = f_score(("s1",), ("s1", "s2", "s3", "s4", "s5"))

        self.assertAlmostEqual(result, 1/3)

    def test_basic_f_score_equals(self):
        sentences = ("s1", "s2", "s3", "s4", "s5")
        result = f_score(sentences, sentences)

        self.assertAlmostEqual(result, 1.0)

    def test_f_score_1(self):
        sentences = (("s1",), ("s1", "s2", "s3", "s4", "s5"))
        result = f_score(*sentences, weight=2.0)

        p = 1/1
        r = 1/5
        # ( (W^2 + 1) * P * R ) / ( W^2 * P + R )
        expected = (5 * p * r) / (4 * p + r)

        self.assertAlmostEqual(result, expected)

    def test_f_score_2(self):
        sentences = (("s1", "s3", "s6"), ("s1", "s2", "s3", "s4", "s5"))
        result = f_score(*sentences, weight=0.5)

        p = 2/3
        r = 2/5
        # ( (W^2 + 1) * P * R ) / ( W^2 * P + R )
        expected = (1.25 * p * r) / (0.25 * p + r)

        self.assertAlmostEqual(result, expected)


class TestContentBasedEvaluation(unittest.TestCase):
    def test_wrong_arguments(self):
        text = "Toto je moja veta, to sa nedá poprieť."
        model = TfDocumentModel(text, Tokenizer("czech"))

        self.assertRaises(ValueError, cosine_similarity, text, text)
        self.assertRaises(ValueError, cosine_similarity, text, model)
        self.assertRaises(ValueError, cosine_similarity, model, text)

    def test_cosine_exact_match(self):
        text = "Toto je moja veta, to sa nedá poprieť."
        model = TfDocumentModel(text, Tokenizer("czech"))

        self.assertAlmostEqual(cosine_similarity(model, model), 1.0)

    def test_cosine_no_match(self):
        tokenizer = Tokenizer("czech")
        model1 = TfDocumentModel("Toto je moja veta. To sa nedá poprieť!",
            tokenizer)
        model2 = TfDocumentModel("Hento bolo jeho slovo, ale možno klame.",
            tokenizer)

        self.assertAlmostEqual(cosine_similarity(model1, model2), 0.0)

    def test_cosine_half_match(self):
        tokenizer = Tokenizer("czech")
        model1 = TfDocumentModel("Veta aká sa len veľmi ťažko hľadá.",
            tokenizer)
        model2 = TfDocumentModel("Teta ktorá sa iba veľmi zle hľadá.",
            tokenizer)

        self.assertAlmostEqual(cosine_similarity(model1, model2), 0.5)
