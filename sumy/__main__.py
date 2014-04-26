# -*- coding: utf8 -*-

"""
Sumy - automatic text summarizer.

Usage:
    sumy (luhn | edmundson | lsa | text-rank | lex-rank) [--length=<length>] [--language=<lang>] [--stopwords=<file_path>] [--format=<file_format>]
    sumy (luhn | edmundson | lsa | text-rank | lex-rank) [--length=<length>] [--language=<lang>] [--stopwords=<file_path>] [--format=<file_format>] --url=<url>
    sumy (luhn | edmundson | lsa | text-rank | lex-rank) [--length=<length>] [--language=<lang>] [--stopwords=<file_path>] [--format=<file_format>] --file=<file_path>
    sumy --version
    sumy --help

Options:
    --length=<length>       Length of summarized text. It may be count of sentences
                            or percentage of input text. [default: 20%]
    --language=<lang>       Natural language of summarized text. [default: english]
    --stopwords=<file_path> Path to a file containing a list of stopwords for the language used.
    --format=<file_format>  Format of input file.
    --url=<url>             URL address of the web page to summarize.
    --file=<file_path>      Path to the text file to summarize.
    --version               Displays current application version.
    --help                  Displays this text.

"""

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

import sys

from docopt import docopt
from . import __version__
from .utils import ItemsCount, get_stop_words, read_stop_words
from ._compat import urllib, to_string, to_unicode, to_bytes, PY3
from .nlp.tokenizers import Tokenizer
from .parsers.html import HtmlParser
from .parsers.plaintext import PlaintextParser
from .summarizers.luhn import LuhnSummarizer
from .summarizers.edmundson import EdmundsonSummarizer
from .summarizers.lsa import LsaSummarizer
from .summarizers.text_rank import TextRankSummarizer
from .summarizers.lex_rank import LexRankSummarizer
from .nlp.stemmers import Stemmer

HEADERS = {
    "User-Agent": "Sumy (Automatic text summarizer) Version/%s" % __version__,
}
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
}


def main(args=None):
    args = docopt(to_string(__doc__), args, version=__version__)
    summarizer, parser, items_count = handle_arguments(args)

    for sentence in summarizer(parser.document, items_count):
        if PY3:
            print(to_unicode(sentence))
        else:
            print(to_bytes(sentence))


def handle_arguments(args, default_input_stream=sys.stdin):
    language = args["--language"]
    file_format = args['--format']

    if args["--url"]:
        parser = PARSERS[file_format or "html"]
        request = urllib.Request(args["--url"], headers=HEADERS)
        input_stream = urllib.urlopen(request)
    elif args["--file"]:
        parser = PARSERS[file_format or "plaintext"]
        input_stream = open(args["--file"], "rb")
    else:
        parser = PARSERS[file_format or "plaintext"]
        input_stream = default_input_stream

    items_count = ItemsCount(args["--length"])

    parser = parser(input_stream.read(), Tokenizer(language))
    if input_stream is not sys.stdin:
        input_stream.close()

    if args['--stopwords']:
        stop_words = read_stop_words(args['--stopwords'])
    else:
        stop_words = get_stop_words(language)
    stemmer = Stemmer(language)

    summarize_method = next(method for method in AVAILABLE_METHODS.keys() if args[method])
    summarizer = build_summarizer(summarize_method, stop_words, stemmer, parser)

    return summarizer, parser, items_count


def build_summarizer(summarize_method, stop_words, stemmer, parser):
    summarizer_class = AVAILABLE_METHODS[summarize_method]
    summarizer = summarizer_class(stemmer)
    if summarize_method == 'edmundson':
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
