# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from case import unittest, build_document, build_sentence
from sumy.algorithms import EdmundsonMethod
from sumy._py3k import to_unicode


class TestEdmundson(unittest.TestCase):
    def test_bonus_words_property(self):
        document = build_document()
        summarize = EdmundsonMethod(document)

        self.assertSequenceEqual(summarize.bonus_words, frozenset())

        words = ("word", "another", "and", "some", "next",)
        summarize.bonus_words = words
        self.assertIsInstance(summarize.bonus_words, frozenset)
        self.assertEqual(summarize.bonus_words, frozenset(words))

    def test_stigma_words_property(self):
        document = build_document()
        summarize = EdmundsonMethod(document)

        self.assertSequenceEqual(summarize.stigma_words, frozenset())

        words = ("word", "another", "and", "some", "next",)
        summarize.stigma_words = words
        self.assertIsInstance(summarize.stigma_words, frozenset)
        self.assertEqual(summarize.stigma_words, frozenset(words))

    def test_null_words_property(self):
        document = build_document()
        summarize = EdmundsonMethod(document)

        self.assertSequenceEqual(summarize.null_words, frozenset())

        words = ("word", "another", "and", "some", "next",)
        summarize.null_words = words
        self.assertIsInstance(summarize.null_words, frozenset)
        self.assertEqual(summarize.null_words, frozenset(words))

    def test_empty_document(self):
        document = build_document()
        summarize = EdmundsonMethod(document)

        returned = summarize(10)
        self.assertEqual(len(returned), 0)

    def test_cue_with_no_words(self):
        document = build_document()
        summarize = EdmundsonMethod(document)

        self.assertRaises(ValueError, summarize.cue_method, 10)

    def test_cue_with_no_stigma_words(self):
        document = build_document()
        summarize = EdmundsonMethod(document)
        summarize.bonus_words = ("great", "very", "beautiful",)

        self.assertRaises(ValueError, summarize.cue_method, 10)

    def test_cue_with_no_bonus_words(self):
        document = build_document()
        summarize = EdmundsonMethod(document)
        summarize.stigma_words = ("useless", "bad", "spinach",)

        self.assertRaises(ValueError, summarize.cue_method, 10)

    def test_cue_empty(self):
        document = build_document()

        summarize = EdmundsonMethod(document)
        summarize.bonus_words = ("b1", "b2", "b3",)
        summarize.stigma_words = ("s1", "s2", "s3",)

        returned = summarize.cue_method(10)
        self.assertEqual(len(returned), 0)

    def test_cue_letters_case(self):
        document = build_document(
            ("X X X", "x x x x",),
            ("w w w", "W W W W",)
        )

        summarize = EdmundsonMethod(document)
        summarize.bonus_words = ("X", "w",)
        summarize.stigma_words = ("stigma",)

        sentences = summarize.cue_method(2)
        self.assertEqual(len(sentences), 2)
        self.assertEqual(to_unicode(sentences[0]), "x x x x")
        self.assertEqual(to_unicode(sentences[1]), "W W W W")

    def test_cue_1(self):
        document = build_document(
            ("b1 b2 b3 b2 unknown ľščťžýáíé s2 s3 s2",)
        )

        summarize = EdmundsonMethod(document)
        summarize.bonus_words = ("b1", "b2", "b3",)
        summarize.stigma_words = ("s1", "s2", "s3",)

        returned = summarize.cue_method(10)
        self.assertEqual(len(returned), 1)

    def test_cue_2(self):
        document = build_document(
            ("b1 b2 b3 b2 unknown ľščťžýáíé s2 s3 s2",),
            ("Pepek likes spinach",)
        )

        summarize = EdmundsonMethod(document)
        summarize.bonus_words = ("b1", "b2", "b3",)
        summarize.stigma_words = ("s1", "s2", "s3",)

        sentences = summarize.cue_method(10)
        self.assertEqual(len(sentences), 2)
        self.assertEqual(to_unicode(sentences[0]),
            "b1 b2 b3 b2 unknown ľščťžýáíé s2 s3 s2")
        self.assertEqual(to_unicode(sentences[1]), "Pepek likes spinach")

        sentences = summarize.cue_method(1)
        self.assertEqual(len(sentences), 1)
        self.assertEqual(to_unicode(sentences[0]),
            "b1 b2 b3 b2 unknown ľščťžýáíé s2 s3 s2")

    def test_cue_3(self):
        document = build_document(
            (
                "b1 "*10,
                "b2 "*10,
                " s1"*8 + " b2"*10,
                "b2 b3 b1",
            ),
            (),
            (
                "b1b2b3 "*10,
                "n1 n2 n3 n4 s1" + " b3"*10,
                " b1 n"*10,
            )
        )

        summarize = EdmundsonMethod(document)
        summarize.bonus_words = ("b1", "b2", "b3",)
        summarize.stigma_words = ("s1", "s2", "s3",)

        sentences = summarize.cue_method(5)
        self.assertEqual(len(sentences), 5)
        self.assertEqual(to_unicode(sentences[0]), ("b1 "*10).strip())
        self.assertEqual(to_unicode(sentences[1]), ("b2 "*10).strip())
        self.assertEqual(to_unicode(sentences[2]), "b2 b3 b1")
        self.assertEqual(to_unicode(sentences[3]),
            "n1 n2 n3 n4 s1 b3 b3 b3 b3 b3 b3 b3 b3 b3 b3")
        self.assertEqual(to_unicode(sentences[4]), ("b1 n "*10).strip())

    def test_key_empty(self):
        document = build_document()

        summarize = EdmundsonMethod(document)
        summarize.bonus_words = ("b1", "b2", "b3",)

        returned = summarize.key_method(10)
        self.assertEqual(len(returned), 0)

    def test_key_without_bonus_words(self):
        document = build_document()
        summarize = EdmundsonMethod(document)

        self.assertRaises(ValueError, summarize.key_method, 10)

    def test_key_no_bunus_words_in_document(self):
        document = build_document(
            ("w1 w2 w3 w4", "I like music",),
            ("This is test sentence with some extra words",)
        )
        summarize = EdmundsonMethod(document)
        summarize.bonus_words = ("b1", "b2", "b3", "bonus",)

        sentences = summarize.key_method(10)
        self.assertEqual(len(sentences), 3)
        self.assertEqual(to_unicode(sentences[0]), "w1 w2 w3 w4")
        self.assertEqual(to_unicode(sentences[1]), "I like music")
        self.assertEqual(to_unicode(sentences[2]),
            "This is test sentence with some extra words")

    def test_key_1(self):
        document = build_document(
            ("w1 w2 w3 w4", "I like music",),
            ("This is test sentence with some extra words and bonus",)
        )
        summarize = EdmundsonMethod(document)
        summarize.bonus_words = ("b1", "b2", "b3", "bonus",)

        sentences = summarize.key_method(1)
        self.assertEqual(len(sentences), 1)
        self.assertEqual(to_unicode(sentences[0]),
            "This is test sentence with some extra words and bonus")

    def test_key_2(self):
        document = build_document(
            ("Om nom nom nom nom", "Sure I sumarrize it, with bonus",),
            ("This is bonus test sentence with some extra words and bonus",)
        )
        summarize = EdmundsonMethod(document)
        summarize.bonus_words = ("nom", "bonus",)

        sentences = summarize.key_method(2)
        self.assertEqual(len(sentences), 2)
        self.assertEqual(to_unicode(sentences[0]), "Om nom nom nom nom")
        self.assertEqual(to_unicode(sentences[1]),
            "This is bonus test sentence with some extra words and bonus")

    def test_key_3(self):
        document = build_document(
            ("w1", "w1 w1", "w1 w1 w1", "w1 w1 w1 w1", "w1 W1 W1 W1 w1",),
            ("x X x X",)
        )
        summarize = EdmundsonMethod(document)
        summarize.bonus_words = ("w1", "X",)

        sentences = summarize.key_method(3)
        self.assertEqual(len(sentences), 3)
        self.assertEqual(to_unicode(sentences[0]), "w1 w1 w1")
        self.assertEqual(to_unicode(sentences[1]), "w1 w1 w1 w1")
        self.assertEqual(to_unicode(sentences[2]), "w1 W1 W1 W1 w1")

        sentences = summarize.key_method(3, weight=0)
        self.assertEqual(len(sentences), 3)
        self.assertEqual(to_unicode(sentences[0]), "w1 w1 w1 w1")
        self.assertEqual(to_unicode(sentences[1]), "w1 W1 W1 W1 w1")
        self.assertEqual(to_unicode(sentences[2]), "x X x X")
