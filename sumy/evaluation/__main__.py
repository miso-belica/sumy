# -*- coding: utf8 -*-

"""
Sumy - evaluation of automatic text summary.

Usage:
    sumy_eval (random | luhn | edmundson | lsa | text-rank | lex-rank | sum-basic | kl) <reference_summary> [--length=<length>] [--language=<lang>]
    sumy_eval (random | luhn | edmundson | lsa | text-rank | lex-rank | sum-basic | kl) <reference_summary> [--length=<length>] [--language=<lang>] --url=<url>
    sumy_eval (random | luhn | edmundson | lsa | text-rank | lex-rank | sum-basic | kl) <reference_summary> [--length=<length>] [--language=<lang>] --file=<file_path> --format=<file_format>
    sumy_eval --version
    sumy_eval --help

Options:
    <reference_summary>  Path to the file with reference summary.
    --url=<url>          URL address of summarizied message.
    --file=<file>        Path to file with summarizied text.
    --format=<format>    Format of input file. [default: plaintext]
    --length=<length>    Length of summarizied text. It may be count of sentences
                         or percentage of input text. [default: 20%]
    --language=<lang>    Natural language of summarizied text. [default: english]
    --version            Displays version of application.
    --help               Displays this text.

"""

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

import sys

from itertools import chain
from docopt import docopt
from .. import __version__
from ..utils import ItemsCount, get_stop_words, fetch_url
from ..models import TfDocumentModel
from .._compat import to_string
from ..nlp.tokenizers import Tokenizer
from ..parsers.html import HtmlParser
from ..parsers.plaintext import PlaintextParser
from ..summarizers.random import RandomSummarizer
from ..summarizers.luhn import LuhnSummarizer
from ..summarizers.edmundson import EdmundsonSummarizer
from ..summarizers.lsa import LsaSummarizer
from ..summarizers.text_rank import TextRankSummarizer
from ..summarizers.lex_rank import LexRankSummarizer
from ..summarizers.sum_basic import SumBasicSummarizer
from ..summarizers.kl import KLSummarizer
from ..nlp.stemmers import Stemmer
from . import precision, recall, f_score, cosine_similarity, unit_overlap
from . import rouge_1, rouge_2, rouge_l_sentence_level, rouge_l_summary_level 


PARSERS = {
    "html": HtmlParser,
    "plaintext": PlaintextParser,
}


def build_random(parser, language):
    return RandomSummarizer()


def build_luhn(parser, language):
    summarizer = LuhnSummarizer(Stemmer(language))
    summarizer.stop_words = get_stop_words(language)

    return summarizer


def build_edmundson(parser, language):
    summarizer = EdmundsonSummarizer(Stemmer(language))
    summarizer.null_words = get_stop_words(language)
    summarizer.bonus_words = parser.significant_words
    summarizer.stigma_words = parser.stigma_words

    return summarizer


def build_lsa(parser, language):
    summarizer = LsaSummarizer(Stemmer(language))
    summarizer.stop_words = get_stop_words(language)

    return summarizer


def build_text_rank(parser, language):
    summarizer = TextRankSummarizer(Stemmer(language))
    summarizer.stop_words = get_stop_words(language)

    return summarizer


def build_lex_rank(parser, language):
    summarizer = LexRankSummarizer(Stemmer(language))
    summarizer.stop_words = get_stop_words(language)

    return summarizer


def build_sum_basic(parser, language):
    summarizer = SumBasicSummarizer(Stemmer(language))
    summarizer.stop_words = get_stop_words(language)

    return summarizer


def build_kl(parser, language):
    summarizer = KLSummarizer(Stemmer(language))
    summarizer.stop_words = get_stop_words(language)

    return summarizer


def evaluate_cosine_similarity(evaluated_sentences, reference_sentences):
    evaluated_words = tuple(chain(*(s.words for s in evaluated_sentences)))
    reference_words = tuple(chain(*(s.words for s in reference_sentences)))
    evaluated_model = TfDocumentModel(evaluated_words)
    reference_model = TfDocumentModel(reference_words)

    return cosine_similarity(evaluated_model, reference_model)


def evaluate_unit_overlap(evaluated_sentences, reference_sentences):
    evaluated_words = tuple(chain(*(s.words for s in evaluated_sentences)))
    reference_words = tuple(chain(*(s.words for s in reference_sentences)))
    evaluated_model = TfDocumentModel(evaluated_words)
    reference_model = TfDocumentModel(reference_words)

    return unit_overlap(evaluated_model, reference_model)


AVAILABLE_METHODS = {
    "random": build_random,
    "luhn": build_luhn,
    "edmundson": build_edmundson,
    "lsa": build_lsa,
    "text-rank": build_text_rank,
    "lex-rank": build_lex_rank,
    "sum-basic": build_sum_basic,
    "kl": build_kl,
}

AVAILABLE_EVALUATIONS = (
    ("Precision", False, precision),
    ("Recall", False, recall),
    ("F-score", False, f_score),
    ("Cosine similarity", False, evaluate_cosine_similarity),
    ("Cosine similarity (document)", True, evaluate_cosine_similarity),
    ("Unit overlap", False, evaluate_unit_overlap),
    ("Unit overlap (document)", True, evaluate_unit_overlap),
    ("Rouge-1", False, rouge_1),
    ("Rouge-2", False, rouge_2),
    ("Rouge-L (Sentence Level)", False, rouge_l_sentence_level),
    ("Rouge-L (Summary Level)", False, rouge_l_summary_level)
)


def main(args=None):
    args = docopt(to_string(__doc__), args, version=__version__)
    summarizer, document, items_count, reference_summary = handle_arguments(args)

    evaluated_sentences = summarizer(document, items_count)
    reference_document = PlaintextParser.from_string(reference_summary,
        Tokenizer(args["--language"]))
    reference_sentences = reference_document.document.sentences

    for name, evaluate_document, evaluate in AVAILABLE_EVALUATIONS:
        if evaluate_document:
            result = evaluate(evaluated_sentences, document.sentences)
        else:
            result = evaluate(evaluated_sentences, reference_sentences)
        print("%s: %f" % (name, result))

    return 0


def handle_arguments(args):
    document_format = args["--format"]
    if document_format is not None and document_format not in PARSERS:
        raise ValueError("Unsupported format of input document. Possible values are: %s. Given: %s." % (
            ", ".join(PARSERS.keys()),
            document_format,
        ))

    if args["--url"] is not None:
        parser = PARSERS["html"]
        document_content = fetch_url(args["--url"])
    elif args["--file"] is not None:
        parser = PARSERS.get(document_format, PlaintextParser)
        with open(args["--file"], "rb") as file:
            document_content = file.read()
    else:
        parser = PARSERS["plaintext"]
        document_content = sys.stdin.read()

    summarizer_builder = AVAILABLE_METHODS["luhn"]
    for method, builder in AVAILABLE_METHODS.items():
        if args[method]:
            summarizer_builder = builder
            break

    items_count = ItemsCount(args["--length"])

    parser = parser(document_content, Tokenizer(args["--language"]))

    with open(args["<reference_summary>"], "rb") as file:
        reference_summmary = file.read().decode("utf8")

    return summarizer_builder(parser, args["--language"]), parser.document, items_count, reference_summmary


if __name__ == "__main__":
    try:
        exit_code = main()
        exit(exit_code)
    except KeyboardInterrupt:
        exit(1)
    except Exception as e:
        print(e)
        exit(1)
