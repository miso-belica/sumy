# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from sumy._compat import to_unicode
from sumy.nlp.stemmers.czech import stem_word
from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.luhn import LuhnSummarizer
from sumy.utils import get_stop_words
from ..utils import build_document


def test_empty_document():
    document = build_document()
    summarizer = LuhnSummarizer()

    returned = summarizer(document, 10)
    assert len(returned) == 0


def test_single_sentence():
    document = build_document(("Já jsem jedna věta",))
    summarizer = LuhnSummarizer()
    summarizer.stop_words = ("já", "jsem",)

    returned = summarizer(document, 10)
    assert len(returned) == 1


def test_two_sentences():
    document = build_document(("Já jsem 1. věta", "A já ta 2. vítězná výhra"))
    summarizer = LuhnSummarizer()
    summarizer.stop_words = ("já", "jsem", "a", "ta",)

    returned = summarizer(document, 10)
    assert list(map(to_unicode, returned)) == [
        "Já jsem 1. věta",
        "A já ta 2. vítězná výhra",
    ]


def test_two_sentences_but_one_winner():
    document = build_document((
        "Já jsem 1. vítězná ta věta",
        "A já ta 2. vítězná věta"
    ))
    summarizer = LuhnSummarizer()
    summarizer.stop_words = ("já", "jsem", "a", "ta",)

    returned = summarizer(document, 1)
    assert list(map(to_unicode, returned)) == [
        "A já ta 2. vítězná věta",
    ]


def test_three_sentences():
    document = build_document((
        "wa s s s wa s s s wa",
        "wb s wb s wb s s s s s s s s s wb",
        "wc s s wc s s wc",
    ))
    summarizer = LuhnSummarizer()
    summarizer.stop_words = ("s",)

    returned = summarizer(document, 1)
    assert list(map(to_unicode, returned)) == [
        "wb s wb s wb s s s s s s s s s wb",
    ]

    returned = summarizer(document, 2)
    assert list(map(to_unicode, returned)) == [
        "wb s wb s wb s s s s s s s s s wb",
        "wc s s wc s s wc",
    ]

    returned = summarizer(document, 3)
    assert list(map(to_unicode, returned)) == [
        "wa s s s wa s s s wa",
        "wb s wb s wb s s s s s s s s s wb",
        "wc s s wc s s wc",
    ]


def test_various_words_with_significant_percentage():
    document = build_document((
        "1 a",
        "2 b b",
        "3 c c c",
        "4 d d d",
        "5 z z z z",
        "6 e e e e e",
    ))
    summarizer = LuhnSummarizer()
    summarizer.stop_words = ("1", "2", "3", "4", "5", "6")

    returned = summarizer(document, 1)
    assert list(map(to_unicode, returned)) == [
        "6 e e e e e",
    ]

    returned = summarizer(document, 2)
    assert list(map(to_unicode, returned)) == [
        "5 z z z z",
        "6 e e e e e",
    ]

    returned = summarizer(document, 3)
    assert list(map(to_unicode, returned)) == [
        "3 c c c",
        "5 z z z z",
        "6 e e e e e",
    ]


def test_real_example():
    parser = PlaintextParser.from_string(
        "Jednalo se o případ chlapce v 6. třídě, který měl problémy s učením. "
        "Přerostly až v reparát z jazyka na konci školního roku. "
        "Nedopadl bohužel dobře a tak musel opakovat 6. třídu, což se chlapci ani trochu nelíbilo. "
        "Připadal si, že je mezi malými dětmi a realizoval se tím, že si ve třídě "
        "o rok mladších dětí budoval vedoucí pozici. "
        "Dost razantně. Fyzickou převahu měl, takže to nedalo až tak moc práce.",
        Tokenizer("czech")
    )
    summarizer = LuhnSummarizer(stem_word)
    summarizer.stop_words = get_stop_words("czech")

    returned = summarizer(parser.document, 2)
    assert list(map(to_unicode, returned)) == [
        "Jednalo se o případ chlapce v 6. třídě, který měl problémy s učením.",
        "Připadal si, že je mezi malými dětmi a realizoval se tím, že si ve třídě o rok mladších dětí budoval vedoucí pozici.",
    ]
