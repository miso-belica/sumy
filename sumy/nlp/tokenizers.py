# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

import re
import zipfile
import nltk

from .._compat import to_string, to_unicode, unicode
from ..utils import normalize_language


class DefaultWordTokenizer(object):
    def tokenize(self, text):
        return nltk.word_tokenize(text)


class JapaneseWordTokenizer:
    def tokenize(self, text):
        try:
            import tinysegmenter
        except ImportError as e:
            raise ValueError("Japanese tokenizer requires tinysegmenter. Please, install it by command 'pip install tinysegmenter'.")
        segmenter = tinysegmenter.TinySegmenter()
        return segmenter.tokenize(text)


class ChineseWordTokenizer:
    def tokenize(self, text):
        try:
            import jieba
        except ImportError as e:
            raise ValueError("Chinese tokenizer requires jieba. Please, install it by command 'pip install jieba'.")
        return jieba.cut(text)


class Tokenizer(object):
    """Language dependent tokenizer of text document."""

    _WORD_PATTERN = re.compile(r"^[^\W\d_]+$", re.UNICODE)
    # feel free to contribute if you have better tokenizer for any of these languages :)
    LANGUAGE_ALIASES = {
        "slovak": "czech",
    }

    # improve tokenizer by adding specific abbreviations it has issues with
    # note the final point in these items must not be included
    LANGUAGE_EXTRA_ABREVS = {
        "english": ["e.g", "al", "i.e"],
        "german": ["al", "z.B", "Inc", "engl", "z. B", "vgl", "lat", "bzw", "S"],
    }

    SPECIAL_SENTENCE_TOKENIZERS = {
        'japanese': nltk.RegexpTokenizer('[^　！？。]*[！？。]'),
        'chinese': nltk.RegexpTokenizer('[^　！？。]*[！？。]')
    }

    SPECIAL_WORD_TOKENIZERS = {
        'japanese': JapaneseWordTokenizer(),
        'chinese': ChineseWordTokenizer(),
    }

    def __init__(self, language):
        language = normalize_language(language)
        self._language = language

        tokenizer_language = self.LANGUAGE_ALIASES.get(language, language)
        self._sentence_tokenizer = self._get_sentence_tokenizer(tokenizer_language)
        self._word_tokenizer = self._get_word_tokenizer(tokenizer_language)

    @property
    def language(self):
        return self._language

    def _get_sentence_tokenizer(self, language):
        if language in self.SPECIAL_SENTENCE_TOKENIZERS:
            return self.SPECIAL_SENTENCE_TOKENIZERS[language]
        try:
            path = to_string("tokenizers/punkt/%s.pickle") % to_string(language)
            return nltk.data.load(path)
        except (LookupError, zipfile.BadZipfile):
            raise LookupError(
                "NLTK tokenizers are missing. Download them by following command: "
                '''python -c "import nltk; nltk.download('punkt')"'''
            )

    def _get_word_tokenizer(self, language):
        if language in self.SPECIAL_WORD_TOKENIZERS:
            return self.SPECIAL_WORD_TOKENIZERS[language]
        else:
            return DefaultWordTokenizer()

    def to_sentences(self, paragraph):
        if hasattr(self._sentence_tokenizer, '_params'):
            extra_abbreviations = self.LANGUAGE_EXTRA_ABREVS.get(self._language, [])
            self._sentence_tokenizer._params.abbrev_types.update(extra_abbreviations)
        sentences = self._sentence_tokenizer.tokenize(to_unicode(paragraph))
        return tuple(map(unicode.strip, sentences))

    def to_words(self, sentence):
        words = self._word_tokenizer.tokenize(to_unicode(sentence))
        return tuple(filter(self._is_word, words))

    def _is_word(self, word):
        return bool(Tokenizer._WORD_PATTERN.search(word))
