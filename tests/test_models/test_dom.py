# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

import unittest

from sumy._compat import to_unicode
from sumy.nlp.tokenizers import Tokenizer
from sumy.models.dom import Paragraph, Sentence
from ..utils import build_document, build_document_from_string


class TestDocument(unittest.TestCase):
    def test_unique_words(self):
        document = build_document(
            ("Nějaký muž šel kolem naší zahrady", "Nějaký muž šel kolem vaší zahrady",),
            ("Už už abych taky šel",),
        )

        returned = tuple(sorted(frozenset(document.words)))
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
        self.assertEqual(expected, returned)

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

    def test_only_instances_of_sentence_allowed(self):
        document = build_document_from_string("""
            Nějaký muž šel kolem naší zahrady
            Nějaký jiný muž šel kolem vaší zahrady

            # Nová myšlenka
            Už už abych taky šel
        """)

        self.assertRaises(TypeError, Paragraph,
            list(document.sentences) + ["Last sentence"])

    def test_sentences_equal(self):
        sentence1 = Sentence("", Tokenizer("czech"))
        sentence2 = Sentence("", Tokenizer("czech"))
        self.assertEqual(sentence1, sentence2)

        sentence1 = Sentence("word another.", Tokenizer("czech"))
        sentence2 = Sentence("word another.", Tokenizer("czech"))
        self.assertEqual(sentence1, sentence2)

        sentence1 = Sentence("word another", Tokenizer("czech"))
        sentence2 = Sentence("another word", Tokenizer("czech"))
        self.assertNotEqual(sentence1, sentence2)
