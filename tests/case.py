# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

import sys
import unittest

from os import pardir
from os.path import dirname, join, abspath
sys.path.insert(0, abspath(join(dirname(__file__), pardir)))

from sumy.document import Document, Paragraph, Sentence, Word


def build_document(*sets_of_sentences):
    paragraphs = []
    for sentences in sets_of_sentences:
        sentence_instances = []
        for sentence_as_string in sentences:
            sentence = build_sentence(sentence_as_string)
            sentence_instances.append(sentence)

        paragraphs.append(Paragraph(sentence_instances))

    return Document(paragraphs)


def build_sentence(sentence_as_string):
    return Sentence(map(Word, sentence_as_string.split()))


def to_words(*words):
    return tuple(map(Word, words))
