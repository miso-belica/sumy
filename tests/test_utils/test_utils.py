

import pytest

from sumy.utils import ItemsCount, get_stop_words, normalize_language, read_stop_words

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


@pytest.mark.parametrize("amount, expected_result", [
    ("0%", [0]),
    ("20%", [0, 1]),
    ("30%", [0, 1, 2]),
    ("35%", [0, 1, 2]),
    ("50%", [0, 1, 2, 3, 4]),
    ("100%", [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]),

    (False, []),
    (True, [0]),
    (3.5, [0, 1, 2]),
])
def test_supported_items_count(amount, expected_result):
    count = ItemsCount(amount)

    returned = count([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])

    assert returned == expected_result


def test_unsupported_items_count():
    count = ItemsCount("Hacker")

    with pytest.raises(ValueError):
        count([])


def test_items_count_with_unsupported_init_type():
    count = ItemsCount([])

    with pytest.raises(TypeError):
        count([])


@pytest.mark.parametrize("language, expected", [
    # ISO 639-1 codes
    ("fr", "french"),
    ("zh", "chinese"),
    ("sk", "slovak"),
    # ISO 639-3 codes
    ("fra", "french"),
    ("zho", "chinese"),
    ("slk", "slovak"),
    # ISO 639 names these "Modern Greek (1453-)", "Norwegian Bokmål" and "Norwegian Nynorsk"
    ("el", "greek"),
    ("ell", "greek"),
    ("nb", "norwegian"),
    ("nn", "norwegian"),
    # language names
    ("french", "french"),
    ("chinese", "chinese"),
    ("slovak", "slovak"),
])
def test_normalize_language(language, expected):
    assert normalize_language(language) == expected
