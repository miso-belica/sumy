# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

import unittest

from sumy.summarizers.luhn import LuhnSummarizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.nlp.stemmers.cs import stem_word
from sumy.utils import get_stop_words
from sumy._compat import to_unicode
from ..utils import build_document, build_sentence


class TestLuhn(unittest.TestCase):
    def test_empty_document(self):
        document = build_document()
        luhn = LuhnSummarizer(document)

        returned = luhn(10)
        self.assertEqual(len(returned), 0)

    def test_single_sentence(self):
        document = build_document(("Já jsem jedna věta",))
        luhn = LuhnSummarizer(document)
        luhn.stop_words = ("já", "jsem",)

        returned = luhn(10)
        self.assertEqual(len(returned), 1)

    def test_two_sentences(self):
        document = build_document(("Já jsem 1. věta", "A já ta 2. vítězná výhra"))
        luhn = LuhnSummarizer(document)
        luhn.stop_words = ("já", "jsem", "a", "ta",)

        returned = luhn(10)
        self.assertEqual(len(returned), 2)
        self.assertEqual(to_unicode(returned[0]), "Já jsem 1. věta")
        self.assertEqual(to_unicode(returned[1]), "A já ta 2. vítězná výhra")

    def test_two_sentences_but_one_winner(self):
        document = build_document(("Já jsem 1. ta věta", "A já ta 2. vítězná výhra"))
        luhn = LuhnSummarizer(document)
        luhn.stop_words = ("já", "jsem", "a", "ta",)

        returned = luhn(1)
        self.assertEqual(len(returned), 1)
        self.assertEqual(to_unicode(returned[0]), "A já ta 2. vítězná výhra")

    def test_three_sentences(self):
        document = build_document((
            "wa s s s wa s s s wa",
            "wb s wb s wb s s s s s s s s s wb",
            "wc s s wc s s wc",
        ))
        luhn = LuhnSummarizer(document)
        luhn.stop_words = ("s",)

        returned = luhn(1)
        self.assertEqual(len(returned), 1)
        self.assertEqual(to_unicode(returned[0]), "wb s wb s wb s s s s s s s s s wb")

        returned = luhn(2)
        self.assertEqual(len(returned), 2)
        self.assertEqual(to_unicode(returned[0]), "wb s wb s wb s s s s s s s s s wb")
        self.assertEqual(to_unicode(returned[1]), "wc s s wc s s wc")

        returned = luhn(3)
        self.assertEqual(len(returned), 3)
        self.assertEqual(to_unicode(returned[0]), "wa s s s wa s s s wa")
        self.assertEqual(to_unicode(returned[1]), "wb s wb s wb s s s s s s s s s wb")
        self.assertEqual(to_unicode(returned[2]), "wc s s wc s s wc")

    def test_various_words_with_significant_percentage(self):
        document = build_document((
            "1 a",
            "2 b b",
            "3 c c c",
            "4 d d d",
            "5 z z z z",
            "6 e e e e e",
        ))
        luhn = LuhnSummarizer(document)
        luhn.stop_words = ("1", "2", "3", "4", "5", "6")

        returned = luhn(1)
        self.assertEqual(len(returned), 1)
        self.assertEqual(to_unicode(returned[0]), "6 e e e e e")

        returned = luhn(2)
        self.assertEqual(len(returned), 2)
        self.assertEqual(to_unicode(returned[0]), "5 z z z z")
        self.assertEqual(to_unicode(returned[1]), "6 e e e e e")

        returned = luhn(3)
        self.assertEqual(len(returned), 3)
        self.assertEqual(to_unicode(returned[0]), "3 c c c")
        self.assertEqual(to_unicode(returned[1]), "5 z z z z")
        self.assertEqual(to_unicode(returned[2]), "6 e e e e e")

    def test_real_example(self):
        parser = PlaintextParser.from_string(
            "Jednalo se o případ chlapce v 6. třídě, který měl problémy s učením. "
            "Přerostly až v reparát z jazyka na konci školního roku. "
            "Nedopadl bohužel dobře a tak musel opakovat 6. třídu, což se chlapci ani trochu nelíbilo. "
            "Připadal si, že je mezi malými dětmi a realizoval se tím, že si ve třídě "
            "o rok mladších dětí budoval vedoucí pozici. "
            "Dost razantně. Fyzickou převahu měl, takže to nedalo až tak moc práce.",
            Tokenizer("czech")
        )
        summarizer = LuhnSummarizer(parser.document, stem_word)
        summarizer.stop_words = get_stop_words("cs")
        summarizer.significant_percentage = 0.12

        returned = summarizer(2)
        self.assertEqual(len(returned), 2)
        self.assertEqual(to_unicode(returned[0]),
            "Jednalo se o případ chlapce v 6. třídě , který měl problémy s učením .")
        self.assertEqual(to_unicode(returned[1]),
            "Připadal si , že je mezi malými dětmi a realizoval se tím , "
            "že si ve třídě o rok mladších dětí budoval vedoucí pozici .")


class TestSentenceRating(unittest.TestCase):
    def setUp(self):
        self.luhn = LuhnSummarizer(build_document())
        self.sentence = build_sentence(
            "Nějaký muž šel kolem naší zahrady a žil pěkný život samotáře")

    def test_significant_words(self):
        self.luhn.significant_percentage = 1/5
        words = self.luhn._get_significant_words((
            "wa", "wb", "wc", "wd", "we", "wf", "wg", "wh", "wi", "wj",
            "wa", "wb",
        ))

        self.assertEqual(tuple(sorted(words)), ("wa", "wb"))

    def test_zero_rating(self):
        significant_stems = ()
        self.assertEqual(self.luhn.rate_sentence(self.sentence, significant_stems), 0)

    def test_single_word(self):
        significant_stems = ("muž",)
        self.assertEqual(self.luhn.rate_sentence(self.sentence, significant_stems), 0)

    def test_single_word_before_end(self):
        significant_stems = ("život",)
        self.assertEqual(self.luhn.rate_sentence(self.sentence, significant_stems), 0)

    def test_single_word_at_end(self):
        significant_stems = ("samotáře",)
        self.assertEqual(self.luhn.rate_sentence(self.sentence, significant_stems), 0)

    def test_two_chunks_too_far(self):
        significant_stems = ("šel", "žil",)
        self.assertEqual(self.luhn.rate_sentence(self.sentence, significant_stems), 0)

    def test_two_chunks_at_begin(self):
        significant_stems = ("muž", "šel",)
        self.assertEqual(self.luhn.rate_sentence(self.sentence, significant_stems), 2)

    def test_two_chunks_before_end(self):
        significant_stems = ("pěkný", "život",)
        self.assertEqual(self.luhn.rate_sentence(self.sentence, significant_stems), 2)

    def test_two_chunks_at_end(self):
        significant_stems = ("pěkný", "samotáře",)
        self.assertEqual(self.luhn.rate_sentence(self.sentence, significant_stems), 4/3)

    def test_three_chunks_at_begin(self):
        significant_stems = ("nějaký", "muž", "šel",)
        self.assertEqual(self.luhn.rate_sentence(self.sentence, significant_stems), 3)

    def test_three_chunks_at_end(self):
        significant_stems = ("pěkný", "život", "samotáře",)
        self.assertEqual(self.luhn.rate_sentence(self.sentence, significant_stems), 3)

    def test_three_chunks_with_gaps(self):
        significant_stems = ("muž", "šel", "zahrady",)
        self.assertEqual(self.luhn.rate_sentence(self.sentence, significant_stems), 9/5)

    def test_chunks_with_user_gap(self):
        self.luhn.max_gap_size = 6
        significant_stems = ("muž", "šel", "pěkný",)
        self.assertEqual(self.luhn.rate_sentence(self.sentence, significant_stems), 9/8)

    def test_three_chunks_with_1_gap(self):
        sentence = build_sentence("w s w s w")
        significant_stems = ("w",)

        self.assertEqual(self.luhn.rate_sentence(sentence, significant_stems), 9/5)

    def test_three_chunks_with_2_gap(self):
        sentence = build_sentence("w s s w s s w")
        significant_stems = ("w",)

        self.assertEqual(self.luhn.rate_sentence(sentence, significant_stems), 9/7)

    def test_three_chunks_with_3_gap(self):
        sentence = build_sentence("w s s s w s s s w")
        significant_stems = ("w",)

        self.assertEqual(self.luhn.rate_sentence(sentence, significant_stems), 1)
