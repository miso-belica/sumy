# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from sumy._compat import to_unicode
from sumy.summarizers.random import RandomSummarizer
from ..utils import build_document, build_document_from_string


def test_empty_document():
    document = build_document()
    summarizer = RandomSummarizer()

    sentences = summarizer(document, 10)
    assert len(sentences) == 0


def test_less_sentences_than_requested():
    document = build_document_from_string("""
        This is only one sentence.
    """)
    summarizer = RandomSummarizer()

    sentences = summarizer(document, 10)
    assert len(sentences) == 1
    assert to_unicode(sentences[0]) == "This is only one sentence."


def test_sentences_in_right_order():
    document = build_document_from_string("""
        # Heading one
        First sentence.
        Second sentence.
        Third sentence.
    """)
    summarizer = RandomSummarizer()

    sentences = summarizer(document, 4)
    assert len(sentences) == 3
    assert to_unicode(sentences[0]) == "First sentence."
    assert to_unicode(sentences[1]) == "Second sentence."
    assert to_unicode(sentences[2]) == "Third sentence."


def test_more_sentences_than_requested():
    document = build_document_from_string("""
        # Heading one
        First sentence.
        Second sentence.
        Third sentence.

        # Heading two
        I like sentences
        They are so wordy
        And have many many letters
        And are green in my editor
        But someone doesn't like them :(
    """)
    summarizer = RandomSummarizer()

    sentences = summarizer(document, 4)
    assert len(sentences) == 4
