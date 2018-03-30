# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import pytest

from sumy.utils import get_stop_words, read_stop_words, ItemsCount, \
    normalize_language
from ..utils import expand_resource_path


def test_ok_stop_words_language():
    stop_words = get_stop_words("french")
    assert len(stop_words) > 1


def test_missing_stop_words_language():
    with pytest.raises(LookupError):
        get_stop_words("klingon")


def test_ok_custom_stopwords_file():
    stop_words = read_stop_words(expand_resource_path("stopwords/language.txt"))
    assert len(stop_words) == 4


def test_custom_stop_words_file_not_found():
    with pytest.raises(IOError):
        read_stop_words(expand_resource_path("stopwords/klingon.txt"))


def test_percentage_items_count():
    count = ItemsCount("20%")
    returned = count([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    assert returned == [0, 1]

    count = ItemsCount("100%")
    returned = count([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    assert returned == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    count = ItemsCount("50%")
    returned = count([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    assert returned == [0, 1, 2, 3, 4]

    count = ItemsCount("30%")
    returned = count([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    assert returned == [0, 1, 2]

    count = ItemsCount("35%")
    returned = count([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    assert returned == [0, 1, 2]


def test_float_items_count():
    count = ItemsCount(3.5)
    returned = count([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    assert returned == [0, 1, 2]

    count = ItemsCount(True)
    returned = count([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    assert returned == [0]

    count = ItemsCount(False)
    returned = count([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    assert returned == []


def test_unsupported_items_count():
    count = ItemsCount("Hacker")

    with pytest.raises(ValueError):
        count([])


def test_normalize_language_with_alpha_2_code():
    assert normalize_language("fr") == "french"
    assert normalize_language("zh") == "chinese"
    assert normalize_language("sk") == "slovak"


def test_normalize_language_with_alpha_3_code():
    assert normalize_language("fra") == "french"
    assert normalize_language("zho") == "chinese"
    assert normalize_language("slk") == "slovak"


def test_normalize_language_with_language_name():
    assert normalize_language("french") == "french"
    assert normalize_language("chinese") == "chinese"
    assert normalize_language("slovak") == "slovak"
