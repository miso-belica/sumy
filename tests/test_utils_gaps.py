"""Gap coverage for sumy.utils.

The upstream suite covers the common ItemsCount forms, one missing
stop-words language and the alpha_2/alpha_3/name forms of
normalize_language. These tests pin the remaining edges: negative and
over-100% counts, whitespace-tolerant plain counts, the repr, the
spaces-only-line quirk of parse_stop_words, upper-case and dashed
language codes, and the cached_property memoisation contract.
"""

import pytest

from sumy.parsers.parser import DocumentParser
from sumy.utils import (
    ItemsCount,
    cached_property,
    expand_resource_path,
    get_stop_words,
    normalize_language,
    parse_stop_words,
)


def test_items_count_negative_slices_from_the_end():
    # A negative count is not clamped: it goes through plain sequence
    # slicing, so -1 drops the last (lowest-rated, after sorting) item.
    assert ItemsCount(-1)([0, 1, 2, 3, 4]) == [0, 1, 2, 3]
    assert ItemsCount(-2)([0, 1, 2, 3, 4]) == [0, 1, 2]


def test_items_count_over_100_percent_returns_everything():
    assert ItemsCount("150%")([1, 2, 3]) == [1, 2, 3]


def test_items_count_plain_number_string_with_trailing_space():
    # Not a percentage: int() tolerates surrounding whitespace.
    assert ItemsCount("3 ")(list(range(10))) == [0, 1, 2]


@pytest.mark.parametrize(
    "count, expected",
    [
        (3, "<ItemsCount: 3>"),
        ("20%", "<ItemsCount: '20%'>"),
        (0, "<ItemsCount: 0>"),
    ],
)
def test_items_count_repr(count, expected):
    assert repr(ItemsCount(count)) == expected


def test_parse_stop_words_spaces_only_line_becomes_empty_string():
    # The filter tests the raw line, the rstrip happens afterwards, so a
    # line of only spaces survives as the empty string in the set.
    assert parse_stop_words(b"the\n\n  \nand\n") == frozenset({"the", "and", ""})


def test_parse_stop_words_truly_empty_lines_are_dropped():
    assert parse_stop_words(b"the\n\nand\n") == frozenset({"the", "and"})


def test_parse_stop_words_empty_input():
    assert parse_stop_words(b"") == frozenset()


def test_get_stop_words_alpha_2_code_matches_language_name():
    assert get_stop_words("fr") == get_stop_words("french")


def test_get_stop_words_upper_case_code_is_normalized():
    words = get_stop_words("EN")
    assert words == get_stop_words("english")
    assert len(words) == 580
    assert "the" in words
    assert isinstance(words, frozenset)


def test_get_stop_words_dashed_code_is_not_normalized():
    # normalize_language lower-cases but does not strip a region tag, so
    # "en-US" becomes "en-us" and no such stop-words file exists.
    assert normalize_language("en-US") == "en-us"
    with pytest.raises(LookupError, match="en-us"):
        get_stop_words("en-US")


def test_normalize_language_upper_case_and_empty():
    assert normalize_language("EN") == "english"
    assert normalize_language("FR") == "french"
    assert normalize_language("") == ""


def test_normalize_language_unknown_is_passed_through_unchanged():
    assert normalize_language("klingon") == "klingon"


def test_expand_resource_path_points_into_package_data():
    path = expand_resource_path("stopwords/english.txt")
    assert path.endswith("sumy/data/stopwords/english.txt")


def test_cached_property_computes_only_once_and_returns_same_object():
    class Counter:
        def __init__(self):
            self.calls = 0

        @cached_property
        def value(self):
            self.calls += 1
            return [1]

    obj = Counter()
    first = obj.value
    second = obj.value
    assert obj.calls == 1
    assert first is second
    # The cached object is the live one: mutating it is visible next time.
    first.append(2)
    assert obj.value == [1, 2]


def test_cached_property_is_independent_per_instance():
    class Counter:
        def __init__(self, start):
            self.start = start
            self.calls = 0

        @cached_property
        def value(self):
            self.calls += 1
            return self.start

    a, b = Counter(1), Counter(2)
    assert (a.value, b.value) == (1, 2)
    assert (a.calls, b.calls) == (1, 1)


def test_document_parser_significant_and_stigma_defaults():
    assert DocumentParser.SIGNIFICANT_WORDS[0] == "významný"
    assert DocumentParser.STIGMA_WORDS == ("nejhorší", "zlý", "šeredný")
