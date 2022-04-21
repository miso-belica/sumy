# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import sys

import pytest

from sumy.nlp.tokenizers import Tokenizer


def test_missing_language():
    with pytest.raises(LookupError):
        Tokenizer("klingon")


def test_ensure_czech_tokenizer_available():
    tokenizer = Tokenizer("czech")
    assert "czech" == tokenizer.language

    sentences = tokenizer.to_sentences("""
        Měl jsem sen, že toto je sen. Bylo to také zvláštní.
        Jakoby jsem plaval v moři rekurze.
    """)

    expected = (
        "Měl jsem sen, že toto je sen.",
        "Bylo to také zvláštní.",
        "Jakoby jsem plaval v moři rekurze.",
    )
    assert expected == sentences


def test_language_getter():
    tokenizer = Tokenizer("english")
    assert "english" == tokenizer.language


@pytest.mark.parametrize("language, sentence, expected_words", [
    (
        "english",
        "I am a very nice sentence with comma, but..",
        ("I", "am", "a", "very", "nice", "sentence", "with", "comma", "but"),
    ),
    (
        "english",
        "I am doing sugar-free data-mining for Peter's study - vega punk.",
        ("I", "am", "doing", "sugar-free", "data-mining", "for", "Peter", "study", "vega", "punk"),
    ),
    (
        "japanese",
        "この文章を、正しくトークン化したい。",
        ("この", "文章", "を", "正しく", "トークン", "化", "し", "たい"),
    ),
    (
        "chinese",
        "好用的文档自动化摘要程序",
        ("好用", "的", "文档", "自动化", "摘要", "程序"),
    ),
    pytest.param(
        "korean",
        "대학에서 DB, 통계학, 이산수학 등을 배웠지만...",
        ("대학", "통계학", "이산", "이산수학", "수학", "등"),
        marks=pytest.mark.skipif(sys.version_info < (3,), reason="JPype1 from konlpy does not support Python 2 anymore")
    ),
    (
     "greek",
     "Ποιό είναι το κείμενο; Αυτό εδώ - και είναι έτοιμο! Τέλεια. Το στέλνω...",
     ('Ποιό', 'είναι', 'το', 'κείμενο', 'Αυτό', 'εδώ', 'και', 'είναι', 'έτοιμο', 'Τέλεια', 'Το', 'στέλνω'),
    ),
])
def test_tokenize_sentence_to_words(language, sentence, expected_words):
    tokenizer = Tokenizer(language)

    words = tokenizer.to_words(sentence)

    assert words == expected_words
    assert tokenizer.language == language


def test_tokenize_sentences_with_abbreviations():
    tokenizer = Tokenizer("english")
    sentences = tokenizer.to_sentences("There are people who are weird, e.g. normal people. These people know you.")

    expected = ("There are people who are weird, e.g. normal people.", "These people know you.",)
    assert expected == sentences


def test_tokenize_paragraph():
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
    assert expected == sentences


def test_slovak_alias_into_czech_tokenizer():
    tokenizer = Tokenizer("slovak")
    assert tokenizer.language == "slovak"

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
    assert expected == sentences


def test_tokenize_japanese_paragraph():
    tokenizer = Tokenizer('japanese')
    expected = (
        '１つ目の文章です。',
        'その次は何が来ますか？',
        '「２つ目の文章」です。'
    )
    paragraph = '１つ目の文章です。その次は何が来ますか？　「２つ目の文章」です。'
    assert expected == tokenizer.to_sentences(paragraph)


def test_tokenize_chinese_paragraph():
    tokenizer = Tokenizer('chinese')
    expected = (
        '我正在为这个软件添加中文支持。',
        '这个软件是用于文档摘要！',
        '这个软件支持网页和文本两种输入格式？'
    )

    paragraph = '我正在为这个软件添加中文支持。这个软件是用于文档摘要！这个软件支持网页和文本两种输入格式？'
    assert expected == tokenizer.to_sentences(paragraph)


@pytest.mark.skipif(sys.version_info < (3,), reason="JPype1 from konlpy does not support Python 2 anymore")
def test_tokenize_korean_paragraph():
    tokenizer = Tokenizer('korean')
    expected = (
        '회사 동료 분들과 다녀왔는데 분위기도 좋고 음식도 맛있었어요',
        '다만, 강남 토끼 정이 강남 쉑쉑 버거 골목길로 쭉 올라가야 하는데 다들 쉑쉑버거의 유혹에 넘어갈 뻔 했답니다',
        '강남 역 맛 집 토끼정의 외부 모습.'
    )

    paragraph = '회사 동료 분들과 다녀왔는데 분위기도 좋고 음식도 맛있었어요 다만, 강남 토끼정이 강남 쉑쉑버거 골목길로 쭉 올라가야 하는데 다들 쉑쉑버거의 유혹에 넘어갈 뻔 했답니다 강남역 맛집 토끼정의 외부 모습.'
    assert expected == tokenizer.to_sentences(paragraph)


def test_tokenize_greek_paragraph():
    tokenizer = Tokenizer('greek')
    expected = (
        'Ποιό είναι το κείμενο;',
        'Αυτό εδώ - και είναι έτοιμο!',
        'Τέλεια.',
        'Το στέλνω...'
    )

    paragraph = 'Ποιό είναι το κείμενο; Αυτό εδώ - και είναι έτοιμο! Τέλεια. Το στέλνω...'
    assert expected == tokenizer.to_sentences(paragraph)