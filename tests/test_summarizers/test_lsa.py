# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

import unittest

from sumy.summarizers.lsa import LsaSummarizer
from sumy._compat import to_unicode
from ..utils import build_document


class TestLsa(unittest.TestCase):
    def test_empty_document(self):
        document = build_document()
        summarizer = LsaSummarizer(document)

        sentences = summarizer(10)
        self.assertEqual(len(sentences), 0)

    def test_single_sentence(self):
        document = build_document(("I am the sentence you like",))
        summarizer = LsaSummarizer(document)
        summarizer.stopwords = ("I", "am", "the",)

        sentences = summarizer(10)
        self.assertEqual(len(sentences), 1)
        self.assertEqual(to_unicode(sentences[0]), "I am the sentence you like")

    def test_document(self):
        document = build_document(
            ("I am the sentence you like", "Do you like me too",),
            ("This sentence is better than that above", "Are you kidding me",)
        )
        summarizer = LsaSummarizer(document)
        summarizer.stopwords = ("I", "am", "the", "you", "are", "me", "is", "than", "that", "this",)

        sentences = summarizer(2)
        self.assertEqual(len(sentences), 2)
        self.assertEqual(to_unicode(sentences[0]), "I am the sentence you like")
        self.assertEqual(to_unicode(sentences[1]), "This sentence is better than that above")
