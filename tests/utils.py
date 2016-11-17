# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from os.path import dirname, join, abspath
from sumy.nlp.tokenizers import Tokenizer
from sumy._compat import to_string, to_unicode
from sumy.models.dom import ObjectDocumentModel, Paragraph, Sentence


_TOKENIZER = Tokenizer("czech")


def expand_resource_path(path):
    return join(abspath(dirname(__file__)), to_string("data"), to_string(path))


def load_resource(path):
    path = expand_resource_path(path)
    with open(path, "rb") as file:
        return to_unicode(file.read())


def build_document(*sets_of_sentences):
    paragraphs = []
    for sentences in sets_of_sentences:
        sentence_instances = []
        for sentence_as_string in sentences:
            sentence = build_sentence(sentence_as_string)
            sentence_instances.append(sentence)

        paragraphs.append(Paragraph(sentence_instances))

    return ObjectDocumentModel(paragraphs)


def build_document_from_string(string):
    sentences = []
    paragraphs = []

    for line in string.strip().splitlines():
        line = line.lstrip()
        if line.startswith("# "):
            sentences.append(build_sentence(line[2:], is_heading=True))
        elif not line:
            paragraphs.append(Paragraph(sentences))
            sentences = []
        else:
            sentences.append(build_sentence(line))

    paragraphs.append(Paragraph(sentences))
    return ObjectDocumentModel(paragraphs)


def build_sentence(sentence_as_string, is_heading=False):
    return Sentence(sentence_as_string, _TOKENIZER, is_heading)
