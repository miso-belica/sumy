# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

import pytest

import sumy.summarizers.text_rank as text_rank_module
from sumy.summarizers.text_rank import TextRankSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy._compat import to_unicode
from ..utils import build_document


def test_numpy_not_installed():
    summarizer = TextRankSummarizer()

    numpy = text_rank_module.numpy
    text_rank_module.numpy = None

    with pytest.raises(ValueError):
        summarizer(build_document(), 10)

    text_rank_module.numpy = numpy


def test_empty_document():
    document = build_document()
    summarizer = TextRankSummarizer(Stemmer("english"))

    returned = summarizer(document, 10)
    assert len(returned) == 0


def test_single_sentence():
    document = build_document(("I am one sentence",))
    summarizer = TextRankSummarizer()
    summarizer.stop_words = ("I", "am",)

    returned = summarizer(document, 10)
    assert len(returned) == 1


def test_two_sentences():
    document = build_document(("I am that 1. sentence", "And I am 2. winning prize"))
    summarizer = TextRankSummarizer()
    summarizer.stop_words = ("I", "am", "and", "that",)

    returned = summarizer(document, 10)
    assert len(returned) == 2
    assert to_unicode(returned[0]) == "I am that 1. sentence"
    assert to_unicode(returned[1]) == "And I am 2. winning prize"


def test_stop_words_correctly_removed():
    summarizer = TextRankSummarizer()
    summarizer.stop_words = ["stop", "Halt", "SHUT", "HmMm"]

    document = build_document(
        ("stop halt shut hmmm", "Stop Halt Shut Hmmm",),
        ("StOp HaLt ShUt HmMm", "STOP HALT SHUT HMMM",),
        ("Some relevant sentence", "Some moRe releVant sentEnce",),
    )
    sentences = document.sentences

    expected = []
    returned = summarizer._to_words_set(sentences[0])
    assert expected == returned
    returned = summarizer._to_words_set(sentences[1])
    assert expected == returned
    returned = summarizer._to_words_set(sentences[2])
    assert expected == returned
    returned = summarizer._to_words_set(sentences[3])
    assert expected == returned

    expected = ["some", "relevant", "sentence"]
    returned = summarizer._to_words_set(sentences[4])
    assert expected == returned
    expected = ["some", "more", "relevant", "sentence"]
    returned = summarizer._to_words_set(sentences[5])
    assert expected == returned


def test_sentences_rating():
    document = build_document([
        "a c e g",
        "a b c d e f g",
        "b d f",
    ])
    summarizer = TextRankSummarizer()
    summarizer.stop_words = ["I", "am", "and", "that"]

    ratings = summarizer.rate_sentences(document)
    assert len(ratings) == 3
    assert pytest.approx(sum(ratings.values())) == 1
