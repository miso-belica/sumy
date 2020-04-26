# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

import pytest

from sumy.models.dom._sentence import Sentence
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.kl import KLSummarizer
from ..utils import build_document


@pytest.fixture
def empty_stop_words():
    return []


@pytest.fixture
def stop_words():
    return ["the", "and", "i"]


@pytest.fixture
def summarizer(stop_words):
    summarizer = KLSummarizer()
    summarizer.stop_words = stop_words
    return summarizer


def test_empty_document(summarizer):
    document = build_document()
    returned = summarizer(document, 10)

    assert len(returned) == 0


def test_single_sentence(summarizer):
    s = Sentence("I am one slightly longer sentence.", Tokenizer("english"))
    document = build_document([s])

    returned = summarizer(document, 10)

    assert len(returned) == 1


def test_compute_word_freq(summarizer):
    words = ["one", "two", "three", "four"]
    freq = summarizer._compute_word_freq(words)

    assert freq.get("one", 0) == 1
    assert freq.get("two", 0) == 1
    assert freq.get("three", 0) == 1
    assert freq.get("four", 0) == 1

    words = ["one", "one", "two", "two"]
    freq = summarizer._compute_word_freq(words)

    assert freq.get("one", 0) == 2
    assert freq.get("two", 0) == 2
    assert freq.get("three", 0) == 0


def test_joint_freq(summarizer):
    w1 = ["one", "two", "three", "four"]
    w2 = ["one", "two", "three", "four"]
    freq = summarizer._joint_freq(w1, w2)

    assert freq["one"] == 1.0/4
    assert freq["two"] == 1.0/4
    assert freq["three"] == 1.0/4
    assert freq["four"] == 1.0/4

    w1 = ["one", "two", "three", "four"]
    w2 = ["one", "one", "three", "five"]
    freq = summarizer._joint_freq(w1, w2)

    assert freq["one"] == 3.0/8
    assert freq["two"] == 1.0/8
    assert freq["three"] == 1.0/4
    assert freq["four"] == 1.0/8
    assert freq["five"] == 1.0/8


def test_kl_divergence(summarizer):
    EPS = 0.00001

    w1 = {"one": 0.35, "two": 0.5, "three": 0.15}
    w2 = {"one": 1.0/3.0, "two": 1.0/3.0, "three": 1.0/3.0}

    # This value comes from scipy.stats.entropy(w2_, w1_)
    # Note: the order of params is different
    kl_correct = 0.11475080798005841
    assert abs(summarizer._kl_divergence(w1, w2) - kl_correct) < EPS

    w1 = {"one": 0.1, "two": 0.2, "three": 0.7}
    w2 = {"one": 0.2, "two": 0.4, "three": 0.4}

    # This value comes from scipy.stats.entropy(w2_, w1_)
    # Note: the order of params is different
    kl_correct = 0.1920419931617981
    assert abs(summarizer._kl_divergence(w1, w2) - kl_correct) < EPS


def test_missing_word_in_document_during_kl_divergence_computation(summarizer):
    """
    Missing word should not affect the result.
    See https://github.com/miso-belica/sumy/issues/41
    """
    EPS = 0.00001

    summary_frequences = {"one": 0.35, "two": 0.5, "three": 0.15, "four": 0.9}
    document_frequencies = {"one": 1.0/3.0, "two": 1.0/3.0, "three": 1.0/3.0}

    # This value comes from scipy.stats.entropy(w2_, w1_)
    # Note: the order of params is different
    kl_correct = 0.11475080798005841
    assert abs(summarizer._kl_divergence(summary_frequences, document_frequencies) - kl_correct) < EPS


def test_tf_idf_metric_should_be_real_number():
    """https://github.com/miso-belica/sumy/issues/41"""
    summarizer = KLSummarizer()
    frequencies = summarizer.compute_tf([Sentence("There are five words, jop.", Tokenizer("english"))])

    assert frequencies == {
        "there": 0.2,
        "are": 0.2,
        "five": 0.2,
        "words": 0.2,
        "jop": 0.2,
    }


def test_the_sentences_should_be_in_different_order(summarizer):
    """https://github.com/miso-belica/sumy/issues/146"""
    paragraphs = [
        ["This is 1st sentence.", "This is 2nd sentence."],
        ["This is 3rd sentence.", "This is 4th sentence."],
        ["This is 5th sentence."],
    ]
    document = build_document(*paragraphs)
    reversed_document = build_document(*(reversed(p) for p in reversed(paragraphs)))

    sentences = summarizer(document, "100%")
    reversed_sentences = summarizer(reversed_document, "100%")

    assert tuple(reversed(sentences)) == reversed_sentences
