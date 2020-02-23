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

    ratings = summarizer.rate_sentences(document)

    assert ratings == {
        document.sentences[0]: pytest.approx(0.29714368215098025),
        document.sentences[1]: pytest.approx(0.42683373199392705),
        document.sentences[2]: pytest.approx(0.2760223553913001),
    }
    assert pytest.approx(sum(ratings.values())) == 1


@pytest.mark.parametrize("sentences, expected_ratings", [
    (["", ""], [5.6953125e-06, 5.6953125e-06]),
    (["a", ""], [0.0013040590093013854, 0.00011418189740613421]),
    (["", "a"], [0.00011418189740613433, 0.0013040590093013854]),
    (["a", "a"], [0.49999995750000414, 0.49999995750000414]),
    (["a", "b"], [0.49999995750000414, 0.49999995750000414]),
    (["b", "a"], [0.49999995750000414, 0.49999995750000414]),
])
def test_rating_with_zero_or_single_words_in_sentences(sentences, expected_ratings):
    """
    This is an edge-case test when the sentence(s) have only one word or even zero words.
    This test makes me sure the logic will not break when such a case is encountered.
    """
    document = build_document(sentences)
    summarizer = TextRankSummarizer()

    ratings = summarizer.rate_sentences(document)

    assert ratings == {
        document.sentences[0]: pytest.approx(expected_ratings[0]),
        document.sentences[1]: pytest.approx(expected_ratings[1]),
    }
