# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

import pytest
from pytest import approx

from sumy.evaluation import cosine_similarity, unit_overlap
from sumy.evaluation import precision, recall, f_score
from sumy.evaluation import rouge_n, rouge_l_sentence_level, rouge_l_summary_level
from sumy.evaluation.rouge import _get_ngrams, _split_into_words, _get_word_ngrams, _len_lcs, _recon_lcs, _union_lcs
from sumy.models import TfDocumentModel
from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.plaintext import PlaintextParser


# class TestCoselectionEvaluation(unittest.TestCase):
def test_precision_empty_evaluated():
    with pytest.raises(ValueError):
        precision((), ("s1", "s2", "s3", "s4", "s5"))


def test_precision_empty_reference():
    with pytest.raises(ValueError):
        precision(("s1", "s2", "s3", "s4", "s5"), ())


def test_precision_no_match():
    result = precision(("s1", "s2", "s3", "s4", "s5"), ("s6", "s7", "s8"))

    assert result == 0.0


def test_precision_reference_smaller():
    result = precision(("s1", "s2", "s3", "s4", "s5"), ("s1",))

    assert result == approx(0.2)


def test_precision_evaluated_smaller():
    result = precision(("s1",), ("s1", "s2", "s3", "s4", "s5"))

    assert result == approx(1.0)


def test_precision_equals():
    sentences = ("s1", "s2", "s3", "s4", "s5")
    result = precision(sentences, sentences)

    assert result == approx(1.0)


def test_recall_empty_evaluated():
    with pytest.raises(ValueError):
         recall((), ("s1", "s2", "s3", "s4", "s5"))


def test_recall_empty_reference():
    with pytest.raises(ValueError):
         recall(("s1", "s2", "s3", "s4", "s5"), ())


def test_recall_no_match():
    result = recall(("s1", "s2", "s3", "s4", "s5"), ("s6", "s7", "s8"))

    assert result == 0.0


def test_recall_reference_smaller():
    result = recall(("s1", "s2", "s3", "s4", "s5"), ("s1",))

    assert result == approx(1.0)


def test_recall_evaluated_smaller():
    result = recall(("s1",), ("s1", "s2", "s3", "s4", "s5"))

    assert result == approx(0.20)


def test_recall_equals():
    sentences = ("s1", "s2", "s3", "s4", "s5")
    result = recall(sentences, sentences)

    assert result == approx(1.0)


def test_basic_f_score_empty_evaluated():
    with pytest.raises(ValueError):
        f_score((), ("s1", "s2", "s3", "s4", "s5"))


def test_basic_f_score_empty_reference():
    with pytest.raises(ValueError):
        f_score(("s1", "s2", "s3", "s4", "s5"), ())


def test_basic_f_score_no_match():
    result = f_score(("s1", "s2", "s3", "s4", "s5"), ("s6", "s7", "s8"))

    assert result == 0.0


def test_basic_f_score_reference_smaller():
    result = f_score(("s1", "s2", "s3", "s4", "s5"), ("s1",))

    assert result == approx(1/3)


def test_basic_f_score_evaluated_smaller():
    result = f_score(("s1",), ("s1", "s2", "s3", "s4", "s5"))

    assert result == approx(1/3)


def test_basic_f_score_equals():
    sentences = ("s1", "s2", "s3", "s4", "s5")
    result = f_score(sentences, sentences)

    assert result == approx(1.0)


def test_f_score_1():
    sentences = (("s1",), ("s1", "s2", "s3", "s4", "s5"))
    result = f_score(*sentences, weight=2.0)

    p = 1/1
    r = 1/5
    # ( (W^2 + 1) * P * R ) / ( W^2 * P + R )
    expected = (5 * p * r) / (4 * p + r)

    assert result == approx(expected)


def test_f_score_2():
    sentences = (("s1", "s3", "s6"), ("s1", "s2", "s3", "s4", "s5"))
    result = f_score(*sentences, weight=0.5)

    p = 2/3
    r = 2/5
    # ( (W^2 + 1) * P * R ) / ( W^2 * P + R )
    expected = (1.25 * p * r) / (0.25 * p + r)

    assert result == approx(expected)


# class TestContentBasedEvaluation(unittest.TestCase):
def test_wrong_arguments():
    text = "Toto je moja veta, to sa nedá poprieť."
    model = TfDocumentModel(text, Tokenizer("czech"))

    with pytest.raises(ValueError):
        cosine_similarity(text, text)
    with pytest.raises(ValueError):
        cosine_similarity(text, model)
    with pytest.raises(ValueError):
        cosine_similarity(model, text)


def test_empty_model():
    text = "Toto je moja veta, to sa nedá poprieť."
    model = TfDocumentModel(text, Tokenizer("czech"))
    empty_model = TfDocumentModel([])

    with pytest.raises(ValueError):
        cosine_similarity(empty_model, empty_model)
    with pytest.raises(ValueError):
        cosine_similarity(empty_model, model)
    with pytest.raises(ValueError):
        cosine_similarity(model, empty_model)


def test_cosine_exact_match():
    text = "Toto je moja veta, to sa nedá poprieť."
    model = TfDocumentModel(text, Tokenizer("czech"))

    assert cosine_similarity(model, model) == approx(1.0)


def test_cosine_no_match():
    tokenizer = Tokenizer("czech")
    model1 = TfDocumentModel("Toto je moja veta. To sa nedá poprieť!", tokenizer)
    model2 = TfDocumentModel("Hento bolo jeho slovo, ale možno klame.", tokenizer)

    assert cosine_similarity(model1, model2) == approx(0.0)


def test_cosine_half_match():
    tokenizer = Tokenizer("czech")
    model1 = TfDocumentModel("Veta aká sa tu len veľmi ťažko hľadá", tokenizer)
    model2 = TfDocumentModel("Teta ktorá sa tu iba veľmi zle hľadá", tokenizer)

    assert cosine_similarity(model1, model2) == approx(0.5)


def test_unit_overlap_empty():
    tokenizer = Tokenizer("english")
    model = TfDocumentModel("", tokenizer)

    with pytest.raises(ValueError):
        unit_overlap(model, model)


def test_unit_overlap_wrong_arguments():
    tokenizer = Tokenizer("english")
    model = TfDocumentModel("", tokenizer)

    with pytest.raises(ValueError):
        unit_overlap("model", "model")
    with pytest.raises(ValueError):
        unit_overlap("model", model)
    with pytest.raises(ValueError):
        unit_overlap(model, "model")


def test_unit_overlap_exact_match():
    tokenizer = Tokenizer("czech")
    model = TfDocumentModel("Veta aká sa len veľmi ťažko hľadá.", tokenizer)

    assert unit_overlap(model, model) == approx(1.0)


def test_unit_overlap_no_match():
    tokenizer = Tokenizer("czech")
    model1 = TfDocumentModel("Toto je moja veta. To sa nedá poprieť!", tokenizer)
    model2 = TfDocumentModel("Hento bolo jeho slovo, ale možno klame.", tokenizer)

    assert unit_overlap(model1, model2) == approx(0.0)


def test_unit_overlap_half_match():
    tokenizer = Tokenizer("czech")
    model1 = TfDocumentModel("Veta aká sa tu len veľmi ťažko hľadá", tokenizer)
    model2 = TfDocumentModel("Teta ktorá sa tu iba veľmi zle hľadá", tokenizer)

    assert unit_overlap(model1, model2) == approx(1/3)


# class TestRougeEvaluation(unittest.TestCase):
def test_get_ngrams():
    assert not _get_ngrams(3, "")

    correct_ngrams = [("t", "e"), ("e", "s"), ("s", "t"),
                      ("t", "i"), ("i", "n"), ("n", "g")]
    found_ngrams = _get_ngrams(2, "testing")

    assert len(correct_ngrams) == len(found_ngrams)
    for ngram in correct_ngrams:
        assert ngram in found_ngrams


def test_split_into_words():
    sentences1 = PlaintextParser.from_string("One, two two. Two. Three.", Tokenizer("english")).document.sentences
    assert ["One", "two", "two", "Two", "Three"] == _split_into_words(sentences1)
    sentences2 = PlaintextParser.from_string("two two. Two. Three.", Tokenizer("english")).document.sentences
    assert ["two", "two", "Two", "Three"] == _split_into_words(sentences2)


def test_get_word_ngrams():
    sentences = PlaintextParser.from_string("This is a test.", Tokenizer("english")).document.sentences
    expected_ngrams = {("This", "is"), ("is", "a"), ("a", "test")}
    found_ngrams = _get_word_ngrams(2, sentences)

    assert expected_ngrams == found_ngrams


def test_ngrams_for_more_sentences_should_not_return_words_at_boundaries():
    sentences = PlaintextParser.from_string("This is a pencil.\nThis is a eraser.\nThis is a book.", Tokenizer("english")).document.sentences
    expected_ngrams = {("This", "is"), ("is", "a"), ("a", "pencil"), ("a", "eraser"), ("a", "book")}
    found_ngrams = _get_word_ngrams(2, sentences)

    assert expected_ngrams == found_ngrams


def test_len_lcs():
    assert _len_lcs("1234", "1224533324") == 4
    assert _len_lcs("thisisatest", "testing123testing") == 7


def test_recon_lcs():
    assert _recon_lcs("1234", "1224533324") == ("1", "2", "3", "4")
    assert _recon_lcs("thisisatest", "testing123testing") == ("t", "s", "i", "t", "e", "s", "t")


def test_rouge_n():
    candidate_text = "pulses may ease schizophrenic voices"
    candidate = PlaintextParser(candidate_text, Tokenizer("english")).document.sentences

    reference1_text = "magnetic pulse series sent through brain may ease schizophrenic voices"
    reference1 = PlaintextParser(reference1_text, Tokenizer("english")).document.sentences

    reference2_text = "yale finds magnetic stimulation some relief to schizophrenics imaginary voices"

    reference2 = PlaintextParser.from_string(reference2_text, Tokenizer("english")).document.sentences

    assert rouge_n(candidate, reference1, 1) == approx(4/10)
    assert rouge_n(candidate, reference2, 1) == approx(1/10)

    assert rouge_n(candidate, reference1, 2) == approx(3/9)
    assert rouge_n(candidate, reference2, 2) == approx(0/9)

    assert rouge_n(candidate, reference1, 3) == approx(2/8)
    assert rouge_n(candidate, reference2, 3) == approx(0/8)

    assert rouge_n(candidate, reference1, 4) == approx(1/7)
    assert rouge_n(candidate, reference2, 4) == approx(0/7)

    # These tests will apply when multiple reference summaries can be input
    # assert rouge_n(candidate, [reference1, reference2], 1) == approx(5/20)
    # assert rouge_n(candidate, [reference1, reference2], 2) == approx(3/18)
    # assert rouge_n(candidate, [reference1, reference2], 3) == approx(2/16)
    # assert rouge_n(candidate, [reference1, reference2], 4) == approx(1/14)


def test_rouge_l_sentence_level():
    reference_text = "police killed the gunman"
    reference = PlaintextParser(reference_text, Tokenizer("english")).document.sentences

    candidate1_text = "police kill the gunman"
    candidate1 = PlaintextParser(candidate1_text, Tokenizer("english")).document.sentences

    candidate2_text = "the gunman kill police"
    candidate2 = PlaintextParser(candidate2_text, Tokenizer("english")).document.sentences

    candidate3_text = "the gunman police killed"
    candidate3 = PlaintextParser(candidate3_text, Tokenizer("english")).document.sentences

    assert rouge_l_sentence_level(candidate1, reference) == approx(3/4)
    assert rouge_l_sentence_level(candidate2, reference) == approx(2/4)
    assert rouge_l_sentence_level(candidate3, reference) == approx(2/4)


def test_union_lcs():
    reference_text = "one two three four five"
    reference = PlaintextParser(reference_text, Tokenizer("english")).document.sentences

    candidate_text = "one two six seven eight. one three eight nine five."
    candidates = PlaintextParser(candidate_text, Tokenizer("english")).document.sentences

    assert _union_lcs(candidates, reference[0]) == approx(4/5)


def test_rouge_l_summary_level():
    reference_text = "one two three four five. one two three four five."
    reference = PlaintextParser(reference_text, Tokenizer("english")).document.sentences

    candidate_text = "one two six seven eight. one three eight nine five."
    candidates = PlaintextParser(candidate_text, Tokenizer("english")).document.sentences
    rouge_l_summary_level(candidates, reference)
