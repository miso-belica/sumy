"""Gap coverage for plaintext/HTML parsing, DOM models, TF model,
tokenizers and stemmers.

Upstream covers the standard plaintext shapes (including the Chinese
line that must not become a heading), the two HTML cases, the DOM
basics, the TF basics and one stemmer per language family. These tests
pin the edges that are still untested: empty/heading-only documents,
CRLF, mixed-case and digits-only lines, the punctuation-only line, the
HTML significant/stigma tag sets, the pre-skip, the TF case quirk, the
tokenizer word filter and abbreviation handling, and the null/special
stemmers.
"""

import pytest

from sumy.models import TfDocumentModel
from sumy.models.dom import ObjectDocumentModel, Paragraph, Sentence
from sumy.nlp.stemmers import Stemmer, null_stemmer
from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.html import HtmlParser
from sumy.parsers.parser import DocumentParser
from sumy.parsers.plaintext import PlaintextParser

EN = Tokenizer("english")


def parse(text, tokenizer=EN):
    return PlaintextParser.from_string(text, tokenizer)


def texts(document):
    return [str(s) for s in document.sentences]


# ---------------------------------------------------------------- plaintext


def test_plaintext_empty_string_is_one_empty_paragraph():
    document = parse("").document
    assert len(document.paragraphs) == 1
    assert document.sentences == ()
    assert document.headings == ()


def test_plaintext_whitespace_only_is_one_empty_paragraph():
    document = parse("   \n  \n ").document
    assert len(document.paragraphs) == 1
    assert document.sentences == ()


def test_plaintext_heading_only_document_has_no_sentences():
    document = parse("MY HEADING").document
    assert len(document.paragraphs) == 1
    assert texts(document) == []
    assert [str(s) for s in document.headings] == ["MY HEADING"]
    # The heading words become the significant words.
    assert parse("MY HEADING").significant_words == ("MY", "HEADING")


def test_plaintext_heading_followed_only_by_blank_lines():
    document = parse("MY HEADING\n\n").document
    assert len(document.paragraphs) == 1
    assert [str(s) for s in document.headings] == ["MY HEADING"]


def test_plaintext_trailing_blank_lines_do_not_add_paragraphs():
    document = parse("One sentence here.\n\n\n\n").document
    assert len(document.paragraphs) == 1
    assert texts(document) == ["One sentence here."]


def test_plaintext_crlf_splits_paragraphs():
    document = parse(
        "First sentence here.\r\nSecond sentence here.\r\n\r\nThird sentence here."
    ).document
    assert len(document.paragraphs) == 2
    assert texts(document) == [
        "First sentence here.",
        "Second sentence here.",
        "Third sentence here.",
    ]


def test_plaintext_mixed_case_line_is_not_a_heading():
    # Lines are joined before sentence splitting, so the mixed-case line
    # merges with the following body line into a single sentence.
    document = parse("My Heading\nBody sentence here.").document
    assert document.headings == ()
    assert texts(document) == ["My Heading Body sentence here."]


def test_plaintext_digits_only_line_is_not_a_heading():
    # str.isupper() is False for a digits-only line.
    document = parse("12345\nBody sentence here.").document
    assert document.headings == ()
    assert texts(document) == ["12345 Body sentence here."]


def test_plaintext_heading_in_the_middle_of_a_paragraph():
    document = parse(
        "First sentence here.\nIMPORTANT NOTE\nSecond sentence here."
    ).document
    assert len(document.paragraphs) == 1
    assert texts(document) == ["First sentence here.", "Second sentence here."]
    assert [str(s) for s in document.headings] == ["IMPORTANT NOTE"]
    assert parse(
        "First sentence here.\nIMPORTANT NOTE\nSecond sentence here."
    ).significant_words == ("IMPORTANT", "NOTE")


def test_plaintext_sentence_without_terminal_punctuation_is_kept():
    assert texts(parse("Just some words without period").document) == [
        "Just some words without period"
    ]


def test_plaintext_punctuation_only_line_is_not_dropped():
    # NLTK splits the run of exclamation marks into punctuation
    # sentences instead of discarding the line.
    assert texts(parse("!!!\nBody sentence here.").document) == [
        "!",
        "!!",
        "Body sentence here.",
    ]


def test_plaintext_significant_and_stigma_words_fall_back_to_defaults():
    parser = parse("plain body text here.")
    assert parser.significant_words == DocumentParser.SIGNIFICANT_WORDS
    assert parser.stigma_words == DocumentParser.STIGMA_WORDS


def test_plaintext_from_file(tmp_path):
    path = tmp_path / "doc.txt"
    path.write_text("First sentence here.\n\nSecond sentence here.", encoding="utf-8")
    document = PlaintextParser.from_file(str(path), EN).document
    assert len(document.paragraphs) == 2
    assert texts(document) == ["First sentence here.", "Second sentence here."]


def test_parser_tokenize_sentences_drops_blank_input():
    assert parse("x.").tokenize_sentences("   ") == []


def test_parser_tokenize_words_filters_punctuation_and_numbers():
    assert parse("x.").tokenize_words("Hello, world!") == ("Hello", "world")


# ---------------------------------------------------------------------- HTML


def html_parser(html):
    return HtmlParser.from_string(html, "http://example.com", EN)


def test_html_heading_tags_become_headings_and_significant_words():
    parser = html_parser(
        "<html><body><h2>Section Two Title</h2>"
        "<p>Sentence under section two. Another sentence.</p>"
        "<h3>Subsection Title</h3><p>Sentence under subsection.</p></body></html>"
    )
    document = parser.document
    assert [str(s) for s in document.headings] == [
        "Section Two Title",
        "Subsection Title",
    ]
    assert texts(document) == [
        "Sentence under section two.",
        "Another sentence.",
        "Sentence under subsection.",
    ]
    assert parser.significant_words == (
        "Section",
        "Two",
        "Title",
        "Subsection",
        "Title",
    )


def test_html_strong_and_em_words_are_significant():
    parser = html_parser(
        "<html><body><p><strong>Strong words here.</strong> "
        "<em>Emphasised words here.</em> Plain sentence here.</p></body></html>"
    )
    assert parser.significant_words == (
        "Strong",
        "words",
        "here",
        "Emphasised",
        "words",
        "here",
    )
    assert "Plain sentence here." in texts(parser.document)


def test_html_strike_words_are_stigma_words():
    parser = html_parser(
        "<html><body><p><strike>Struck words here.</strike> "
        "Plain sentence here.</p></body></html>"
    )
    assert parser.stigma_words == ("Struck", "words", "here")
    assert texts(parser.document) == ["Struck words here.", "Plain sentence here."]


def test_html_pre_content_is_skipped():
    parser = html_parser(
        "<html><body><p>Before code sentence here.</p>"
        "<pre>int x = 1;</pre><p>After code sentence here.</p></body></html>"
    )
    assert texts(parser.document) == [
        "Before code sentence here.",
        "After code sentence here.",
    ]


def test_html_multi_paragraph_document_keeps_paragraph_order():
    parser = html_parser(
        "<html><body><p>First paragraph sentence here. Second sentence here.</p>"
        "<p>Another paragraph sentence here. Yet another sentence.</p></body></html>"
    )
    assert texts(parser.document) == [
        "First paragraph sentence here.",
        "Second sentence here.",
        "Another paragraph sentence here.",
        "Yet another sentence.",
    ]


def test_html_empty_body_is_an_empty_document():
    parser = html_parser("<html><body></body></html>")
    assert parser.document.sentences == ()
    assert parser.significant_words == DocumentParser.SIGNIFICANT_WORDS
    assert parser.stigma_words == DocumentParser.STIGMA_WORDS


def test_html_entities_are_decoded():
    parser = html_parser(
        "<html><body><p>Fish &amp; chips are tasty. Cats &amp; dogs.</p></body></html>"
    )
    assert texts(parser.document) == ["Fish & chips are tasty.", "Cats & dogs."]


# ------------------------------------------------------------------ DOM / TF


def test_empty_document_model_repr():
    assert repr(ObjectDocumentModel([])) == "<DOM with 0 paragraphs>"
    assert repr(Paragraph([])) == "<Paragraph with 0 headings & 0 sentences>"


def test_sentence_text_is_stripped_and_words_of_empty_sentence():
    assert str(Sentence("  padded text  ", EN)) == "padded text"
    assert Sentence("", EN).words == ()


def test_sentence_heading_repr_and_heading_flag_breaks_equality():
    assert repr(Sentence("TITLE", EN, is_heading=True)) == "<Heading: TITLE>"
    assert Sentence("a", EN) != Sentence("a", EN, is_heading=True)
    assert hash(Sentence("a", EN)) == hash(Sentence("a", EN))


def test_sentence_equality_with_non_sentence_asserts():
    with pytest.raises(AssertionError):
        Sentence("a", EN) == "a"


def test_tf_model_empty_magnitude_is_zero():
    assert TfDocumentModel(()).magnitude == 0.0


def test_tf_model_term_frequency_lookup_is_case_sensitive():
    # Terms are lower-cased at construction, but term_frequency() does
    # not lower-case its argument, so the upper-case lookup misses.
    model = TfDocumentModel(("wA", "wB"))
    assert model.term_frequency("wa") == 1
    assert model.term_frequency("WA") == 0


def test_tf_model_normalized_frequency_of_missing_term_with_smoothing():
    model = TfDocumentModel(("a", "b", "b"))
    assert model.normalized_term_frequency("z", 0.4) == pytest.approx(0.4)


def test_tf_model_most_frequent_terms_tie_keeps_insertion_order():
    assert TfDocumentModel(("b", "a", "b", "a")).most_frequent_terms() == ("b", "a")


def test_tf_model_string_without_tokenizer_and_bad_type_raise():
    with pytest.raises(ValueError):
        TfDocumentModel("text without tokenizer")
    with pytest.raises(ValueError):
        TfDocumentModel(123)


# ------------------------------------------------------------- tokenizer


def test_tokenizer_words_filter_digits_underscores_and_punctuation():
    assert EN.to_words("abc 123 45x x_1") == ("abc",)
    assert EN.to_words("_hello hello_") == ()
    assert EN.to_words("") == ()
    assert EN.to_words("!!! ??? ...") == ()


def test_tokenizer_words_splits_contractions_and_keeps_hyphens():
    # NLTK word_tokenize splits "don't"; the hyphenated word survives
    # the word-pattern filter as one token.
    assert EN.to_words("don't well-known a-b") == ("do", "n't", "well-known", "a-b")


@pytest.mark.parametrize(
    "text, expected",
    [
        ("This is e.g. an example. Next sentence here.",
         ("This is e.g. an example.", "Next sentence here.")),
        ("It is i.e. obvious. Next one.", ("It is i.e. obvious.", "Next one.")),
        ("Smith et al. wrote this. Next sentence.",
         ("Smith et al. wrote this.", "Next sentence.")),
    ],
)
def test_tokenizer_sentences_keep_extra_abbreviations(text, expected):
    assert EN.to_sentences(text) == expected


def test_tokenizer_sentences_empty_and_blank_input():
    assert EN.to_sentences("") == ()
    assert EN.to_sentences("   ") == ()
    assert EN.to_sentences("Just words here") == ("Just words here",)


def test_tokenizer_slovak_alias_keeps_slovak_language_name():
    tokenizer = Tokenizer("sk")
    assert tokenizer.language == "slovak"
    assert tokenizer.to_sentences("Ako sa mas? Ja dobre.") == (
        "Ako sa mas?",
        "Ja dobre.",
    )


def test_tokenizer_unknown_language_raises_lookup_error():
    with pytest.raises(LookupError):
        Tokenizer("klingon")


# ---------------------------------------------------------------- stemmers


def test_null_stemmer_lower_cases_and_handles_empty():
    assert null_stemmer("") == ""
    assert null_stemmer("ľŠčŤžÝáÍé") == "ľščťžýáíé"


def test_stemmer_alpha_2_code_is_normalized():
    assert Stemmer("en")("running") == "run"
    assert Stemmer("english")("Beautiful") == "beauti"


def test_stemmer_special_languages_fall_back_to_null_stemmer():
    assert Stemmer("hebrew")("Shalom") == "shalom"
    assert Stemmer("chinese")("Hello") == "hello"


def test_stemmer_ukrainian_and_slovak_alias():
    assert Stemmer("ukrainian")("роботи") == "робот"
    assert Stemmer("slovak")("pěkný") == Stemmer("czech")("pěkný") == "pěkn"
