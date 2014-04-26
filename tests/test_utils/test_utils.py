# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

import unittest

from sumy.utils import get_stop_words, read_stop_words, ItemsCount
from ..utils import expand_resource_path


class TestUtils(unittest.TestCase):
    def test_ok_stop_words_language(self):
        stop_words = get_stop_words("french")
        self.assertTrue(len(stop_words) > 1, str(len(stop_words)))

    def test_missing_stop_words_language(self):
        self.assertRaises(LookupError, get_stop_words, "klingon")

    def test_ok_custom_stopwords_file(self):
        stop_words = read_stop_words(expand_resource_path("stopwords/language.txt"))
        self.assertEqual(len(stop_words), 4)

    def test_custom_stop_words_file_not_found(self):
        self.assertRaises(IOError, read_stop_words, expand_resource_path("stopwords/klingon.txt"))

    def test_percentage_items_count(self):
        count = ItemsCount("20%")
        returned = count([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        self.assertEqual(returned, [0, 1])

        count = ItemsCount("100%")
        returned = count([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        self.assertEqual(returned, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])

        count = ItemsCount("50%")
        returned = count([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        self.assertEqual(returned, [0, 1, 2, 3, 4])

        count = ItemsCount("30%")
        returned = count([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        self.assertEqual(returned, [0, 1, 2])

        count = ItemsCount("35%")
        returned = count([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        self.assertEqual(returned, [0, 1, 2])

    def test_float_items_count(self):
        count = ItemsCount(3.5)
        returned = count([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        self.assertEqual(returned, [0, 1, 2])

        count = ItemsCount(True)
        returned = count([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        self.assertEqual(returned, [0])

        count = ItemsCount(False)
        returned = count([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        self.assertEqual(returned, [])

    def test_unsuported_items_count(self):
        count = ItemsCount("Hacker")
        self.assertRaises(ValueError, count, [])
