# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import pytest
from docopt import docopt, DocoptExit

from sumy.__main__ import __doc__ as main_doc, handle_arguments, to_string, __version__
from .utils import StringIO


DEFAULT_ARGS = {
    '--file': None,
    '--format': None,
    '--help': False,
    '--language': 'english',
    '--length': '20%',
    '--stopwords': None,
    '--url': None,
    '--text': None,
    '--version': False,
    'edmundson': False,
    'lex-rank': False,
    'lsa': True,
    'luhn': False,
    'text-rank': False,
    'sum-basic': False,
    'kl': False,
}


def test_ok_args():
    docopt(to_string(main_doc), 'luhn --url=URL --format=FORMAT'.split(), version=__version__)


def test_args_none():
    with pytest.raises(DocoptExit):
        docopt(to_string(main_doc), None, version=__version__)


def test_args_just_command():
    args = docopt(to_string(main_doc), ['lsa'], version=__version__)

    assert DEFAULT_ARGS == args


def test_args_two_commands():
    with pytest.raises(DocoptExit):
        docopt(to_string(main_doc), 'lsa luhn'.split(), version=__version__)


def test_args_url_and_file():
    with pytest.raises(DocoptExit):
        docopt(to_string(main_doc), 'lsa --url=URL --file=FILE'.split(), version=__version__)


def test_args_url_and_text():
    with pytest.raises(DocoptExit):
        docopt(to_string(main_doc), 'lsa --url=URL --text=TEXT'.split(), version=__version__)


def test_handle_default_arguments():
    handle_arguments(DEFAULT_ARGS, default_input_stream=StringIO("Whatever."))


def test_handle_wrong_format():
    wrong_args = DEFAULT_ARGS.copy()
    wrong_args.update({'--url': 'URL', '--format': 'text'})

    with pytest.raises(ValueError):
        handle_arguments(wrong_args, default_input_stream=StringIO("Whatever."))
