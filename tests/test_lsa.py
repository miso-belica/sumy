# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from case import unittest, build_document
from sumy.algorithms.lsa import LsaMethod
from sumy._py3k import to_unicode


class TestLsa(unittest.TestCase):
    def test_empty_document(self):
        document = build_document()
        sumarize = LsaMethod(document)

        sentences = sumarize(10)
        self.assertEqual(len(sentences), 0)

    def test_single_sentence(self):
        document = build_document(("I am the sentence you like",))
        sumarize = LsaMethod(document)
        sumarize.stopwords = ("I", "am", "the",)

        sentences = sumarize(10)
        self.assertEqual(len(sentences), 1)
        self.assertEqual(to_unicode(sentences[0]), "I am the sentence you like")

    def test_document(self):
        document = build_document(
            ("I am the sentence you like", "Do you like me too",),
            ("This sentence is better than that above", "Are you kidding me",)
        )
        sumarize = LsaMethod(document)
        sumarize.stopwords = ("I", "am", "the", "you", "are", "me", "is", "than", "that", "this",)

        sentences = sumarize(2)
        self.assertEqual(len(sentences), 2)
        self.assertEqual(to_unicode(sentences[0]), "I am the sentence you like")
        self.assertEqual(to_unicode(sentences[1]), "This sentence is better than that above")
