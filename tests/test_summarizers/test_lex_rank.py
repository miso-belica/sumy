

import itertools
import math
import random
import time

import numpy
import pytest

import sumy.summarizers.lex_rank as lex_rank_module
from sumy.nlp.stemmers.czech import stem_word
from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.utils import get_stop_words

from ..utils import build_document, load_resource


def test_numpy_not_installed():
    summarizer = LexRankSummarizer()

    numpy = lex_rank_module.numpy
    lex_rank_module.numpy = None

    with pytest.raises(ValueError):
        summarizer(build_document(), 10)

    lex_rank_module.numpy = numpy


def test_tf_metrics():
    summarizer = LexRankSummarizer()

    sentences = [
        ("this", "sentence", "is", "simple", "sentence"),
        ("this", "is", "simple", "sentence", "yes", "is", "too", "too", "too"),
    ]
    metrics = summarizer._compute_tf(sentences)

    expected = [
        {"this": 1/2, "is": 1/2, "simple": 1/2, "sentence": 1.0},
        {"this": 1/3, "is": 2/3, "yes": 1/3, "simple": 1/3, "sentence": 1/3, "too": 1.0},
    ]
    assert expected == metrics


def test_idf_metrics():
    summarizer = LexRankSummarizer()

    sentences = [
        ("this", "sentence", "is", "simple", "sentence",),
        ("this", "is", "simple", "sentence", "yes", "is", "too", "too", "too",),
        ("not", "every", "sentence", "makes", "me", "happy",),
        ("yes",),
        (),
        ("every", "day", "is", "happy", "day",),
    ]
    metrics = summarizer._compute_idf(sentences)

    expected = {
        "this": math.log(6/2),
        "is": math.log(6/3),
        "yes": math.log(6/2),
        "simple": math.log(6/2),
        "sentence": math.log(6/3),
        "too": math.log(6/1),
        "not": math.log(6/1),
        "every": math.log(6/2),
        "makes": math.log(6/1),
        "me": math.log(6/1),
        "happy": math.log(6/2),
        "day": math.log(6/1),
    }
    assert expected == metrics


def test_words_shared_by_all_but_one_sentence_are_not_ignored():
    """
    "cats" and "dogs" occur in 2 of 3 sentences. With IDF log(N / n_w) from the paper they
    link the last sentence to both others, so it is the most central one.
    """
    document = build_document(("Cats sleep.", "Dogs bark.", "Cats like dogs."))

    sentences = LexRankSummarizer()(document, 1)

    assert [str(s) for s in sentences] == ["Cats like dogs."]


@pytest.mark.filterwarnings("error")
def test_single_sentence_document():
    """Every word of a single sentence is in all sentences, so all IDFs are 0."""
    document = build_document(("Cats sleep.",))

    sentences = LexRankSummarizer()(document, 1)

    assert [str(s) for s in sentences] == ["Cats sleep."]


def test_cosine_similarity_for_the_same_sentence_with_duplicate_words_should_be_one():
    """
    We compute similarity of the same sentences. These should be exactly the same and
    therefor have similarity close to 1.0.
    see https://github.com/miso-belica/sumy/issues/58
    """
    sentence1 = ["this", "sentence", "is", "simple", "sentence"]
    tf1 = {"this": 1/2, "sentence": 1.0, "is": 1/2, "simple": 1/2}
    sentence2 = ["this", "sentence", "is", "simple", "sentence"]
    tf2 = {"this": 1/2, "sentence": 1.0, "is": 1/2, "simple": 1/2}
    idf = {
        "this": 2/2,
        "sentence": 2/2,
        "is": 2/2,
        "simple": 2/2,
    }

    summarizer = LexRankSummarizer()
    cosine = summarizer.cosine_similarity(sentence1, sentence2, tf1, tf2, idf)

    assert abs(1.0 - cosine) < 0.00001


def test_cosine_similarity_sentences_with_no_common_word_should_be_zero():
    """
    We compute similarity of the sentences without single common word.
    These are considered dissimilar so have similarity close to 0.0.
    see https://github.com/miso-belica/sumy/issues/58
    """
    sentence1 = ["this", "sentence", "is", "simple", "sentence"]
    tf1 = {"this": 1/2, "sentence": 1.0, "is": 1/2, "simple": 1/2}
    sentence2 = ["that", "paragraph", "has", "some", "words"]
    tf2 = {"that": 1.0, "paragraph": 1.0, "has": 1.0, "some": 1.0, "words": 1.0}
    idf = {
        "this": 2/1,
        "sentence": 2/1,
        "is": 2/1,
        "simple": 2/1,
        "that": 2/1,
        "paragraph": 2/1,
        "has": 2/1,
        "some": 2/1,
        "words": 2/1,
    }

    summarizer = LexRankSummarizer()
    cosine = summarizer.cosine_similarity(sentence1, sentence2, tf1, tf2, idf)

    assert abs(0.0 - cosine) < 0.00001


def test_article_example():
    """Source: http://www.prevko.cz/dite/skutecne-pribehy-deti"""
    parser = PlaintextParser.from_string(
        load_resource("articles/prevko_cz_1.txt"),
        Tokenizer("czech")
    )
    summarizer = LexRankSummarizer(stem_word)
    summarizer.stop_words = get_stop_words("czech")

    sentences = summarizer(parser.document, 20)
    assert len(sentences) == 20


@pytest.mark.parametrize("sentences_count, expected_indexes", [
    (5, [2, 7, 17, 32, 43]),
    # the 16th best sentence ties with 14 others, so stop before it
    (15, [0, 2, 7, 17, 19, 22, 23, 26, 28, 29, 32, 34, 36, 40, 43]),
])
def test_article_example_picks_the_same_sentences(sentences_count, expected_indexes):
    parser = PlaintextParser.from_string(
        load_resource("articles/prevko_cz_1.txt"),
        Tokenizer("czech")
    )
    document = parser.document
    summarizer = LexRankSummarizer(stem_word)
    summarizer.stop_words = get_stop_words("czech")

    sentences = summarizer(document, sentences_count)

    assert [document.sentences.index(s) for s in sentences] == expected_indexes


def test_large_document_is_summarized_fast():
    """See https://github.com/miso-belica/sumy/issues/109"""
    rnd = random.Random(0)
    # the tokenizer drops words with digits, so spell the 2 000 words in letters only
    vocabulary = ["".join(letters) for letters in itertools.product("abcdefghij", repeat=4)][:2000]
    sentences = [" ".join(rnd.choice(vocabulary) for _ in range(15)) + "." for _ in range(2000)]
    document = build_document(sentences)
    for sentence in document.sentences:
        _ = sentence.words  # tokenize up front, so only LexRank is timed

    start = time.perf_counter()
    summary = LexRankSummarizer()(document, 10)
    elapsed = time.perf_counter() - start

    assert len(summary) == 10
    assert elapsed < 1.0


def test_document_is_all_in_upper_case():
    """
    When all words is in upper case Plaintext parser first line as heading and
    LexRank algorithm raises exception "ZeroDivisionError: float division by zero"
    because there is no sentence to summarize.
    See https://github.com/miso-belica/sumy/issues/25
    """
    parser = PlaintextParser.from_string(
        "JUST WRITING SOME TEXT. TO TEST CASE. WITH ZERO SENTENCES RETURNED. FROM TOKENIZER.",
        Tokenizer("english")
    )
    summarizer = LexRankSummarizer(stem_word)
    summarizer.stop_words = get_stop_words("english")

    sentences = summarizer(parser.document, 20)
    assert len(sentences) == 0


def test_power_method_should_return_different_scores_for_sentences():
    """See https://github.com/miso-belica/sumy/issues/26"""
    matrix = numpy.array([
        [0.1, 0.2, 0.3, 0.6, 0.9],
        [0.45, 0, 0.3, 0.6, 0],
        [0.5, 0.6, 0.3, 1, 0.9],
        [0.7, 0, 0, 0.6, 0],
        [0.5, 0.123, 0, 0.111, 0.9],
    ])
    scores = LexRankSummarizer.power_method(matrix, LexRankSummarizer.epsilon)

    assert len(frozenset(scores.tolist())) > 1

def test_power_method_should_return_finite():
    """See https://github.com/miso-belica/sumy/issues/187"""
    matrix = numpy.array([
        [0.1, 0.2, 0.3, 0.6, 0.9],
        [0.45, 0, 0.3, 0.6, 0],
        [0.5, 0.6, 0.3, 1, 0.9],
        [0.7, 0, 0, 0.6, 0],
        [0.5, 0.123, 0, 0.111, 0.9],
    ])
    scores = LexRankSummarizer.power_method(matrix, LexRankSummarizer.epsilon)

    assert all(numpy.isfinite(scores))