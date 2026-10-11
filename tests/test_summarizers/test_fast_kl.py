# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

import pytest
import numpy as np

import sumy.summarizers.fast_kl as fast_kl_module
from sumy.models.dom._sentence import Sentence
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.fast_kl import KLSummarizer
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


def test_numpy_not_installed():
    summarizer = KLSummarizer()

    numpy = fast_kl_module.np
    fast_kl_module.np = None

    with pytest.raises(ValueError):
        summarizer(build_document(), 10)

    fast_kl_module.np = numpy


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
    word_freq = np.zeros(len(words))
    word_to_ind = {word: index for index, word in enumerate(words)}
    freq = summarizer._compute_word_freq(words, word_freq, word_to_ind)

    assert np.all(freq == 1)

    words = ["one", "one", "two", "two"]
    word_freq = np.zeros(len(set(words)))
    word_to_ind = {word: index for index, word in enumerate(set(words))}
    freq = summarizer._compute_word_freq(words, word_freq, word_to_ind)

    assert np.all(freq == 2)


def test_joint_freq(summarizer):
    w1 = ["one", "two", "three", "four"]
    w2 = ["one", "two", "three", "four"]

    word_freq1 = np.zeros(len(w1))
    word_freq2 = np.zeros_like(word_freq1)
    word_to_ind = {word: index for index, word in enumerate(w1)}
    freq1 = summarizer._compute_word_freq(w1, word_freq1, word_to_ind)
    freq2 = summarizer._compute_word_freq(w1, word_freq2, word_to_ind)

    freq = summarizer._joint_freq(freq1, freq2, len(w1) + len(w2))

    assert np.all(freq == 1.0/4)

    w1 = ["one", "two", "three", "four"]
    w2 = ["one", "one", "three", "five"]

    vocabulary = set(w1).union(set(w2))
    word_freq1 = np.zeros(len(vocabulary))
    word_freq2 = np.zeros_like(word_freq1)
    word_to_ind = {word: index for index, word in enumerate(vocabulary)}
    freq1 = summarizer._compute_word_freq(w1, word_freq1, word_to_ind)
    freq2 = summarizer._compute_word_freq(w2, word_freq2, word_to_ind)

    freq = summarizer._joint_freq(freq1, freq2, len(w1) + len(w2))

    assert freq[word_to_ind["one"]] == 3.0/8
    assert freq[word_to_ind["two"]] == 1.0/8
    assert freq[word_to_ind["three"]] == 1.0/4
    assert freq[word_to_ind["four"]] == 1.0/8
    assert freq[word_to_ind["five"]] == 1.0/8


def test_kl_divergence(summarizer):
    EPS = 0.00001

    words = ["one", "two", "three"]
    word_freq1 = np.zeros(len(words))
    word_freq2 = np.zeros_like(word_freq1)
    word_to_ind = {word: index for index, word in enumerate(words)}

    word_freq1[word_to_ind["one"]] = 0.35
    word_freq1[word_to_ind["two"]] = 0.5
    word_freq1[word_to_ind["three"]] = 0.15

    word_freq2[word_to_ind["one"]] = 1.0/3.0
    word_freq2[word_to_ind["two"]] = 1.0/3.0
    word_freq2[word_to_ind["three"]] = 1.0/3.0

    missing_word_mask = np.repeat(True, 3)

    # This value comes from scipy.stats.entropy(w2_, w1_)
    # Note: the order of params is different
    kl_correct = 0.11475080798005841
    assert abs(summarizer._kl_divergence(word_freq1, word_freq2, missing_word_mask) - kl_correct) < EPS

    word_freq1[word_to_ind["one"]] = 0.1
    word_freq1[word_to_ind["two"]] = 0.2
    word_freq1[word_to_ind["three"]] = 0.7

    word_freq2[word_to_ind["one"]] = 0.2
    word_freq2[word_to_ind["two"]] = 0.4
    word_freq2[word_to_ind["three"]] = 0.4

    # This value comes from scipy.stats.entropy(w2_, w1_)
    # Note: the order of params is different
    kl_correct = 0.1920419931617981
    assert abs(summarizer._kl_divergence(word_freq1, word_freq2, missing_word_mask) - kl_correct) < EPS


def test_missing_word_in_document_during_kl_divergence_computation(summarizer):
    """
    Missing word should not affect the result.
    See https://github.com/miso-belica/sumy/issues/41
    """
    EPS = 0.00001

    words = ["one", "two", "three", "four"]
    summary_frequences = np.zeros(len(words))
    document_frequencies = np.repeat(summarizer.MISSING_WORD_VAL, len(words))
    word_to_ind = {word: index for index, word in enumerate(words)}

    summary_frequences[word_to_ind["one"]] = 0.35
    summary_frequences[word_to_ind["two"]] = 0.5
    summary_frequences[word_to_ind["three"]] = 0.15
    summary_frequences[word_to_ind["four"]] = 0.9

    document_frequencies[word_to_ind["one"]] = 1.0 / 3.0
    document_frequencies[word_to_ind["two"]] = 1.0 / 3.0
    document_frequencies[word_to_ind["three"]] = 1.0 / 3.0

    missing_word_mask = np.repeat(False, len(summary_frequences))
    missing_word_mask[word_to_ind["one"]] = True
    missing_word_mask[word_to_ind["two"]] = True
    missing_word_mask[word_to_ind["three"]] = True

    # This value comes from scipy.stats.entropy(w2_, w1_)
    # Note: the order of params is different
    kl_correct = 0.11475080798005841
    assert abs(summarizer._kl_divergence(summary_frequences, document_frequencies,
                                         missing_word_mask) - kl_correct) < EPS


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
