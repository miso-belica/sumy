

from pytest import approx

from sumy.evaluation import rouge_l_sentence_level, rouge_l_summary_level, rouge_n
from sumy.evaluation.rouge import _get_ngrams, _get_word_ngrams, _len_lcs, _recon_lcs, _split_into_words, _union_lcs
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
