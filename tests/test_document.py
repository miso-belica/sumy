# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from case import unittest, build_document, build_document_from_string
from sumy._py3k import to_unicode


class TestDocument(unittest.TestCase):
    def test_unique_words(self):
        document = build_document(
            ("Nějaký muž šel kolem naší zahrady", "Nějaký muž šel kolem vaší zahrady",),
            ("Už už abych taky šel",),
        )

        returned = sorted(frozenset(document.words))
        expected = (
            "Nějaký",
            "Už",
            "abych",
            "kolem",
            "muž",
            "naší",
            "taky",
            "už",
            "vaší",
            "zahrady",
            "šel"
        )
        self.assertSequenceEqual(expected, returned)

    def test_headings(self):
        document = build_document_from_string("""
            Nějaký muž šel kolem naší zahrady
            Nějaký jiný muž šel kolem vaší zahrady

            # Nová myšlenka
            Už už abych taky šel
        """)

        self.assertEqual(len(document.headings), 1)
        self.assertEqual(to_unicode(document.headings[0]), "Nová myšlenka")

    def test_sentences(self):
        document = build_document_from_string("""
            Nějaký muž šel kolem naší zahrady
            Nějaký jiný muž šel kolem vaší zahrady

            # Nová myšlenka
            Už už abych taky šel
        """)

        self.assertEqual(len(document.sentences), 3)
        self.assertEqual(to_unicode(document.sentences[0]),
            "Nějaký muž šel kolem naší zahrady")
        self.assertEqual(to_unicode(document.sentences[1]),
            "Nějaký jiný muž šel kolem vaší zahrady")
        self.assertEqual(to_unicode(document.sentences[2]),
            "Už už abych taky šel")
