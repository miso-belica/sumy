# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

import re
import string
import zipfile

import nltk

from .._compat import to_string, to_unicode, unicode
from ..utils import normalize_language


class DefaultWordTokenizer(object):
    """NLTK tokenizer"""
    def tokenize(self, text):
        return nltk.word_tokenize(text)


class HebrewWordTokenizer:
    """https://github.com/iddoberger/awesome-hebrew-nlp"""
    _TRANSLATOR = str.maketrans("", "", string.punctuation)

    @classmethod
    def tokenize(cls, text):
        try:
            from hebrew_tokenizer import tokenize
            from hebrew_tokenizer.groups import Groups
        except ImportError:
            raise ValueError("Hebrew tokenizer requires hebrew_tokenizer. Please, install it by command 'pip install hebrew_tokenizer'.")

        text = text.translate(cls._TRANSLATOR)
        return [
            word for token, word, _, _ in tokenize(text)
            if token in (Groups.HEBREW, Groups.HEBREW_1, Groups.HEBREW_2)
        ]
    

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


class KoreanSentencesTokenizer:
    def tokenize(self, text):
        try:
            from konlpy.tag import Kkma
        except ImportError as e:
            raise ValueError("Korean tokenizer requires konlpy. Please, install it by command 'pip install konlpy'.")
        kkma = Kkma()
        return kkma.sentences(text)


class KoreanWordTokenizer:
    def tokenize(self, text):
        try:
            from konlpy.tag import Kkma
        except ImportError as e:
            raise ValueError("Korean tokenizer requires konlpy. Please, install it by command 'pip install konlpy'.")
        kkma = Kkma()
        return kkma.nouns(text)


class GreekSentencesTokenizer:
    """Calls sent_tokenize for greek text, which doesn't split sentences
    on the english semicolon ';' (U+003B - https://unicode-table.com/en/003B/)
    or the greek question mark ';' (U+037E - https://unicode-table.com/en/037E/). 
    The regex below splits on both characters while retaining them in the sentence.
    This follows the logic of sent_tokenize().
    Regexpr Explanation: 
        (?<= -> look behind to see if there is, 
        [;;] -> any of these characters in the set, 
        ) end of look-behind
        {escape}s+ -> match and remove a single whitespace character one or more times.
    """
    @classmethod
    def tokenize(self, text):
        sentences = nltk.sent_tokenize(text, language='greek')
        sentences = (filter(None, re.split(r'(?<=[;;])\s+', sentence)) for sentence in sentences)
        return [sentence.strip() for sent_gen in sentences for sentence in sent_gen]


class ArabicWordTokenizer:
    def tokenize(self, text):
        try:
            from pyarabic.araby import tokenize
        except ImportError:
            raise ValueError("arabic tokenizer requires pyarabic. Please, install it by command 'pip install pyarabic'.")
        return tokenize(text)


class ArabicSentencesTokenizer:
    def tokenize(self, text):
        try:
            from pyarabic.araby import sentence_tokenize
        except ImportError:
            raise ValueError("arabic tokenizer requires pyarabic. Please, install it by command 'pip install pyarabic'.")
        return sentence_tokenize(text)


class Tokenizer(object):
    """Language dependent tokenizer of text document."""

    _WORD_PATTERN = re.compile(r"^[^\W\d_](?:[^\W\d_]|['-])*$", re.UNICODE)
    # feel free to contribute if you have better tokenizer for any of these languages :)
    LANGUAGE_ALIASES = {
        "slovak": "czech",
    }

    # improve tokenizer by adding specific abbreviations it has issues with
    # note the final point in these items must not be included
    LANGUAGE_EXTRA_ABREVS = {
        "english": ["e.g", "al", "i.e"],
        "german": ["al", "z.B", "Inc", "engl", "z. B", "vgl", "lat", "bzw", "S"],
        "ukrainian": ["ім.", "о.", "вул.", "просп.", "бул.", "пров.", "пл.", "г.", "р.", "див.", "п.", "с.", "м."],
        "greek": ["π.χ", "κ.α", "Α.Ε", "Ο.Ε", "κ.λπ", "κ.τ.λ", "λ.χ", "χμ", "χλμ", "Υ.Γ", "τηλ", "π.Χ", 
                  "μ.Χ", "π.μ", "μ.μ", "δηλ", "βλ", "κ.ο.κ", "σελ", "κεφ", "χιλ", "αρ"],
    }

    SPECIAL_SENTENCE_TOKENIZERS = {
        'ukrainian': nltk.RegexpTokenizer(r'[.!?…»]', gaps=True),
        'hebrew': nltk.RegexpTokenizer(r'\.\s+', gaps=True),
        'japanese': nltk.RegexpTokenizer('[^　！？。]*[！？。]'),
        'chinese': nltk.RegexpTokenizer('[^　！？。]*[！？。]'),
        'korean': KoreanSentencesTokenizer(),
        'greek': GreekSentencesTokenizer(),
        'arabic': ArabicSentencesTokenizer(),
    }

    SPECIAL_WORD_TOKENIZERS = {
        'hebrew': HebrewWordTokenizer(),
        'japanese': JapaneseWordTokenizer(),
        'chinese': ChineseWordTokenizer(),
        'korean': KoreanWordTokenizer(),
        'greek': nltk.RegexpTokenizer(r"[ ,;;.!?:-]+", gaps=True),
        'arabic': ArabicWordTokenizer(),
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
        except (LookupError, zipfile.BadZipfile) as e:
            raise LookupError(
                "NLTK tokenizers are missing or the language is not supported.\n"
                """Download them by following command: python -c "import nltk; nltk.download('punkt')"\n"""
                "Original error was:\n" + str(e)
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

    @staticmethod
    def _is_word(word):
        return bool(Tokenizer._WORD_PATTERN.match(word))
