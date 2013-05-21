# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

import unittest

from sumy.summarizers.edmundson import EdmundsonSummarizer
from sumy._compat import to_unicode
from ..utils import build_document, build_document_from_string


class TestEdmundson(unittest.TestCase):
    def test_bonus_words_property(self):
        summarizer = EdmundsonSummarizer()

        self.assertEqual(summarizer.bonus_words, frozenset())

        words = ("word", "another", "and", "some", "next",)
        summarizer.bonus_words = words
        self.assertTrue(isinstance(summarizer.bonus_words, frozenset))
        self.assertEqual(summarizer.bonus_words, frozenset(words))

    def test_stigma_words_property(self):
        summarizer = EdmundsonSummarizer()

        self.assertEqual(summarizer.stigma_words, frozenset())

        words = ("word", "another", "and", "some", "next",)
        summarizer.stigma_words = words
        self.assertTrue(isinstance(summarizer.stigma_words, frozenset))
        self.assertEqual(summarizer.stigma_words, frozenset(words))

    def test_null_words_property(self):
        summarizer = EdmundsonSummarizer()

        self.assertEqual(summarizer.null_words, frozenset())

        words = ("word", "another", "and", "some", "next",)
        summarizer.null_words = words
        self.assertTrue(isinstance(summarizer.null_words, frozenset))
        self.assertEqual(summarizer.null_words, frozenset(words))

    def test_empty_document(self):
        summarizer = EdmundsonSummarizer(cue_weight=0, key_weight=0,
            title_weight=0, location_weight=0)

        sentences = summarizer(build_document(), 10)
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

        summarizer = EdmundsonSummarizer(cue_weight=1, key_weight=1,
            title_weight=0, location_weight=0)
        summarizer.bonus_words = ("cool", "heading", "sentence", "words", "like", "because")
        summarizer.stigma_words = ("this", "is", "I", "am", "and",)

        sentences = summarizer(document, 2)
        self.assertEqual(len(sentences), 2)
        self.assertEqual(to_unicode(sentences[0]),
            "Because I am sentence I like words")
        self.assertEqual(to_unicode(sentences[1]),
            "Here is the winner because contains words like cool and heading")

    def test_cue_with_no_words(self):
        summarizer = EdmundsonSummarizer()

        self.assertRaises(ValueError, summarizer.cue_method, build_document(), 10)

    def test_cue_with_no_stigma_words(self):
        summarizer = EdmundsonSummarizer()
        summarizer.bonus_words = ("great", "very", "beautiful",)

        self.assertRaises(ValueError, summarizer.cue_method, build_document(), 10)

    def test_cue_with_no_bonus_words(self):
        summarizer = EdmundsonSummarizer()
        summarizer.stigma_words = ("useless", "bad", "spinach",)

        self.assertRaises(ValueError, summarizer.cue_method, build_document(), 10)

    def test_cue_empty(self):
        summarizer = EdmundsonSummarizer()
        summarizer.bonus_words = ("ba", "bb", "bc",)
        summarizer.stigma_words = ("sa", "sb", "sc",)

        sentences = summarizer.cue_method(build_document(), 10)
        self.assertEqual(len(sentences), 0)

    def test_cue_letters_case(self):
        document = build_document(
            ("X X X", "x x x x",),
            ("w w w", "W W W W",)
        )

        summarizer = EdmundsonSummarizer()
        summarizer.bonus_words = ("X", "w",)
        summarizer.stigma_words = ("stigma",)

        sentences = summarizer.cue_method(document, 2)
        self.assertEqual(len(sentences), 2)
        self.assertEqual(to_unicode(sentences[0]), "x x x x")
        self.assertEqual(to_unicode(sentences[1]), "W W W W")

    def test_cue_1(self):
        document = build_document(
            ("ba bb bc bb unknown ľščťžýáíé sb sc sb",)
        )

        summarizer = EdmundsonSummarizer()
        summarizer.bonus_words = ("ba", "bb", "bc",)
        summarizer.stigma_words = ("sa", "sb", "sc",)

        sentences = summarizer.cue_method(document, 10)
        self.assertEqual(len(sentences), 1)

    def test_cue_2(self):
        document = build_document(
            ("ba bb bc bb unknown ľščťžýáíé sb sc sb",),
            ("Pepek likes spinach",)
        )

        summarizer = EdmundsonSummarizer()
        summarizer.bonus_words = ("ba", "bb", "bc",)
        summarizer.stigma_words = ("sa", "sb", "sc",)

        sentences = summarizer.cue_method(document, 10)
        self.assertEqual(len(sentences), 2)
        self.assertEqual(to_unicode(sentences[0]),
            "ba bb bc bb unknown ľščťžýáíé sb sc sb")
        self.assertEqual(to_unicode(sentences[1]), "Pepek likes spinach")

        sentences = summarizer.cue_method(document, 1)
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

        summarizer = EdmundsonSummarizer()
        summarizer.bonus_words = ("ba", "bb", "bc",)
        summarizer.stigma_words = ("sa", "sb", "sc",)

        sentences = summarizer.cue_method(document, 5)
        self.assertEqual(len(sentences), 5)
        self.assertEqual(to_unicode(sentences[0]), ("ba "*10).strip())
        self.assertEqual(to_unicode(sentences[1]), ("bb "*10).strip())
        self.assertEqual(to_unicode(sentences[2]), "bb bc ba")
        self.assertEqual(to_unicode(sentences[3]),
            "na nb nc nd sa bc bc bc bc bc bc bc bc bc bc")
        self.assertEqual(to_unicode(sentences[4]), ("ba n "*10).strip())

    def test_key_empty(self):
        summarizer = EdmundsonSummarizer()
        summarizer.bonus_words = ("ba", "bb", "bc",)

        sentences = summarizer.key_method(build_document(), 10)
        self.assertEqual(len(sentences), 0)

    def test_key_without_bonus_words(self):
        summarizer = EdmundsonSummarizer()

        self.assertRaises(ValueError, summarizer.key_method, build_document(), 10)

    def test_key_no_bonus_words_in_document(self):
        document = build_document(
            ("wa wb wc wd", "I like music",),
            ("This is test sentence with some extra words",)
        )
        summarizer = EdmundsonSummarizer()
        summarizer.bonus_words = ("ba", "bb", "bc", "bonus",)

        sentences = summarizer.key_method(document, 10)
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
        summarizer = EdmundsonSummarizer()
        summarizer.bonus_words = ("ba", "bb", "bc", "bonus",)

        sentences = summarizer.key_method(document, 1)
        self.assertEqual(len(sentences), 1)
        self.assertEqual(to_unicode(sentences[0]),
            "This is test sentence with some extra words and bonus")

    def test_key_2(self):
        document = build_document(
            ("Om nom nom nom nom", "Sure I summarize it, with bonus",),
            ("This is bonus test sentence with some extra words and bonus",)
        )
        summarizer = EdmundsonSummarizer()
        summarizer.bonus_words = ("nom", "bonus",)

        sentences = summarizer.key_method(document, 2)
        self.assertEqual(len(sentences), 2)
        self.assertEqual(to_unicode(sentences[0]), "Om nom nom nom nom")
        self.assertEqual(to_unicode(sentences[1]),
            "This is bonus test sentence with some extra words and bonus")

    def test_key_3(self):
        document = build_document(
            ("wa", "wa wa", "wa wa wa", "wa wa wa wa", "wa Wa Wa Wa wa",),
            ("x X x X",)
        )
        summarizer = EdmundsonSummarizer()
        summarizer.bonus_words = ("wa", "X",)

        sentences = summarizer.key_method(document, 3)
        self.assertEqual(len(sentences), 3)
        self.assertEqual(to_unicode(sentences[0]), "wa wa wa")
        self.assertEqual(to_unicode(sentences[1]), "wa wa wa wa")
        self.assertEqual(to_unicode(sentences[2]), "wa Wa Wa Wa wa")

        sentences = summarizer.key_method(document, 3, weight=0)
        self.assertEqual(len(sentences), 3)
        self.assertEqual(to_unicode(sentences[0]), "wa wa wa wa")
        self.assertEqual(to_unicode(sentences[1]), "wa Wa Wa Wa wa")
        self.assertEqual(to_unicode(sentences[2]), "x X x X")

    def test_title_method_with_empty_document(self):
        summarizer = EdmundsonSummarizer()
        summarizer.null_words = ("ba", "bb", "bc",)

        sentences = summarizer.title_method(build_document(), 10)
        self.assertEqual(len(sentences), 0)

    def test_title_method_without_null_words(self):
        summarizer = EdmundsonSummarizer()

        self.assertRaises(ValueError, summarizer.title_method, build_document(), 10)

    def test_title_method_without_title(self):
        document = build_document(
            ("This is sentence", "This is another one",),
            ("And some next sentence but no heading",)
        )

        summarizer = EdmundsonSummarizer()
        summarizer.null_words = ("this", "is", "some", "and",)

        sentences = summarizer.title_method(document, 10)
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

        summarizer = EdmundsonSummarizer()
        summarizer.null_words = ("this", "is", "I", "am", "and",)

        sentences = summarizer.title_method(document, 1)
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

        summarizer = EdmundsonSummarizer()
        summarizer.null_words = ("this", "is", "I", "am", "and",)

        sentences = summarizer.title_method(document, 2)
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

        summarizer = EdmundsonSummarizer()
        summarizer.null_words = ("this", "is", "I", "am", "and",)

        sentences = summarizer.title_method(document, 3)
        self.assertEqual(len(sentences), 3)
        self.assertEqual(to_unicode(sentences[0]),
            "Because I am sentence I like words")
        self.assertEqual(to_unicode(sentences[1]),
            "This is next paragraph because of blank line above")
        self.assertEqual(to_unicode(sentences[2]),
            "Here is the winner because contains words like cool and heading")

    def test_location_method_with_empty_document(self):
        summarizer = EdmundsonSummarizer()
        summarizer.null_words = ("na", "nb", "nc",)

        sentences = summarizer.location_method(build_document(), 10)
        self.assertEqual(len(sentences), 0)

    def test_location_method_without_null_words(self):
        summarizer = EdmundsonSummarizer()

        self.assertRaises(ValueError, summarizer.location_method, build_document(), 10)

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

        summarizer = EdmundsonSummarizer()
        summarizer.null_words = ("na", "nb", "nc", "nd", "ne",)

        sentences = summarizer.location_method(document, 4)
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

        summarizer = EdmundsonSummarizer()
        summarizer.null_words = ("na", "nb", "nc", "nd", "ne",)

        sentences = summarizer.location_method(document, 4, w_p1=0, w_p2=0)
        self.assertEqual(len(sentences), 4)
        self.assertEqual(to_unicode(sentences[0]), "ha hb = 2 + 1 + 0 = 3")
        self.assertEqual(to_unicode(sentences[1]), "ha hb ha = 3")
        self.assertEqual(to_unicode(sentences[2]), "hb hc hd = 3 + 1 + 0 = 4")
        self.assertEqual(to_unicode(sentences[3]), "ha hb = 2 + 1 + 0 = 3")
