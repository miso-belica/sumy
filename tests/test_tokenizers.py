# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

import unittest

from sumy.nlp.tokenizers import Tokenizer


class TestTokenizer(unittest.TestCase):
    def test_missing_language(self):
        self.assertRaises(LookupError, Tokenizer, "klingon")

    def test_ensure_czech_tokenizer_available(self):
        tokenizer = Tokenizer("czech")
        self.assertEqual("czech", tokenizer.language)

        sentences = tokenizer.to_sentences("""
            Měl jsem sen, že toto je sen. Bylo to také zvláštní.
            Jakoby jsem plaval v moři rekurze.
        """)

        expected = (
            "Měl jsem sen, že toto je sen.",
            "Bylo to také zvláštní.",
            "Jakoby jsem plaval v moři rekurze.",
        )
        self.assertEqual(expected, sentences)

    def test_language_getter(self):
        tokenizer = Tokenizer("english")
        self.assertEqual("english", tokenizer.language)

    def test_tokenize_sentence(self):
        tokenizer = Tokenizer("english")
        words = tokenizer.to_words("I am a very nice sentence with comma, but..")

        expected = (
            "I", "am", "a", "very", "nice", "sentence",
            "with", "comma",
        )
        self.assertEqual(expected, words)

    def test_tokenize_sentences_with_abbreviations(self):
        tokenizer = Tokenizer("english")
        sentences = tokenizer.to_sentences("There are people who are weird, e.g. normal people. These people know you.")

        expected = ("There are people who are weird, e.g. normal people.", "These people know you.",)
        assert expected == sentences

    def test_tokenize_paragraph(self):
        tokenizer = Tokenizer("english")
        sentences = tokenizer.to_sentences("""
            I am a very nice sentence with comma, but..
            This is next sentence. "I'm bored", said Pepek.
            Ou jee, duffman is here.
        """)

        expected = (
            "I am a very nice sentence with comma, but..",
            "This is next sentence.",
            '"I\'m bored", said Pepek.',
            "Ou jee, duffman is here.",
        )
        self.assertEqual(expected, sentences)

    def test_slovak_alias_into_czech_tokenizer(self):
        tokenizer = Tokenizer("slovak")
        self.assertEqual(tokenizer.language, "slovak")

        sentences = tokenizer.to_sentences("""
            Je to veľmi fajn. Bodaj by nie.
            Ale na druhej strane čo je to oproti inému?
            To nechám na čitateľa.
        """)

        expected = (
            "Je to veľmi fajn.",
            "Bodaj by nie.",
            "Ale na druhej strane čo je to oproti inému?",
            "To nechám na čitateľa.",
        )
        self.assertEqual(expected, sentences)

    def test_tokenize_japanese_sentence(self):
        tokenizer = Tokenizer('japanese')
        self.assertEqual(tokenizer.language, 'japanese')

        sentence = 'この文章を、正しくトークン化したい。'
        expected = ('この', '文章', 'を', '正しく', 'トークン', '化', 'し', 'たい')
        self.assertEqual(expected, tokenizer.to_words(sentence))

    def test_tokenize_japanese_paragraph(self):
        tokenizer = Tokenizer('japanese')
        expected = (
            '１つ目の文章です。',
            'その次は何が来ますか？',
            '「２つ目の文章」です。'
        )
        paragraph = '１つ目の文章です。その次は何が来ますか？　「２つ目の文章」です。'
        self.assertEqual(expected, tokenizer.to_sentences(paragraph))

    def test_tokenize_chinese_sentence(self):
        tokenizer = Tokenizer('chinese')
        self.assertEqual(tokenizer.language, 'chinese')

        sentence = '好用的文档自动化摘要程序。'
        expected = ('好用', '的', '文档', '自动化', '摘要', '程序')
        self.assertEqual(expected, tokenizer.to_words(sentence))

    def test_tokenize_chinese_paragraph(self):
        tokenizer = Tokenizer('chinese')
        expected = (
            '我正在为这个软件添加中文支持。',
            '这个软件是用于文档摘要！',
            '这个软件支持网页和文本两种输入格式？'
        )

        paragraph = '我正在为这个软件添加中文支持。这个软件是用于文档摘要！这个软件支持网页和文本两种输入格式？'
        self.assertEqual(expected, tokenizer.to_sentences(paragraph))
