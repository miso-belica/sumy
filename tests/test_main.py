# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

import unittest

from docopt import docopt, DocoptExit
from sumy.__main__ import __doc__ as main_doc
from sumy.__main__ import handle_arguments, to_string, __version__
from .utils import StringIO


class TestMain(unittest.TestCase):
    DEFAULT_ARGS = {
        '--file': None,
        '--format': None,
        '--help': False,
        '--language': 'english',
        '--length': '20%',
        '--stopwords': None,
        '--url': None,
        '--version': False,
        'edmundson': False,
        'lex-rank': False,
        'lsa': True,
        'luhn': False,
        'text-rank': False,
        'sum-basic': False,
        'kl': False,
    }

    def test_ok_args(self):
        docopt(to_string(main_doc), 'luhn --url=URL --format=FORMAT'.split(), version=__version__)

    def test_args_none(self):
        self.assertRaises(DocoptExit, docopt, to_string(main_doc), None, version=__version__)

    def test_args_just_command(self):
        args = docopt(to_string(main_doc), ['lsa'], version=__version__)
        self.assertEqual(self.DEFAULT_ARGS, args)

    def test_args_two_commands(self):
        self.assertRaises(DocoptExit, docopt, to_string(main_doc), 'lsa luhn'.split(), version=__version__)

    def test_args_url_and_file(self):
        self.assertRaises(DocoptExit, docopt, to_string(main_doc), 'lsa --url=URL --file=FILE'.split(), version=__version__)

    def test_handle_default_arguments(self):
        handle_arguments(self.DEFAULT_ARGS, default_input_stream=StringIO("Whatever."))

    def test_handle_wrong_format(self):
        wrong_args = self.DEFAULT_ARGS.copy()
        wrong_args.update({'--url': 'URL', '--format': 'text'})
        self.assertRaises(ValueError, handle_arguments, wrong_args, default_input_stream=StringIO("Whatever."))
