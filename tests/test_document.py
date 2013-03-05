# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from case import unittest, build_document


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
