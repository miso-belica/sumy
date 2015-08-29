# -*- coding: utf8 -*-

"""
Sumy - automatic text summarizer.

Usage:
    sumy (luhn | edmundson | lsa | text-rank | lex-rank | sum-basic | kl) [--length=<length>] [--language=<lang>] [--stopwords=<file_path>] [--format=<format>]
    sumy (luhn | edmundson | lsa | text-rank | lex-rank | sum-basic | kl) [--length=<length>] [--language=<lang>] [--stopwords=<file_path>] [--format=<format>] --url=<url>
    sumy (luhn | edmundson | lsa | text-rank | lex-rank | sum-basic | kl) [--length=<length>] [--language=<lang>] [--stopwords=<file_path>] [--format=<format>] --file=<file_path>
    sumy --version
    sumy --help

Options:
    --length=<length>        Length of summarized text. It may be count of sentences
                             or percentage of input text. [default: 20%]
    --language=<lang>        Natural language of summarized text. [default: english]
    --stopwords=<file_path>  Path to a file containing a list of stopwords. One word per line in UTF-8 encoding.
                             If it's not provided default list of stop-words is used according to chosen language.
    --format=<format>        Format of input document. Possible values: html, plaintext
    --url=<url>              URL address of the web page to summarize.
    --file=<file_path>       Path to the text file to summarize.
    --version                Displays current application version.
    --help                   Displays this text.

"""

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

import sys

from docopt import docopt
from . import __version__
from .utils import ItemsCount, get_stop_words, read_stop_words, fetch_url
from ._compat import to_string, to_unicode, to_bytes, PY3
from .nlp.tokenizers import Tokenizer
from .parsers.html import HtmlParser
from .parsers.plaintext import PlaintextParser
from .summarizers.luhn import LuhnSummarizer
from .summarizers.edmundson import EdmundsonSummarizer
from .summarizers.lsa import LsaSummarizer
from .summarizers.text_rank import TextRankSummarizer
from .summarizers.lex_rank import LexRankSummarizer
from .summarizers.sum_basic import SumBasicSummarizer
from .summarizers.kl import KLSummarizer
from .nlp.stemmers import Stemmer

PARSERS = {
    "html": HtmlParser,
    "plaintext": PlaintextParser,
}

AVAILABLE_METHODS = {
    "luhn": LuhnSummarizer,
    "edmundson": EdmundsonSummarizer,
    "lsa": LsaSummarizer,
    "text-rank": TextRankSummarizer,
    "lex-rank": LexRankSummarizer,
    "sum-basic": SumBasicSummarizer,
    "kl": KLSummarizer,
}


def main(args=None):
    args = docopt(to_string(__doc__), args, version=__version__)
    summarizer, parser, items_count = handle_arguments(args)

    for sentence in summarizer(parser.document, items_count):
        if PY3:
            print(to_unicode(sentence))
        else:
            print(to_bytes(sentence))

    return 0


def handle_arguments(args, default_input_stream=sys.stdin):
    document_format = args['--format']
    if document_format is not None and document_format not in PARSERS:
        raise ValueError("Unsupported format of input document. Possible values are: %s. Given: %s." % (
            ", ".join(PARSERS.keys()),
            document_format,
        ))

    if args["--url"] is not None:
        parser = PARSERS[document_format or "html"]
        document_content = fetch_url(args["--url"])
    elif args["--file"] is not None:
        parser = PARSERS[document_format or "plaintext"]
        with open(args["--file"], "rb") as file:
            document_content = file.read()
    else:
        parser = PARSERS[document_format or "plaintext"]
        document_content = default_input_stream.read()

    items_count = ItemsCount(args["--length"])

    language = args["--language"]
    if args['--stopwords']:
        stop_words = read_stop_words(args['--stopwords'])
    else:
        stop_words = get_stop_words(language)

    parser = parser(document_content, Tokenizer(language))
    stemmer = Stemmer(language)

    summarizer_class = next(cls for name, cls in AVAILABLE_METHODS.items() if args[name])
    summarizer = build_summarizer(summarizer_class, stop_words, stemmer, parser)

    return summarizer, parser, items_count


def build_summarizer(summarizer_class, stop_words, stemmer, parser):
    summarizer = summarizer_class(stemmer)
    if summarizer_class is EdmundsonSummarizer:
        summarizer.null_words = stop_words
        summarizer.bonus_words = parser.significant_words
        summarizer.stigma_words = parser.stigma_words
    else:
        summarizer.stop_words = stop_words
    return summarizer


if __name__ == "__main__":
    try:
        exit_code = main()
        exit(exit_code)
    except KeyboardInterrupt:
        exit(1)
    except Exception as e:
        print(e)
        exit(1)
