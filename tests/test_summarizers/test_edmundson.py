# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

import unittest

from sumy.summarizers.edmundson import EdmundsonSummarizer
from sumy._compat import to_unicode
from ..utils import build_document, build_document_from_string


class TestEdmundson(unittest.TestCase):
    def test_bonus_words_property(self):
        document = build_document()
        summarize = EdmundsonSummarizer(document)

        self.assertEqual(summarize.bonus_words, frozenset())

        words = ("word", "another", "and", "some", "next",)
        summarize.bonus_words = words
        self.assertTrue(isinstance(summarize.bonus_words, frozenset))
        self.assertEqual(summarize.bonus_words, frozenset(words))

    def test_stigma_words_property(self):
        document = build_document()
        summarize = EdmundsonSummarizer(document)

        self.assertEqual(summarize.stigma_words, frozenset())

        words = ("word", "another", "and", "some", "next",)
        summarize.stigma_words = words
        self.assertTrue(isinstance(summarize.stigma_words, frozenset))
        self.assertEqual(summarize.stigma_words, frozenset(words))

    def test_null_words_property(self):
        document = build_document()
        summarize = EdmundsonSummarizer(document)

        self.assertEqual(summarize.null_words, frozenset())

        words = ("word", "another", "and", "some", "next",)
        summarize.null_words = words
        self.assertTrue(isinstance(summarize.null_words, frozenset))
        self.assertEqual(summarize.null_words, frozenset(words))

    def test_empty_document(self):
        document = build_document()
        summarize = EdmundsonSummarizer(document, cue_weight=0, key_weight=0,
            title_weight=0, location_weight=0)

        sentences = summarize(10)
        self.assertEqual(len(sentences), 0)

    def test_mixed_cue_key(self):
        document = build_document_from_string("""
            # This is cool heading
            Because I am sentence I like words
            And because I am string I like characters

            # blank and heading
            This is next paragraph because of blank line above
            Here is the winner because contains words like cool and heading
        """)

        summarize = EdmundsonSummarizer(document, cue_weight=1, key_weight=1,
            title_weight=0, location_weight=0)
        summarize.bonus_words = ("cool", "heading", "sentence", "words", "like", "because")
        summarize.stigma_words = ("this", "is", "I", "am", "and",)

        sentences = summarize(2)
        self.assertEqual(len(sentences), 2)
        self.assertEqual(to_unicode(sentences[0]),
            "Because I am sentence I like words")
        self.assertEqual(to_unicode(sentences[1]),
            "Here is the winner because contains words like cool and heading")

    def test_cue_with_no_words(self):
        document = build_document()
        summarize = EdmundsonSummarizer(document)

        self.assertRaises(ValueError, summarize.cue_method, 10)

    def test_cue_with_no_stigma_words(self):
        document = build_document()
        summarize = EdmundsonSummarizer(document)
        summarize.bonus_words = ("great", "very", "beautiful",)

        self.assertRaises(ValueError, summarize.cue_method, 10)

    def test_cue_with_no_bonus_words(self):
        document = build_document()
        summarize = EdmundsonSummarizer(document)
        summarize.stigma_words = ("useless", "bad", "spinach",)

        self.assertRaises(ValueError, summarize.cue_method, 10)

    def test_cue_empty(self):
        document = build_document()

        summarize = EdmundsonSummarizer(document)
        summarize.bonus_words = ("ba", "bb", "bc",)
        summarize.stigma_words = ("sa", "sb", "sc",)

        sentences = summarize.cue_method(10)
        self.assertEqual(len(sentences), 0)

    def test_cue_letters_case(self):
        document = build_document(
            ("X X X", "x x x x",),
            ("w w w", "W W W W",)
        )

        summarize = EdmundsonSummarizer(document)
        summarize.bonus_words = ("X", "w",)
        summarize.stigma_words = ("stigma",)

        sentences = summarize.cue_method(2)
        self.assertEqual(len(sentences), 2)
        self.assertEqual(to_unicode(sentences[0]), "x x x x")
        self.assertEqual(to_unicode(sentences[1]), "W W W W")

    def test_cue_1(self):
        document = build_document(
            ("ba bb bc bb unknown ľščťžýáíé sb sc sb",)
        )

        summarize = EdmundsonSummarizer(document)
        summarize.bonus_words = ("ba", "bb", "bc",)
        summarize.stigma_words = ("sa", "sb", "sc",)

        sentences = summarize.cue_method(10)
        self.assertEqual(len(sentences), 1)

    def test_cue_2(self):
        document = build_document(
            ("ba bb bc bb unknown ľščťžýáíé sb sc sb",),
            ("Pepek likes spinach",)
        )

        summarize = EdmundsonSummarizer(document)
        summarize.bonus_words = ("ba", "bb", "bc",)
        summarize.stigma_words = ("sa", "sb", "sc",)

        sentences = summarize.cue_method(10)
        self.assertEqual(len(sentences), 2)
        self.assertEqual(to_unicode(sentences[0]),
            "ba bb bc bb unknown ľščťžýáíé sb sc sb")
        self.assertEqual(to_unicode(sentences[1]), "Pepek likes spinach")

        sentences = summarize.cue_method(1)
        self.assertEqual(len(sentences), 1)
        self.assertEqual(to_unicode(sentences[0]),
            "ba bb bc bb unknown ľščťžýáíé sb sc sb")

    def test_cue_3(self):
        document = build_document(
            (
                "ba "*10,
                "bb "*10,
                " sa"*8 + " bb"*10,
                "bb bc ba",
            ),
            (),
            (
                "babbbc "*10,
                "na nb nc nd sa" + " bc"*10,
                " ba n"*10,
            )
        )

        summarize = EdmundsonSummarizer(document)
        summarize.bonus_words = ("ba", "bb", "bc",)
        summarize.stigma_words = ("sa", "sb", "sc",)

        sentences = summarize.cue_method(5)
        self.assertEqual(len(sentences), 5)
        self.assertEqual(to_unicode(sentences[0]), ("ba "*10).strip())
        self.assertEqual(to_unicode(sentences[1]), ("bb "*10).strip())
        self.assertEqual(to_unicode(sentences[2]), "bb bc ba")
        self.assertEqual(to_unicode(sentences[3]),
            "na nb nc nd sa bc bc bc bc bc bc bc bc bc bc")
        self.assertEqual(to_unicode(sentences[4]), ("ba n "*10).strip())

    def test_key_empty(self):
        document = build_document()

        summarize = EdmundsonSummarizer(document)
        summarize.bonus_words = ("ba", "bb", "bc",)

        sentences = summarize.key_method(10)
        self.assertEqual(len(sentences), 0)

    def test_key_without_bonus_words(self):
        document = build_document()
        summarize = EdmundsonSummarizer(document)

        self.assertRaises(ValueError, summarize.key_method, 10)

    def test_key_no_bonus_words_in_document(self):
        document = build_document(
            ("wa wb wc wd", "I like music",),
            ("This is test sentence with some extra words",)
        )
        summarize = EdmundsonSummarizer(document)
        summarize.bonus_words = ("ba", "bb", "bc", "bonus",)

        sentences = summarize.key_method(10)
        self.assertEqual(len(sentences), 3)
        self.assertEqual(to_unicode(sentences[0]), "wa wb wc wd")
        self.assertEqual(to_unicode(sentences[1]), "I like music")
        self.assertEqual(to_unicode(sentences[2]),
            "This is test sentence with some extra words")

    def test_key_1(self):
        document = build_document(
            ("wa wb wc wd", "I like music",),
            ("This is test sentence with some extra words and bonus",)
        )
        summarize = EdmundsonSummarizer(document)
        summarize.bonus_words = ("ba", "bb", "bc", "bonus",)

        sentences = summarize.key_method(1)
        self.assertEqual(len(sentences), 1)
        self.assertEqual(to_unicode(sentences[0]),
            "This is test sentence with some extra words and bonus")

    def test_key_2(self):
        document = build_document(
            ("Om nom nom nom nom", "Sure I summarize it, with bonus",),
            ("This is bonus test sentence with some extra words and bonus",)
        )
        summarize = EdmundsonSummarizer(document)
        summarize.bonus_words = ("nom", "bonus",)

        sentences = summarize.key_method(2)
        self.assertEqual(len(sentences), 2)
        self.assertEqual(to_unicode(sentences[0]), "Om nom nom nom nom")
        self.assertEqual(to_unicode(sentences[1]),
            "This is bonus test sentence with some extra words and bonus")

    def test_key_3(self):
        document = build_document(
            ("wa", "wa wa", "wa wa wa", "wa wa wa wa", "wa Wa Wa Wa wa",),
            ("x X x X",)
        )
        summarize = EdmundsonSummarizer(document)
        summarize.bonus_words = ("wa", "X",)

        sentences = summarize.key_method(3)
        self.assertEqual(len(sentences), 3)
        self.assertEqual(to_unicode(sentences[0]), "wa wa wa")
        self.assertEqual(to_unicode(sentences[1]), "wa wa wa wa")
        self.assertEqual(to_unicode(sentences[2]), "wa Wa Wa Wa wa")

        sentences = summarize.key_method(3, weight=0)
        self.assertEqual(len(sentences), 3)
        self.assertEqual(to_unicode(sentences[0]), "wa wa wa wa")
        self.assertEqual(to_unicode(sentences[1]), "wa Wa Wa Wa wa")
        self.assertEqual(to_unicode(sentences[2]), "x X x X")

    def test_title_method_with_empty_document(self):
        document = build_document()

        summarize = EdmundsonSummarizer(document)
        summarize.null_words = ("ba", "bb", "bc",)

        sentences = summarize.title_method(10)
        self.assertEqual(len(sentences), 0)

    def test_title_method_without_null_words(self):
        document = build_document()
        summarize = EdmundsonSummarizer(document)

        self.assertRaises(ValueError, summarize.title_method, 10)

    def test_title_method_without_title(self):
        document = build_document(
            ("This is sentence", "This is another one",),
            ("And some next sentence but no heading",)
        )

        summarize = EdmundsonSummarizer(document)
        summarize.null_words = ("this", "is", "some", "and",)

        sentences = summarize.title_method(10)
        self.assertEqual(len(sentences), 3)
        self.assertEqual(to_unicode(sentences[0]), "This is sentence")
        self.assertEqual(to_unicode(sentences[1]), "This is another one")
        self.assertEqual(to_unicode(sentences[2]), "And some next sentence but no heading")

    def test_title_method_1(self):
        document = build_document_from_string("""
            # This is cool heading
            Because I am sentence I like words
            And because I am string I like characters

            # blank and heading
            This is next paragraph because of blank line above
            Here is the winner because contains words like cool and heading
        """)

        summarize = EdmundsonSummarizer(document)
        summarize.null_words = ("this", "is", "I", "am", "and",)

        sentences = summarize.title_method(1)
        self.assertEqual(len(sentences), 1)
        self.assertEqual(to_unicode(sentences[0]),
            "Here is the winner because contains words like cool and heading")

    def test_title_method_2(self):
        document = build_document_from_string("""
            # This is cool heading
            Because I am sentence I like words
            And because I am string I like characters

            # blank and heading
            This is next paragraph because of blank line above
            Here is the winner because contains words like cool and heading
        """)

        summarize = EdmundsonSummarizer(document)
        summarize.null_words = ("this", "is", "I", "am", "and",)

        sentences = summarize.title_method(2)
        self.assertEqual(len(sentences), 2)
        self.assertEqual(to_unicode(sentences[0]),
            "This is next paragraph because of blank line above")
        self.assertEqual(to_unicode(sentences[1]),
            "Here is the winner because contains words like cool and heading")

    def test_title_method_3(self):
        document = build_document_from_string("""
            # This is cool heading
            Because I am sentence I like words
            And because I am string I like characters

            # blank and heading
            This is next paragraph because of blank line above
            Here is the winner because contains words like cool and heading
        """)

        summarize = EdmundsonSummarizer(document)
        summarize.null_words = ("this", "is", "I", "am", "and",)

        sentences = summarize.title_method(3)
        self.assertEqual(len(sentences), 3)
        self.assertEqual(to_unicode(sentences[0]),
            "Because I am sentence I like words")
        self.assertEqual(to_unicode(sentences[1]),
            "This is next paragraph because of blank line above")
        self.assertEqual(to_unicode(sentences[2]),
            "Here is the winner because contains words like cool and heading")

    def test_location_method_with_empty_document(self):
        document = build_document()

        summarize = EdmundsonSummarizer(document)
        summarize.null_words = ("na", "nb", "nc",)

        sentences = summarize.location_method(10)
        self.assertEqual(len(sentences), 0)

    def test_location_method_without_null_words(self):
        document = build_document()
        summarize = EdmundsonSummarizer(document)

        self.assertRaises(ValueError, summarize.location_method, 10)

    def test_location_method_1(self):
        document = build_document_from_string("""
            # na nb nc ha hb
            ha = 1 + 1 + 1 = 3
            ha hb = 2 + 1 + 1 = 4

            first = 1
            ha hb ha = 3
            last = 1

            # hc hd
            hb hc hd = 3 + 1 + 1 = 5
            ha hb = 2 + 1 + 1 = 4
        """)

        summarize = EdmundsonSummarizer(document)
        summarize.null_words = ("na", "nb", "nc", "nd", "ne",)

        sentences = summarize.location_method(4)
        self.assertEqual(len(sentences), 4)
        self.assertEqual(to_unicode(sentences[0]), "ha = 1 + 1 + 1 = 3")
        self.assertEqual(to_unicode(sentences[1]), "ha hb = 2 + 1 + 1 = 4")
        self.assertEqual(to_unicode(sentences[2]), "hb hc hd = 3 + 1 + 1 = 5")
        self.assertEqual(to_unicode(sentences[3]), "ha hb = 2 + 1 + 1 = 4")

    def test_location_method_2(self):
        document = build_document_from_string("""
            # na nb nc ha hb
            ha = 1 + 1 + 0 = 2
            middle = 0
            ha hb = 2 + 1 + 0 = 3

            first = 1
            ha hb ha = 3
            last = 1

            # hc hd
            hb hc hd = 3 + 1 + 0 = 4
            ha hb = 2 + 1 + 0 = 3
        """)

        summarize = EdmundsonSummarizer(document)
        summarize.null_words = ("na", "nb", "nc", "nd", "ne",)

        sentences = summarize.location_method(4, w_p1=0, w_p2=0)
        self.assertEqual(len(sentences), 4)
        self.assertEqual(to_unicode(sentences[0]), "ha hb = 2 + 1 + 0 = 3")
        self.assertEqual(to_unicode(sentences[1]), "ha hb ha = 3")
        self.assertEqual(to_unicode(sentences[2]), "hb hc hd = 3 + 1 + 0 = 4")
        self.assertEqual(to_unicode(sentences[3]), "ha hb = 2 + 1 + 0 = 3")
