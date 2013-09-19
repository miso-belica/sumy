# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

import unittest

from sumy.nlp.stemmers import null_stemmer
from sumy.nlp.stemmers.czech import stem_word as czech_stemmer
from sumy.nlp.stemmers.english import stem_word as english_stemmer
from sumy.nlp.stemmers.german import stem_word as german_stemmer


class TestStemmers(unittest.TestCase):
    """Simple tests to make sure all stemmers share the same API."""
    def test_null_stemmer(self):
        self.assertEqual("ľščťžýáíé", null_stemmer("ľŠčŤžÝáÍé"))

    def test_english_stemmer(self):
        self.assertEqual("beauti", english_stemmer("beautiful"))

    def test_german_stemmer(self):
        self.assertEqual("sterb", german_stemmer("sterben"))

    def test_czech_stemmer(self):
        self.assertEqual("pěkn", czech_stemmer("pěkný"))
