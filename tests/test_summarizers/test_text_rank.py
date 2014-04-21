# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

import unittest

from sumy.summarizers.text_rank import TextRankSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy._compat import to_unicode
from ..utils import build_document


class TestTextRank(unittest.TestCase):
    def test_empty_document(self):
        document = build_document()
        summarizer = TextRankSummarizer(Stemmer("english"))

        returned = summarizer(document, 10)
        self.assertEqual(len(returned), 0)

    def test_single_sentence(self):
        document = build_document(("I am one sentence",))
        summarizer = TextRankSummarizer()
        summarizer.stop_words = ("I", "am",)

        returned = summarizer(document, 10)
        self.assertEqual(len(returned), 1)

    def test_two_sentences(self):
        document = build_document(("I am that 1. sentence", "And I am 2. winning prize"))
        summarizer = TextRankSummarizer()
        summarizer.stop_words = ("I", "am", "and", "that",)

        returned = summarizer(document, 10)
        self.assertEqual(len(returned), 2)
        self.assertEqual(to_unicode(returned[0]), "I am that 1. sentence")
        self.assertEqual(to_unicode(returned[1]), "And I am 2. winning prize")

    def test_stop_words_correctly_removed(self):
        summarizer = TextRankSummarizer()
        summarizer.stop_words = ["stop", "Halt", "SHUT", "HmMm"]

        document = build_document(
            ("stop halt shut hmmm", "Stop Halt Shut Hmmm",),
            ("StOp HaLt ShUt HmMm", "STOP HALT SHUT HMMM",),
            ("Some relevant sentence", "Some moRe releVant sentEnce",),
        )
        sentences = document.sentences

        expected = []
        returned = summarizer._to_words_set(sentences[0])
        self.assertEqual(expected, returned)
        returned = summarizer._to_words_set(sentences[1])
        self.assertEqual(expected, returned)
        returned = summarizer._to_words_set(sentences[2])
        self.assertEqual(expected, returned)
        returned = summarizer._to_words_set(sentences[3])
        self.assertEqual(expected, returned)

        expected = ["some", "relevant", "sentence"]
        returned = summarizer._to_words_set(sentences[4])
        self.assertEqual(expected, returned)
        expected = ["some", "more", "relevant", "sentence"]
        returned = summarizer._to_words_set(sentences[5])
        self.assertEqual(expected, returned)

    def test_three_sentences_but_second_winner(self):
        document = build_document([
            "I am that 1. sentence",
            "And I am 2. sentence - winning sentence",
            "And I am 3. sentence - winner is my 2nd name",
        ])
        summarizer = TextRankSummarizer()
        summarizer.stop_words = ["I", "am", "and", "that"]

        returned = summarizer(document, 1)
        self.assertEqual(len(returned), 1)
        self.assertEqual(to_unicode(returned[0]), "And I am 2. sentence - winning sentence")

    def test_sentences_rating(self):
        document = build_document([
            "a c e g",
            "a b c d e f g",
            "b d f",
        ])
        summarizer = TextRankSummarizer()
        summarizer.stop_words = ["I", "am", "and", "that"]

        ratings = summarizer.rate_sentences(document)
        self.assertEqual(len(ratings), 3)
        self.assertTrue(ratings[document.sentences[1]] > ratings[document.sentences[0]])
        self.assertTrue(ratings[document.sentences[0]] > ratings[document.sentences[2]])
