# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from functools import partial

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


def test_less_than_10_words_should_be_returned():
    """https://github.com/miso-belica/sumy/issues/159"""
    document = build_document_from_string("""
        # Heading one
        First sentence.
        Second sentence.
        Third sentence.

        # Heading two
        I like sentences but this one is really long.
        They are so wordy
        And have many many letters
        And are green in my editor
        But someone doesn't like them :(
    """)
    summarizer = RandomSummarizer()

    def count(max_words, sentence_infos):
        results = []
        words_count = 0
        for info in sentence_infos:
            words_count += len(info.sentence.words)
            if words_count > max_words:
                return results
            else:
                results.append(info)

        return results

    sentences = summarizer(document, partial(count, 10))
    assert 0 < sum(len(s.words) for s in sentences) <= 10
