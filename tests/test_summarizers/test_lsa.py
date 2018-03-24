# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import pytest

import sumy.summarizers.lsa as lsa_module
from sumy._compat import to_unicode
from sumy.nlp.stemmers import Stemmer
from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.lsa import LsaSummarizer
from sumy.utils import get_stop_words
from ..utils import build_document, load_resource


def test_numpy_not_installed():
    summarizer = LsaSummarizer()

    numpy = lsa_module.numpy
    lsa_module.numpy = None

    with pytest.raises(ValueError):
        summarizer(build_document(), 10)

    lsa_module.numpy = numpy


def test_dictionary_without_stop_words():
    summarizer = LsaSummarizer()
    summarizer.stop_words = ["stop", "Halt", "SHUT", "HmMm"]

    document = build_document(
        ("stop halt shut hmmm", "Stop Halt Shut Hmmm",),
        ("StOp HaLt ShUt HmMm", "STOP HALT SHUT HMMM",),
        ("Some relevant sentence", "Some moRe releVant sentEnce",),
    )

    expected = frozenset(["some", "more", "relevant", "sentence"])
    dictionary = summarizer._create_dictionary(document)

    assert expected == frozenset(dictionary.keys())


def test_empty_document():
    document = build_document()
    summarizer = LsaSummarizer()

    sentences = summarizer(document, 10)
    assert len(sentences) == 0


def test_single_sentence():
    document = build_document(("I am the sentence you like",))
    summarizer = LsaSummarizer()
    summarizer.stopwords = ("I", "am", "the",)

    sentences = summarizer(document, 10)
    assert len(sentences) == 1
    assert to_unicode(sentences[0]) == "I am the sentence you like"


def test_document():
    document = build_document(
        ("I am the sentence you like", "Do you like me too",),
        ("This sentence is better than that above", "Are you kidding me",)
    )
    summarizer = LsaSummarizer()
    summarizer.stopwords = (
        "I", "am", "the", "you", "are", "me", "is", "than", "that", "this",
    )

    sentences = summarizer(document, 2)
    assert len(sentences) == 2
    assert to_unicode(sentences[0]) == "I am the sentence you like"
    assert to_unicode(sentences[1]) == "This sentence is better than that above"


def test_real_example():
    """Source: http://www.prevko.cz/dite/skutecne-pribehy-deti"""
    parser = PlaintextParser.from_string(
        load_resource("snippets/prevko.txt"),
        Tokenizer("czech")
    )
    summarizer = LsaSummarizer(Stemmer("czech"))
    summarizer.stop_words = get_stop_words("czech")

    sentences = summarizer(parser.document, 2)
    assert len(sentences) == 2


def test_article_example():
    """Source: http://www.prevko.cz/dite/skutecne-pribehy-deti"""
    parser = PlaintextParser.from_string(
        load_resource("articles/prevko_cz_1.txt"),
        Tokenizer("czech")
    )
    summarizer = LsaSummarizer(Stemmer("czech"))
    summarizer.stop_words = get_stop_words("czech")

    sentences = summarizer(parser.document, 20)
    assert len(sentences) == 20


def test_issue_5_svd_converges():
    """Source: https://github.com/miso-belica/sumy/issues/5"""
    pytest.skip("Can't reproduce the issue.")

    parser = PlaintextParser.from_string(
        load_resource("articles/svd_converges.txt"),
        Tokenizer("english")
    )
    summarizer = LsaSummarizer(Stemmer("english"))
    summarizer.stop_words = get_stop_words("english")

    sentences = summarizer(parser.document, 20)
    assert len(sentences) == 20
