# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

import sys
import nltk

from readability.readable import Article
from .._compat import urllib, to_unicode, to_string
from ..utils import cached_property
from ..document import Sentence, Paragraph, Document
from .parser import DocumentParser


class HtmlParser(DocumentParser):
    """Parser of text from HTML format into DOM."""

    @classmethod
    def from_string(cls, string, url, tokenizer):
        return cls(string, url, tokenizer)

    @classmethod
    def from_file(cls, file_path, url, tokenizer):
        with open(file_path, "rb") as file:
            return cls(file.read(), url, tokenizer)

    @classmethod
    def from_url(cls, url, tokenizer):
        response = urllib.urlopen(url)
        data = response.read()
        response.close()

        return cls(data, url, tokenizer)

    def __init__(self, html_content, url, tokenizer):
        super(HtmlParser, self).__init__(tokenizer)
        self._article = Article(html_content, to_unicode(url))

    @cached_property
    def document(self):
        # "a", "abbr", "acronym", "b", "big", "blink", "blockquote", "cite", "code",
        # "dd", "del", "dfn", "dir", "dl", "dt", "em", "h", "h1", "h2", "h3", "h4",
        # "h5", "h6", "i", "ins", "kbd", "li", "marquee", "menu", "ol", "pre", "q",
        # "s", "samp", "strike", "strong", "sub", "sup", "tt", "u", "ul", "var",

        annotated_text = self._article.main_text

        paragraphs = []
        for paragraph in annotated_text:
            sentences = []

            for text, annotations in paragraph:
                if annotations and ("h1" in annotations or "h2" in annotations or "h3" in annotations):
                    words = self.tokenize_words(text)
                    sentences.append(Sentence(words, is_heading=True))
                else:
                    words = map(self.tokenize_words, self.tokenize_sentences(text))
                    sentences.extend(map(Sentence, words))

            paragraphs.append(Paragraph(sentences))

        return Document(paragraphs)
