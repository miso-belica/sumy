"""Gap coverage for the evaluation metrics.

Upstream covers ROUGE-N partial scores, the reference-too-short and
candidate-without-ngram cases, ROUGE-L sentence/summary partial scores,
and the coselection precision/recall/f-score tables in depth. These
tests pin the remaining edges: ROUGE-1 identical/disjoint scores,
a ROUGE-2 partial score, ROUGE-N with an empty evaluated collection,
ROUGE-L empty-collection and empty-word rejections, and the set
semantics of the coselection metrics — a sentence repeated in a
collection counts only once.
"""

import pytest

from sumy.evaluation import f_score, precision, recall
from sumy.evaluation.rouge import (
    rouge_1,
    rouge_2,
    rouge_l_sentence_level,
    rouge_l_summary_level,
    rouge_n,
)
from sumy.models.dom import Sentence
from sumy.nlp.tokenizers import Tokenizer

EN = Tokenizer("english")


def sentences(*texts):
    return [Sentence(text, EN) for text in texts]


def test_rouge_1_identical_and_disjoint():
    same = sentences("the cat sat", "the dog ran")
    assert rouge_1(same, same) == 1.0
    assert rouge_1(same, sentences("fish swim fast", "birds fly high")) == 0.0


def test_rouge_2_partial_overlap():
    # Reference bigrams: (the, cat), (cat, sat), (sat, there); two overlap.
    assert rouge_2(
        sentences("the cat sat here"), sentences("the cat sat there")
    ) == pytest.approx(2 / 3)


def test_rouge_n_candidate_shorter_than_n_scores_zero():
    assert rouge_n(sentences("hi"), sentences("one two three four"), 3) == 0.0


def test_rouge_n_empty_evaluated_collection_raises():
    with pytest.raises(ValueError, match="at least 1 sentence"):
        rouge_n([], sentences("the cat sat"))


def test_rouge_l_sentence_level_identical_is_one():
    same = sentences("the cat sat", "the dog ran")
    assert rouge_l_sentence_level(same, same) == 1.0


@pytest.mark.parametrize(
    "func",
    [rouge_l_sentence_level, rouge_l_summary_level],
)
def test_rouge_l_empty_collection_raises(func):
    with pytest.raises(ValueError, match="at least 1 sentence"):
        func([], sentences("the cat"))


@pytest.mark.parametrize(
    "func",
    [rouge_l_sentence_level, rouge_l_summary_level],
)
def test_rouge_l_wordless_collection_raises(func):
    with pytest.raises(ValueError, match="at least 1 word"):
        func(sentences(""), sentences("the cat"))


def test_coselection_duplicate_sentences_count_once():
    # precision/recall/f_score all go through frozensets, so repeating
    # a sentence in a collection does not change any of the scores.
    evaluated = sentences("x one", "x one")
    reference = sentences("x one")
    assert precision(evaluated, reference) == 1.0
    assert recall(evaluated, reference) == 1.0
    assert f_score(evaluated, reference) == 1.0


def test_coselection_duplicate_in_reference_does_not_change_recall():
    evaluated = sentences("x one")
    reference = sentences("x one", "x one", "y two")
    assert recall(evaluated, reference) == 0.5
    assert precision(evaluated, reference) == 1.0
