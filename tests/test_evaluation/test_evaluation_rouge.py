# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from pytest import approx

from sumy.evaluation import rouge_n, rouge_l_sentence_level, rouge_l_summary_level
from sumy.evaluation.rouge import _get_ngrams, _split_into_words, _get_word_ngrams, _len_lcs, _recon_lcs, _union_lcs
from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.plaintext import PlaintextParser


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
