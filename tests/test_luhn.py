# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from case import unittest, build_document, build_sentence
from sumy.algorithms._luhn import LuhnMethod
from sumy._py3k import to_unicode


class TestLuhn(unittest.TestCase):
    def test_empty_document(self):
        document = build_document()
        luhn = LuhnMethod(document)

        returned = luhn(10)
        self.assertEqual(len(returned), 0)

    def test_single_sentence(self):
        document = build_document(("Já jsem jedna věta",))
        stopwords = ("já", "jsem",)
        luhn = LuhnMethod(document, stopwords)

        returned = luhn(10)
        self.assertEqual(len(returned), 1)

    def test_two_sentences(self):
        document = build_document(("Já jsem 1. věta", "A já ta 2. vítězná výhra"))
        stopwords = ("já", "jsem", "a", "ta",)
        luhn = LuhnMethod(document, stopwords)

        returned = luhn(10)
        self.assertEqual(len(returned), 2)
        self.assertEqual(to_unicode(returned[0]), "Já jsem 1. věta")
        self.assertEqual(to_unicode(returned[1]), "A já ta 2. vítězná výhra")

    def test_two_sentences_but_one_winner(self):
        document = build_document(("Já jsem 1. ta věta", "A já ta 2. vítězná výhra"))
        stopwords = ("já", "jsem", "a", "ta",)
        luhn = LuhnMethod(document, stopwords)

        returned = luhn(1)
        self.assertEqual(len(returned), 1)
        self.assertEqual(to_unicode(returned[0]), "A já ta 2. vítězná výhra")

    def test_three_sentences(self):
        document = build_document((
            "1 s s s 1 s s s 1",
            "2 s 2 s 2 s s s s s s s s s 2",
            "3 s s 3 s s 3",
        ))
        stopwords = ("s",)
        luhn = LuhnMethod(document, stopwords)

        returned = luhn(1)
        self.assertEqual(len(returned), 1)
        self.assertEqual(to_unicode(returned[0]), "2 s 2 s 2 s s s s s s s s s 2")

        returned = luhn(2)
        self.assertEqual(len(returned), 2)
        self.assertEqual(to_unicode(returned[0]), "2 s 2 s 2 s s s s s s s s s 2")
        self.assertEqual(to_unicode(returned[1]), "3 s s 3 s s 3")

        returned = luhn(3)
        self.assertEqual(len(returned), 3)
        self.assertEqual(to_unicode(returned[0]), "1 s s s 1 s s s 1")
        self.assertEqual(to_unicode(returned[1]), "2 s 2 s 2 s s s s s s s s s 2")
        self.assertEqual(to_unicode(returned[2]), "3 s s 3 s s 3")


class TestSentenceRating(unittest.TestCase):
    def setUp(self):
        self.luhn = LuhnMethod(build_document())
        self.sentence = build_sentence(
            "Nějaký muž šel kolem naší zahrady a žil pěkný život samotáře")

    def test_zero_rating(self):
        significant_stems = ()
        self.assertEqual(self.luhn.rate_sentence(self.sentence, significant_stems), 0)

    def test_single_word(self):
        significant_stems = ("muž",)
        self.assertEqual(self.luhn.rate_sentence(self.sentence, significant_stems), 0)

    def test_single_word_before_end(self):
        significant_stems = ("život",)
        self.assertEqual(self.luhn.rate_sentence(self.sentence, significant_stems), 0)

    def test_single_word_at_end(self):
        significant_stems = ("samotáře",)
        self.assertEqual(self.luhn.rate_sentence(self.sentence, significant_stems), 0)

    def test_two_chunks_too_far(self):
        significant_stems = ("šel", "žil",)
        self.assertEqual(self.luhn.rate_sentence(self.sentence, significant_stems), 0)

    def test_two_chunks_at_begin(self):
        significant_stems = ("muž", "šel",)
        self.assertEqual(self.luhn.rate_sentence(self.sentence, significant_stems), 2)

    def test_two_chunks_before_end(self):
        significant_stems = ("pěkný", "život",)
        self.assertEqual(self.luhn.rate_sentence(self.sentence, significant_stems), 2)

    def test_two_chunks_at_end(self):
        significant_stems = ("pěkný", "samotáře",)
        self.assertEqual(self.luhn.rate_sentence(self.sentence, significant_stems), 4/3)

    def test_three_chunks_at_begin(self):
        significant_stems = ("nějaký", "muž", "šel",)
        self.assertEqual(self.luhn.rate_sentence(self.sentence, significant_stems), 3)

    def test_three_chunks_at_end(self):
        significant_stems = ("pěkný", "život", "samotáře",)
        self.assertEqual(self.luhn.rate_sentence(self.sentence, significant_stems), 3)

    def test_three_chunks_with_gaps(self):
        significant_stems = ("muž", "šel", "zahrady",)
        self.assertEqual(self.luhn.rate_sentence(self.sentence, significant_stems), 9/5)

    def test_chunks_with_user_gap(self):
        self.luhn.max_gap_size = 6
        significant_stems = ("muž", "šel", "pěkný",)
        self.assertEqual(self.luhn.rate_sentence(self.sentence, significant_stems), 9/8)

    def test_three_chunks_with_1_gap(self):
        sentence = build_sentence("w s w s w")
        significant_stems = ("w",)

        self.assertEqual(self.luhn.rate_sentence(sentence, significant_stems), 9/5)

    def test_three_chunks_with_2_gap(self):
        sentence = build_sentence("w s s w s s w")
        significant_stems = ("w",)

        self.assertEqual(self.luhn.rate_sentence(sentence, significant_stems), 9/7)

    def test_three_chunks_with_3_gap(self):
        sentence = build_sentence("w s s s w s s s w")
        significant_stems = ("w",)

        self.assertEqual(self.luhn.rate_sentence(sentence, significant_stems), 1)
