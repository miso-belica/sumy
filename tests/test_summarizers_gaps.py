"""Gap coverage for the summarizers.

Upstream covers empty/single documents for most summarizers, the main
rating examples, and Edmundson's four methods in depth. These tests pin
what is still untested: the count forms every summarizer shares
(0 / over-100 / percentage / the at-least-one 0% rule / negative
slicing), heading-only documents, the stop-words switch changing the
outcome, the single-significant-word Luhn rating, the Reduction edge
guards, the SumBasic all-stop-words document, the KL tf helper, the
Edmundson weight validation and single-method selections, the LSA
warning and all-stop-words document, the TextRank single-word edge and
power method, and the LexRank empty/identical documents.
"""

import warnings

import pytest
from pytest import approx

from sumy.models.dom import Sentence
from sumy.nlp.stemmers import null_stemmer
from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers._summarizer import AbstractSummarizer
from sumy.summarizers.edmundson import EdmundsonSummarizer
from sumy.summarizers.kl import KLSummarizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.summarizers.luhn import LuhnSummarizer
from sumy.summarizers.reduction import ReductionSummarizer
from sumy.summarizers.random import RandomSummarizer
from sumy.summarizers.sum_basic import SumBasicSummarizer
from sumy.summarizers.text_rank import TextRankSummarizer

EN = Tokenizer("english")
RICH_TEXT = (
    "Cats are small animals. Dogs are loyal animals. "
    "Cats and dogs are common pets. Birds can fly high. Fish swim in water."
)


def doc(text):
    return PlaintextParser.from_string(text, EN).document


def texts(sentences):
    return [str(s) for s in sentences]


RICH = doc(RICH_TEXT)
RICH_TEXTS = texts(RICH.sentences)

NON_EDMUNDSON = [
    LuhnSummarizer,
    ReductionSummarizer,
    RandomSummarizer,
    SumBasicSummarizer,
    KLSummarizer,
    LsaSummarizer,
    TextRankSummarizer,
    LexRankSummarizer,
]


# ------------------------------------------------------------ base contract


def test_abstract_summarizer_rejects_non_callable_stemmer():
    with pytest.raises(TypeError):
        AbstractSummarizer(stemmer=123)


def test_abstract_summarizer_normalize_and_stem_word():
    summarizer = AbstractSummarizer()
    assert summarizer.normalize_word("HeLLo") == "hello"
    assert summarizer.stem_word("HeLLo") == "hello"  # null_stemmer


@pytest.mark.parametrize("cls", NON_EDMUNDSON)
def test_all_summarizers_count_zero_returns_empty(cls):
    assert cls()(RICH, 0) == ()


@pytest.mark.parametrize("cls", NON_EDMUNDSON)
def test_all_summarizers_count_over_total_returns_everything(cls):
    result = cls()(RICH, 99)
    assert len(result) == 5
    assert set(texts(result)) == set(RICH_TEXTS)


@pytest.mark.parametrize("cls", NON_EDMUNDSON)
def test_all_summarizers_percentage_count(cls):
    assert len(cls()(RICH, "50%")) == 2


@pytest.mark.parametrize("cls", NON_EDMUNDSON)
def test_all_summarizers_zero_percent_still_returns_one(cls):
    # ItemsCount clamps a percentage to at least one sentence.
    assert len(cls()(RICH, "0%")) == 1


@pytest.mark.parametrize("cls", NON_EDMUNDSON)
def test_all_summarizers_negative_count_drops_one(cls):
    result = cls()(RICH, -1)
    assert len(result) == 4
    assert set(texts(result)) < set(RICH_TEXTS)


@pytest.mark.parametrize("cls", NON_EDMUNDSON)
def test_all_summarizers_heading_only_document_returns_empty(cls):
    assert cls()(doc("MY HEADING"), 2) == ()


def test_luhn_negative_count_drops_the_lowest_rated_sentence():
    # Probed: the Fish sentence (the lowest-rated one) is the one dropped.
    assert texts(LuhnSummarizer()(RICH, -1)) == RICH_TEXTS[:4]


def test_reduction_negative_count_drops_the_lowest_rated_sentence():
    assert texts(ReductionSummarizer()(RICH, -1)) == RICH_TEXTS[:4]


def test_random_summarizer_result_is_a_document_ordered_subset():
    result = RandomSummarizer()(RICH, 3)
    assert len(result) == 3
    assert set(texts(result)) < set(RICH_TEXTS)
    # _get_best_sentences re-sorts by document order whatever the ratings.
    assert texts(result) == sorted(
        texts(result), key=RICH_TEXTS.index
    )


# --------------------------------------------------------------------- Luhn


def test_luhn_rate_sentence_single_significant_word_twice():
    summarizer = LuhnSummarizer()
    # One chunk of two significant words: 2**2 / 2 = 2.0.
    assert summarizer.rate_sentence(Sentence("cats cats", EN), ("cats",)) == 2.0
    assert summarizer.rate_sentence(Sentence("hello world", EN), ("cats",)) == 0
    assert summarizer.rate_sentence(Sentence("", EN), ("cats",)) == 0


def test_luhn_rate_sentence_single_significant_word_scores_zero():
    # A chunk with a single significant word scores 0 by definition.
    assert LuhnSummarizer().rate_sentence(
        Sentence("cats and dogs", EN), ("cats",)
    ) == 0


def test_luhn_stop_words_setter_lower_cases():
    summarizer = LuhnSummarizer()
    summarizer.stop_words = ["THE", "And"]
    assert summarizer.stop_words == frozenset({"the", "and"})


def test_luhn_stop_words_change_the_winner():
    document = doc(
        "Cats cats cats are here. Dogs dogs dogs are here. Birds fly high."
    )
    plain = LuhnSummarizer()(document, 1)
    stopped = LuhnSummarizer()
    stopped.stop_words = ["cats"]
    assert texts(plain) == ["Cats cats cats are here."]
    assert texts(stopped(document, 1)) == ["Dogs dogs dogs are here."]


# ----------------------------------------------------------------- Reduction


def test_reduction_single_word_edge_returns_zero():
    summarizer = ReductionSummarizer()
    # log(1) + log(1) == 0, so the guard returns 0.0 instead of dividing.
    assert summarizer._rate_sentences_edge(["a"], ["a"]) == 0.0
    assert summarizer._rate_sentences_edge(["a", "b"], ["c", "d"]) == 0.0


def test_reduction_single_sentence_has_no_ratings():
    assert ReductionSummarizer().rate_sentences(doc("Only one sentence here.")) == {}


def test_reduction_stop_words_change_the_winner():
    document = doc(
        "Cats sleep all day. Dogs sleep all day. Cats dogs play together."
    )
    # Without stop words the first two sentences tie and the first wins;
    # removing "cats" breaks the tie in favour of the Dogs sentence.
    assert texts(ReductionSummarizer()(document, 1)) == ["Cats sleep all day."]
    stopped = ReductionSummarizer()
    stopped.stop_words = ["cats"]
    assert texts(stopped(document, 1)) == ["Dogs sleep all day."]


# ------------------------------------------------------------------ SumBasic


def test_sumbasic_all_stop_words_document_still_returns_sentences():
    summarizer = SumBasicSummarizer()
    summarizer.stop_words = ["the", "and"]
    document = doc("The the the. And and and. The and the.")
    # Every content-word list is empty, every rating is 0, and the
    # first sentences win the ties in document order.
    assert texts(summarizer(document, 2)) == ["The the the.", "And and and."]


def test_sumbasic_stop_words_setter_lower_cases():
    summarizer = SumBasicSummarizer()
    summarizer.stop_words = ["THE"]
    assert summarizer.stop_words == frozenset({"the"})


# ------------------------------------------------------------------------- KL


def test_kl_compute_tf_empty_and_single_sentence():
    summarizer = KLSummarizer()
    assert summarizer.compute_tf([]) == {}
    assert summarizer.compute_tf([Sentence("a b a", EN)]) == approx(
        {"a": 2 / 3, "b": 1 / 3}
    )


def test_kl_stop_words_filter_the_document_words():
    summarizer = KLSummarizer()
    summarizer.stop_words = ["the"]
    assert summarizer._get_all_content_words_in_doc(
        [Sentence("the cat the dog", EN)]
    ) == ["cat", "dog"]


# ------------------------------------------------------------------ Edmundson


def edmundson(**weights):
    summarizer = EdmundsonSummarizer(**weights)
    summarizer.bonus_words = ["cats", "dogs"]
    summarizer.stigma_words = ["birds"]
    summarizer.null_words = ["the"]
    return summarizer


def test_edmundson_default_without_bonus_words_raises():
    with pytest.raises(ValueError, match="bonus words"):
        EdmundsonSummarizer()(RICH, 2)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"cue_weight": -1},
        {"key_weight": -0.5},
        {"title_weight": -1},
        {"location_weight": -1},
    ],
)
def test_edmundson_negative_weight_raises(kwargs):
    with pytest.raises(ValueError, match="Negative weights"):
        EdmundsonSummarizer(**kwargs)


def test_edmundson_weights_are_stored_as_floats():
    summarizer = EdmundsonSummarizer(cue_weight=2, key_weight=0)
    assert summarizer._cue_weight == 2.0
    assert summarizer._key_weight == 0.0


def test_edmundson_all_zero_weights_returns_first_sentences_in_order():
    summarizer = edmundson(
        cue_weight=0, key_weight=0, title_weight=0, location_weight=0
    )
    assert texts(summarizer(RICH, 2)) == RICH_TEXTS[:2]


def test_edmundson_cue_only_and_key_only_selections():
    cue = edmundson(cue_weight=1, key_weight=0, title_weight=0, location_weight=0)
    assert texts(cue(RICH, 2)) == [
        "Cats are small animals.",
        "Cats and dogs are common pets.",
    ]
    key = edmundson(cue_weight=0, key_weight=1, title_weight=0, location_weight=0)
    assert texts(key(RICH, 2)) == [
        "Cats are small animals.",
        "Cats and dogs are common pets.",
    ]


def test_edmundson_title_null_words_change_the_winner():
    titled = PlaintextParser.from_string(
        "CATS AND DOGS\nCats are small animals. Dogs are loyal animals. "
        "Birds can fly high.",
        EN,
    ).document
    summarizer = EdmundsonSummarizer(
        cue_weight=0, key_weight=0, title_weight=1, location_weight=0
    )
    summarizer.bonus_words = ["cats"]
    summarizer.null_words = ["the"]
    assert texts(summarizer(titled, 1)) == ["Cats are small animals."]
    summarizer.null_words = ["cats"]
    assert texts(summarizer(titled, 1)) == ["Dogs are loyal animals."]


def test_edmundson_location_only_selection():
    summarizer = edmundson(
        cue_weight=0, key_weight=0, title_weight=0, location_weight=1
    )
    assert texts(summarizer(RICH, 2)) == [
        "Cats are small animals.",
        "Fish swim in water.",
    ]


def test_edmundson_heading_only_document_with_all_word_sets_returns_empty():
    assert edmundson()(doc("MY HEADING"), 2) == ()


# ----------------------------------------------------------------------- LSA


def test_lsa_warns_when_words_are_fewer_than_sentences():
    with pytest.warns(UserWarning, match=r"Number of words \(1\)"):
        result = LsaSummarizer()(doc("Cats. Cats. Cats. Cats."), 2)
    assert len(result) == 2


def test_lsa_all_stop_words_document_returns_empty():
    summarizer = LsaSummarizer()
    summarizer.stop_words = ["cats", "dogs", "birds", "fish"]
    assert summarizer(doc("Cats dogs. Birds fish."), 2) == ()


def test_lsa_identical_sentences_return_the_first_one():
    document = doc(
        "Cats are small animals. Cats are small animals. Cats are small animals."
    )
    assert texts(LsaSummarizer()(document, 1)) == ["Cats are small animals."]


# ------------------------------------------------------------------ TextRank


def test_textrank_single_word_edge_cases():
    assert TextRankSummarizer._rate_sentences_edge(["a"], ["a"]) == 1.0
    assert TextRankSummarizer._rate_sentences_edge(["a"], ["b"]) == 0.0
    assert TextRankSummarizer._rate_sentences_edge(["a", "b"], ["c", "d"]) == 0.0


def test_textrank_power_method_on_identity_matrix_stays_uniform():
    import numpy

    assert list(TextRankSummarizer.power_method(numpy.eye(2), 1e-4)) == approx(
        [0.5, 0.5]
    )


def test_textrank_single_sentence_rating_is_near_one():
    ratings = TextRankSummarizer().rate_sentences(doc("Only one sentence here."))
    assert len(ratings) == 1
    assert list(ratings.values())[0] == approx(1.0, abs=1e-6)


# ------------------------------------------------------------------- LexRank


def test_lexrank_empty_document_returns_empty():
    assert LexRankSummarizer()(doc(""), 2) == ()


def test_lexrank_identical_sentences_return_the_first_ones():
    document = doc(
        "Cats are small animals. Cats are small animals. Cats are small animals."
    )
    result = LexRankSummarizer()(document, 2)
    assert len(result) == 2
    assert texts(result) == ["Cats are small animals.", "Cats are small animals."]
