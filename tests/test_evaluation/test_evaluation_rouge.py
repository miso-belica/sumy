

import pytest
from pytest import approx

from sumy.evaluation import rouge_l_sentence_level, rouge_l_summary_level, rouge_n
from sumy.evaluation.rouge import _get_ngrams, _get_word_ngrams, _len_lcs, _recon_lcs, _split_into_words, _union_lcs
from sumy.models.dom import Sentence
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


def test_rouge_n_rejects_reference_too_short_for_the_ngram_size():
    """
    ROUGE-N divides by the number of reference n-grams, which can be 0.

    A reference of fewer than n words yields no n-gram at all, so the recall
    denominator is 0 and `rouge_n` used to raise `ZeroDivisionError`. This needs
    no word-less sentence: a one word reference is enough to break `rouge_2`.
    Nothing can be measured against a reference holding no n-gram of that size,
    so the input is refused rather than scored.
    """
    reference = PlaintextParser("hello", Tokenizer("english")).document.sentences
    candidate = PlaintextParser("hello there", Tokenizer("english")).document.sentences

    assert rouge_n(candidate, reference, 1) == approx(1)
    with pytest.raises(ValueError):
        rouge_n(candidate, reference, 2)


def test_rouge_n_scores_candidate_without_any_ngram_as_zero():
    """
    Only the *reference* count is a denominator, so an empty candidate is fine.

    Recall is well defined when the reference has n-grams and the candidate has
    none: nothing of the reference was covered, which is 0 rather than an error.
    """
    reference = PlaintextParser("police killed the gunman", Tokenizer("english")).document.sentences
    candidate = [Sentence("", Tokenizer("english"))]

    assert rouge_n(candidate, reference, 1) == approx(0)


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


def test_rouge_l_sentence_level_without_any_common_word():
    """
    A summary sharing no word with the reference used to crash with
    `ZeroDivisionError: float division by zero`.

    `_f_lcs` derived `beta` as `p_lcs / r_lcs`, and an empty LCS makes `r_lcs`
    zero. Note this is a *second*, independent division by zero from the one in
    `_union_lcs`: it is reached through `rouge_l_sentence_level`, which never
    calls `_union_lcs` at all. The `denom == 0` guard proposed in
    https://github.com/miso-belica/sumy/issues/128 would not have helped,
    because `beta` is evaluated before `denom` and raises first.

    With no overlap there is neither precision nor recall, so F is 0.
    """
    reference = PlaintextParser("the museum opened last spring", Tokenizer("english")).document.sentences
    candidate = PlaintextParser("penguins waddle across frozen beaches", Tokenizer("english")).document.sentences

    assert rouge_l_sentence_level(candidate, reference) == approx(0)


def test_union_lcs():
    """
    `_union_lcs` returns how many reference words the union of the LCSes covers.

    This used to assert 4/5, because the implementation divided the union size
    by `combined_lcs_length` (2 + 3 for the two candidate sentences below).
    That the old assertion held was a coincidence of this fixture: the sum of
    the per-sentence LCS lengths happened to equal the reference length, so a
    wrong denominator produced the right-looking number. The count of covered
    reference words is 4 -- "one two three five" out of "one two three four five".
    """
    reference_text = "one two three four five"
    reference = PlaintextParser(reference_text, Tokenizer("english")).document.sentences

    candidate_text = "one two six seven eight. one three eight nine five."
    candidates = PlaintextParser(candidate_text, Tokenizer("english")).document.sentences

    assert _union_lcs(candidates, reference[0]) == 4


def test_union_lcs_is_not_deflated_by_repeating_the_same_candidate_sentence():
    """
    Adding a candidate sentence that covers nothing new must not change the score.

    Dividing by `combined_lcs_length` made the result depend on how the same
    coverage was spread over candidate sentences: repeating a sentence doubled
    the denominator while leaving the union untouched, halving the score. Here
    the covered reference words are "one two" either way.
    """
    reference = PlaintextParser("one two three four five", Tokenizer("english")).document.sentences

    single = PlaintextParser("one two.", Tokenizer("english")).document.sentences
    repeated = PlaintextParser("one two. one two.", Tokenizer("english")).document.sentences

    assert _union_lcs(single, reference[0]) == 2
    assert _union_lcs(repeated, reference[0]) == _union_lcs(single, reference[0])


def test_rouge_l_summary_level():
    reference_text = "one two three four five. one two three four five."
    reference = PlaintextParser(reference_text, Tokenizer("english")).document.sentences

    candidate_text = "one two six seven eight. one three eight nine five."
    candidates = PlaintextParser(candidate_text, Tokenizer("english")).document.sentences
    rouge_l_summary_level(candidates, reference)


def test_rouge_l_summary_level_scores_identical_summary_as_one():
    """
    A summary identical to the reference must score 1, even with repeated words.

    The union of longest common subsequences was collected as a set of *words*,
    so a reference word occurring twice ("the" below) could only ever be counted
    once. That caps even a perfect summary below 1 -- here at 9 covered words out
    of 11. Collecting positions in the reference sentence instead keeps the two
    occurrences distinct.
    """
    text = "the cat sat on the mat. the dog ate the bone."
    reference = PlaintextParser(text, Tokenizer("english")).document.sentences
    candidates = PlaintextParser(text, Tokenizer("english")).document.sentences

    assert rouge_l_summary_level(candidates, reference) == approx(1)


def test_rouge_l_summary_level_does_not_count_a_candidate_word_more_than_once():
    """
    A word may be credited only as many times as the summary actually contains it.

    `LCS_u` is counted in positions of the *reference* sentence, so one candidate
    sentence matched against several reference sentences could be credited once
    per reference sentence. Here the single "the cat sat" would cover 6 reference
    words out of 6 while having only 3 of its own, making P_lcs 2.0 and F 1.11 --
    an F-measure above 1.

    ROUGE-1.5.5 clips each hit against the remaining unigram counts, which Lin
    added in v1.4.1: "if a unigram count already involve in one LCS match then it
    will not be counted if it match another token in the model unit. This will
    make sure LCS score is always lower than unigram score." The candidate here
    supplies "the", "cat" and "sat" once each, so there are 3 hits out of m = 6
    and n = 3, giving F = 3*(6^2 + 3^2) / (6^3 + 3^3) = 5/9.
    """
    reference = PlaintextParser("the cat sat. the cat sat.", Tokenizer("english")).document.sentences
    candidates = PlaintextParser("the cat sat.", Tokenizer("english")).document.sentences

    score = rouge_l_summary_level(candidates, reference)

    assert score <= 1
    assert score == approx(5/9)


def test_rouge_l_summary_level_for_reference_sentence_without_any_common_word():
    """
    A reference sentence sharing no word with the summary used to crash with
    `ZeroDivisionError: division by zero`.

    `_union_lcs` normalized the union LCS by `combined_lcs_length` (the sum of
    the per-sentence LCS lengths), which is 0 exactly when nothing overlaps.
    Such a reference sentence is an ordinary input, not a degenerate one, so
    the metric has to score it 0 instead of raising.

    Reported in https://github.com/miso-belica/sumy/issues/128, where it was
    hit both directly and through `sumy_eval`.
    """
    reference = PlaintextParser("one two three four five.", Tokenizer("english")).document.sentences
    candidates = PlaintextParser("alpha beta gamma delta.", Tokenizer("english")).document.sentences

    assert rouge_l_summary_level(candidates, reference) == approx(0)


@pytest.mark.parametrize("rouge_l", [rouge_l_sentence_level, rouge_l_summary_level])
@pytest.mark.parametrize("candidate_text, reference_text", [
    ("", ""),
    ("", "police killed the gunman"),
    ("police killed the gunman", ""),
])
def test_rouge_l_rejects_sentences_without_any_word(rouge_l, candidate_text, reference_text):
    """
    A summary made only of word-less sentences cannot be scored, so it is rejected.

    `Sentence("", tokenizer)` has no words but is a perfectly valid sentence, and
    a collection holding one satisfies the "at least 1 sentence" check while
    containing nothing to measure. Both `m` and `n` are then 0 and `F_lcs` used
    to raise `ZeroDivisionError`.

    Returning 0 would be wrong: 0 means "not a single word in common", which is
    the score for two completely disjoint summaries. Two word-less summaries are
    not disjoint, they are identical. Since `R_lcs = llcs/m` and `P_lcs = llcs/n`
    are both undefined here, there is no score to report and the input itself is
    the problem, so it is refused the same way an empty collection is.
    """
    reference = [Sentence(reference_text, Tokenizer("english"))]
    candidate = [Sentence(candidate_text, Tokenizer("english"))]

    with pytest.raises(ValueError):
        rouge_l(candidate, reference)


@pytest.mark.parametrize("rouge_l", [rouge_l_sentence_level, rouge_l_summary_level])
def test_rouge_l_rejects_word_less_sentences_from_the_parser(rouge_l):
    """
    The parser produces word-less sentences too, so this needs no hand-built `Sentence`.

    A document of nothing but punctuation is split into sentences that all
    tokenize to no words, which reaches the same undefined score through the
    ordinary public API.
    """
    reference = PlaintextParser("... !!! ???", Tokenizer("english")).document.sentences
    candidate = PlaintextParser("--- ;;; ...", Tokenizer("english")).document.sentences
    assert len(reference) > 0 and len(candidate) > 0, "the parser should return sentences"

    with pytest.raises(ValueError):
        rouge_l(candidate, reference)
