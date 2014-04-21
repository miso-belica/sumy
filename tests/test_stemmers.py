# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

import unittest

from sumy.nlp.stemmers import null_stemmer, Stemmer


class TestStemmers(unittest.TestCase):
    """Simple tests to make sure all stemmers share the same API."""
    def test_missing_stemmer_language(self):
        self.assertRaises(LookupError, Stemmer, "klingon")

    def test_null_stemmer(self):
        self.assertEqual("ľščťžýáíé", null_stemmer("ľŠčŤžÝáÍé"))

    def test_english_stemmer(self):
        english_stemmer = Stemmer('english')
        self.assertEqual("beauti", english_stemmer("beautiful"))

    def test_german_stemmer(self):
        german_stemmer = Stemmer('german')
        self.assertEqual("sterb", german_stemmer("sterben"))

    def test_czech_stemmer(self):
        czech_stemmer = Stemmer('czech')
        self.assertEqual("pěkn", czech_stemmer("pěkný"))

    def test_french_stemmer(self):
        french_stemmer = Stemmer('czech')
        self.assertEqual("jol", french_stemmer("jolies"))

    def test_slovak_stemmer(self):
        expected = Stemmer("czech")
        actual = Stemmer("slovak")
        self.assertEqual(type(actual), type(expected))
        self.assertEqual(expected.__dict__, actual.__dict__)
