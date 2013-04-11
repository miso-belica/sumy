# -*- coding: utf8 -*-

"""
Sumy - automatic text summarizer.

Usage:
    sumy (luhn | edmundson | lsa) [--length=<length>]
    sumy (luhn | edmundson | lsa) [--length=<length>] --url=<url>
    sumy (luhn | edmundson | lsa) [--length=<length>] --file=<file_path> --format=<file_format>
    sumy --version
    sumy --help

Options:
    --url=<url>        URL address of summarizied message.
    --file=<file>      Path to file with summarizied text.
    --format=<format>  Format of input file. [default: plaintext]
    --length=<length>  Length of summarizied text. It may be count of sentences
                       or percentage of input text. [default: 20%]
    --version          Displays version of application.
    --help             Displays this text.

"""

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

import sys

from docopt import docopt
from . import __version__
from .utils import ItemsCount, get_stop_words
from ._compat import urllib, to_string, to_unicode, to_bytes, PY3
from .nlp.tokenizers import Tokenizer
from .parsers.html import HtmlParser
from .parsers.plaintext import PlaintextParser
from .summarizers.luhn import LuhnSummarizer
from .summarizers.edmundson import EdmundsonSummarizer
from .summarizers.lsa import LsaSummarizer
from .nlp.stemmers.cs import stem_word

HEADERS = {
    "User-Agent": "Sumy (Automatic text summarizer) Version/%s" % __version__,
}
PARSERS = {
    "html": HtmlParser,
    "plaintext": PlaintextParser,
}


def build_luhn(parser):
    summarizer = LuhnSummarizer(parser.document, stem_word)
    summarizer.stop_words = get_stop_words("cs")

    return summarizer


def build_edmundson(parser):
    summarizer = EdmundsonSummarizer(parser.document, stem_word)
    summarizer.null_words = get_stop_words("cs")
    summarizer.bonus_words = parser.significant_words
    summarizer.stigma_words = parser.stigma_words

    return summarizer


def build_lsa(parser):
    summarizer = LsaSummarizer(parser.document, stem_word)
    summarizer.stop_words = get_stop_words("cs")

    return summarizer


AVAILABLE_METHODS = {
    "luhn": build_luhn,
    "edmundson": build_edmundson,
    "lsa": build_lsa,
}


def main(args=None):
    args = docopt(to_string(__doc__), args, version=__version__)
    method, items_count = handle_arguments(args)

    for sentence in method(items_count):
        if PY3:
            print(to_unicode(sentence))
        else:
            print(to_bytes(sentence))


def handle_arguments(args):
    parser = PARSERS["plaintext"]
    input_stream = sys.stdin

    if args["--url"] is not None:
        parser = PARSERS["html"]
        request = urllib.Request(args["--url"], headers=HEADERS)
        input_stream = urllib.urlopen(request)
    elif args["--file"] is not None:
        parser = PARSERS.get(args["--format"], PlaintextParser)
        input_stream = open(args["--file"], "rb")

    summarizer = AVAILABLE_METHODS["luhn"]
    for method, builder in AVAILABLE_METHODS.items():
        if args[method]:
            summarizer = builder
            break

    items_count = ItemsCount(args["--length"])

    parser = parser(input_stream.read(), Tokenizer("czech"))
    if input_stream is not sys.stdin:
        input_stream.close()

    return summarizer(parser), items_count


if __name__ == "__main__":
    try:
        exit_code = main()
        exit(exit_code)
    except KeyboardInterrupt:
        exit(1)
    except Exception as e:
        print(e)
        exit(1)
