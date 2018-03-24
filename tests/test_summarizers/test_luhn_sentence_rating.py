# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import pytest

from sumy.summarizers.luhn import LuhnSummarizer
from ..utils import build_sentence


@pytest.fixture
def summarizer():
    return LuhnSummarizer()


@pytest.fixture
def sentence():
    return build_sentence("Nějaký muž šel kolem naší zahrady a žil pěkný život samotáře")


def test_significant_words(summarizer):
    summarizer.significant_percentage = 1/5
    words = summarizer._get_significant_words((
        "wa", "wb", "wc", "wd", "we", "wf", "wg", "wh", "wi", "wj",
        "wa", "wb",
    ))

    assert tuple(sorted(words)) == ("wa", "wb")


def test_stop_words_not_in_significant_words(summarizer):
    summarizer.stop_words = ["stop", "Halt", "SHUT", "HmMm"]
    words = summarizer._get_significant_words([
        "stop", "Stop", "StOp", "STOP",
        "halt", "Halt", "HaLt", "HALT",
        "shut", "Shut", "ShUt", "SHUT",
        "hmmm", "Hmmm", "HmMm", "HMMM",
        "some", "relevant", "word",
        "some", "more", "relevant", "word",
    ])

    assert tuple(sorted(words)) == ("relevant", "some", "word")


def test_zero_rating(summarizer, sentence):
    significant_stems = ()
    assert summarizer.rate_sentence(sentence, significant_stems) == 0


def test_single_word(summarizer, sentence):
    significant_stems = ("muž",)
    assert summarizer.rate_sentence(sentence, significant_stems) == 0


def test_single_word_before_end(summarizer, sentence):
    significant_stems = ("život",)
    assert summarizer.rate_sentence(sentence, significant_stems) == 0


def test_single_word_at_end(summarizer, sentence):
    significant_stems = ("samotáře",)
    assert summarizer.rate_sentence(sentence, significant_stems) == 0


def test_two_chunks_too_far(summarizer, sentence):
    significant_stems = ("šel", "žil",)
    assert summarizer.rate_sentence(sentence, significant_stems) == 0


def test_two_chunks_at_begin(summarizer, sentence):
    significant_stems = ("muž", "šel",)
    assert summarizer.rate_sentence(sentence, significant_stems) == 2


def test_two_chunks_before_end(summarizer, sentence):
    significant_stems = ("pěkný", "život",)
    assert summarizer.rate_sentence(sentence, significant_stems) == 2


def test_two_chunks_at_end(summarizer, sentence):
    significant_stems = ("pěkný", "samotáře",)
    assert summarizer.rate_sentence(sentence, significant_stems) == 4/3


def test_three_chunks_at_begin(summarizer, sentence):
    significant_stems = ("nějaký", "muž", "šel",)
    assert summarizer.rate_sentence(sentence, significant_stems) == 3


def test_three_chunks_at_end(summarizer, sentence):
    significant_stems = ("pěkný", "život", "samotáře",)
    assert summarizer.rate_sentence(sentence, significant_stems) == 3


def test_three_chunks_with_gaps(summarizer, sentence):
    significant_stems = ("muž", "šel", "zahrady",)
    assert summarizer.rate_sentence(sentence, significant_stems) == 9/5


def test_chunks_with_user_gap(summarizer, sentence):
    summarizer.max_gap_size = 6
    significant_stems = ("muž", "šel", "pěkný",)
    assert summarizer.rate_sentence(sentence, significant_stems) == 9/8


def test_three_chunks_with_1_gap(summarizer):
    sentence = build_sentence("w s w s w")
    significant_stems = ("w",)

    assert summarizer.rate_sentence(sentence, significant_stems) == 9/5


def test_three_chunks_with_2_gap(summarizer):
    sentence = build_sentence("w s s w s s w")
    significant_stems = ("w",)

    assert summarizer.rate_sentence(sentence, significant_stems) == 9/7


def test_three_chunks_with_3_gap(summarizer):
    sentence = build_sentence("w s s s w s s s w")
    significant_stems = ("w",)

    assert summarizer.rate_sentence(sentence, significant_stems) == 1
