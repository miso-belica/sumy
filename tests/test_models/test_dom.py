# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import pytest

from sumy._compat import to_unicode
from sumy.models.dom import Paragraph, Sentence
from sumy.nlp.tokenizers import Tokenizer
from ..utils import build_document, build_document_from_string


def test_unique_words():
    document = build_document(
        ("Nějaký muž šel kolem naší zahrady", "Nějaký muž šel kolem vaší zahrady",),
        ("Už už abych taky šel",),
    )

    assert sorted(frozenset(document.words)) == [
        "Nějaký",
        "Už",
        "abych",
        "kolem",
        "muž",
        "naší",
        "taky",
        "už",
        "vaší",
        "zahrady",
        "šel",
    ]


def test_headings():
    document = build_document_from_string("""
        Nějaký muž šel kolem naší zahrady
        Nějaký jiný muž šel kolem vaší zahrady

        # Nová myšlenka
        Už už abych taky šel
    """)

    assert list(map(to_unicode, document.headings)) == ["Nová myšlenka"]


def test_sentences():
    document = build_document_from_string("""
        Nějaký muž šel kolem naší zahrady
        Nějaký jiný muž šel kolem vaší zahrady

        # Nová myšlenka
        Už už abych taky šel
    """)

    assert list(map(to_unicode, document.sentences)) == [
        "Nějaký muž šel kolem naší zahrady",
        "Nějaký jiný muž šel kolem vaší zahrady",
        "Už už abych taky šel",
    ]


def test_only_instances_of_sentence_allowed():
    document = build_document_from_string("""
        Nějaký muž šel kolem naší zahrady
        Nějaký jiný muž šel kolem vaší zahrady

        # Nová myšlenka
        Už už abych taky šel
    """)

    with pytest.raises(TypeError):
        Paragraph(list(document.sentences) + ["Last sentence"])


def test_empty_sentences_equal():
    sentence1 = Sentence("", Tokenizer("czech"))
    sentence2 = Sentence("", Tokenizer("czech"))

    assert sentence1 == sentence2


def test_same_sentences_equal():
    sentence1 = Sentence("word another.", Tokenizer("czech"))
    sentence2 = Sentence("word another.", Tokenizer("czech"))

    assert sentence1 == sentence2


def test_sentences_with_same_words_in_different_order_are_different():
    sentence1 = Sentence("word another", Tokenizer("czech"))
    sentence2 = Sentence("another word", Tokenizer("czech"))

    assert sentence1 != sentence2
