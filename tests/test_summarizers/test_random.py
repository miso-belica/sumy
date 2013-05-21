# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

import unittest

from sumy.summarizers.random import RandomSummarizer
from sumy._compat import to_unicode
from ..utils import build_document, build_document_from_string


class TestRandom(unittest.TestCase):
    def test_empty_document(self):
        document = build_document()
        summarizer = RandomSummarizer()

        sentences = summarizer(document, 10)
        self.assertEqual(len(sentences), 0)

    def test_less_sentences_than_requested(self):
        document = build_document_from_string("""
            This is only one sentence.
        """)
        summarizer = RandomSummarizer()

        sentences = summarizer(document, 10)
        self.assertEqual(len(sentences), 1)
        self.assertEqual(to_unicode(sentences[0]), "This is only one sentence.")

    def test_sentences_in_right_order(self):
        document = build_document_from_string("""
            # Heading one
            First sentence.
            Second sentence.
            Third sentence.
        """)
        summarizer = RandomSummarizer()

        sentences = summarizer(document, 4)
        self.assertEqual(len(sentences), 3)
        self.assertEqual(to_unicode(sentences[0]), "First sentence.")
        self.assertEqual(to_unicode(sentences[1]), "Second sentence.")
        self.assertEqual(to_unicode(sentences[2]), "Third sentence.")

    def test_more_sentences_than_requested(self):
        document = build_document_from_string("""
            # Heading one
            First sentence.
            Second sentence.
            Third sentence.

            # Heading two
            I like sentences
            They are so wordy
            And have many many letters
            And are green in my editor
            But someone doesn't like them :(
        """)
        summarizer = RandomSummarizer()

        sentences = summarizer(document, 4)
        self.assertEqual(len(sentences), 4)
