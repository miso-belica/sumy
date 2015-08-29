# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

import math
import numpy
import pytest
import sumy.summarizers.lex_rank as lex_rank_module

from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.stemmers.czech import stem_word
from sumy.nlp.tokenizers import Tokenizer
from sumy.utils import get_stop_words
from ..utils import build_document, load_resource


def test_numpy_not_installed():
    summarizer = LexRankSummarizer()

    numpy = lex_rank_module.numpy
    lex_rank_module.numpy = None

    with pytest.raises(ValueError):
        summarizer(build_document(), 10)

    lex_rank_module.numpy = numpy


def test_tf_metrics():
    summarizer = LexRankSummarizer()

    sentences = [
        ("this", "sentence", "is", "simple", "sentence"),
        ("this", "is", "simple", "sentence", "yes", "is", "too", "too", "too"),
    ]
    metrics = summarizer._compute_tf(sentences)

    expected = [
        {"this": 1/2, "is": 1/2, "simple": 1/2, "sentence": 1.0},
        {"this": 1/3, "is": 2/3, "yes": 1/3, "simple": 1/3, "sentence": 1/3, "too": 1.0},
    ]
    assert expected == metrics


def test_idf_metrics():
    summarizer = LexRankSummarizer()

    sentences = [
        ("this", "sentence", "is", "simple", "sentence",),
        ("this", "is", "simple", "sentence", "yes", "is", "too", "too", "too",),
        ("not", "every", "sentence", "makes", "me", "happy",),
        ("yes",),
        (),
        ("every", "day", "is", "happy", "day",),
    ]
    metrics = summarizer._compute_idf(sentences)

    expected = {
        "this": math.log(6/3),
        "is": math.log(6/4),
        "yes": math.log(6/3),
        "simple": math.log(6/3),
        "sentence": math.log(6/4),
        "too": math.log(6/2),
        "not": math.log(6/2),
        "every": math.log(6/3),
        "makes": math.log(6/2),
        "me": math.log(6/2),
        "happy": math.log(6/3),
        "day": math.log(6/2),
    }
    assert expected == metrics


def test_modified_cosine_computation():
    summarizer = LexRankSummarizer()

    sentence1 = ["this", "sentence", "is", "simple", "sentence"]
    tf1 = {"this": 1/2, "sentence": 1.0, "is": 1/2, "simple": 1/2}
    sentence2 = ["this", "is", "simple", "sentence", "yes", "is", "too", "too"]
    tf2 = {"this": 1/2, "is": 1.0, "simple": 1/2, "sentence": 1/2, "yes": 1/2, "too": 1.0}
    idf = {
        "this": 2/2,
        "sentence": 2/2,
        "is": 2/2,
        "simple": 2/2,
        "yes": 2/1,
        "too": 2/1,
    }

    numerator = sum(tf1[t]*tf2[t]*idf[t]**2 for t in ["this", "sentence", "is", "simple"])
    denominator1 = math.sqrt(sum((tf1[t]*idf[t])**2 for t in sentence1))
    denominator2 = math.sqrt(sum((tf2[t]*idf[t])**2 for t in sentence2))

    expected = numerator / (denominator1 * denominator2)
    cosine = summarizer._compute_cosine(sentence1, sentence2, tf1, tf2, idf)
    assert expected == cosine


def test_article_example():
    """Source: http://www.prevko.cz/dite/skutecne-pribehy-deti"""
    parser = PlaintextParser.from_string(
        load_resource("articles/prevko_cz_1.txt"),
        Tokenizer("czech")
    )
    summarizer = LexRankSummarizer(stem_word)
    summarizer.stop_words = get_stop_words("czech")

    sentences = summarizer(parser.document, 20)
    assert len(sentences) == 20


def test_document_is_all_in_upper_case():
    """
    When all words is in upper case Plaintext parser first line as heading and
    LexRank algorithm raises exception "ZeroDivisionError: float division by zero"
    because there is no sentence to summarize.
    See https://github.com/miso-belica/sumy/issues/25
    """
    parser = PlaintextParser.from_string(
        "JUST WRITING SOME TEXT. TO TEST CASE. WITH ZERO SENTENCES RETURNED. FROM TOKENIZER.",
        Tokenizer("english")
    )
    summarizer = LexRankSummarizer(stem_word)
    summarizer.stop_words = get_stop_words("english")

    sentences = summarizer(parser.document, 20)
    assert len(sentences) == 0


def test_power_method_should_return_different_scores_for_sentences():
    """See https://github.com/miso-belica/sumy/issues/26"""
    matrix = numpy.array([
        [0.1, 0.2, 0.3, 0.6, 0.9],
        [0.45, 0, 0.3, 0.6, 0],
        [0.5, 0.6, 0.3, 1, 0.9],
        [0.7, 0, 0, 0.6, 0],
        [0.5, 0.123, 0, 0.111, 0.9],
    ])
    scores = LexRankSummarizer.power_method(matrix, LexRankSummarizer.epsilon)

    assert len(frozenset(scores.tolist())) > 1
