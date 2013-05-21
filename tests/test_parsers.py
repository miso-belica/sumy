# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

import unittest

from sumy._compat import to_unicode
from sumy.parsers.plaintext import PlaintextParser
from sumy.parsers.html import HtmlParser
from sumy.nlp.tokenizers import Tokenizer
from .utils import expand_resource_path


class TestParser(unittest.TestCase):
    def test_parse_plaintext(self):
        parser = PlaintextParser.from_string("""
            Ako sa máš? Ja dobre! A ty? No
            mohlo to byť aj lepšie!!! Ale pohodička.


            TOTO JE AKOŽE NADPIS
            A toto je text pod ním, ktorý je textový.
            A tak ďalej...
        """, Tokenizer("czech"))

        document = parser.document

        self.assertEqual(len(document.paragraphs), 2)

        self.assertEqual(len(document.paragraphs[0].headings), 0)
        self.assertEqual(len(document.paragraphs[0].sentences), 5)

        self.assertEqual(len(document.paragraphs[1].headings), 1)
        self.assertEqual(len(document.paragraphs[1].sentences), 2)

    def test_parse_plaintext_long(self):
        parser = PlaintextParser.from_string("""
            Ako sa máš? Ja dobre! A ty? No
            mohlo to byť aj lepšie!!! Ale pohodička.

            TOTO JE AKOŽE NADPIS
            A toto je text pod ním, ktorý je textový.
            A tak ďalej...

            VEĽKOLEPÉ PREKVAPENIE
            Tretí odstavec v tomto texte je úplne o ničom. Ale má
            vety a to je hlavné. Takže sa majte na pozore ;-)

            A tak ďalej...


            A tak este dalej!
        """, Tokenizer("czech"))

        document = parser.document

        self.assertEqual(len(document.paragraphs), 5)

        self.assertEqual(len(document.paragraphs[0].headings), 0)
        self.assertEqual(len(document.paragraphs[0].sentences), 5)

        self.assertEqual(len(document.paragraphs[1].headings), 1)
        self.assertEqual(len(document.paragraphs[1].sentences), 2)

        self.assertEqual(len(document.paragraphs[2].headings), 1)
        self.assertEqual(len(document.paragraphs[2].sentences), 3)

        self.assertEqual(len(document.paragraphs[3].headings), 0)
        self.assertEqual(len(document.paragraphs[3].sentences), 1)

        self.assertEqual(len(document.paragraphs[4].headings), 0)
        self.assertEqual(len(document.paragraphs[4].sentences), 1)


class TestHtmlParser(unittest.TestCase):
    def test_annotated_text(self):
        path = expand_resource_path("snippets/paragraphs.html")
        url = "http://www.snippet.org/paragraphs.html"
        parser = HtmlParser.from_file(path, url, Tokenizer("czech"))

        document = parser.document

        self.assertEqual(len(document.paragraphs), 2)

        self.assertEqual(len(document.paragraphs[0].headings), 1)
        self.assertEqual(len(document.paragraphs[0].sentences), 1)

        self.assertEqual(to_unicode(document.paragraphs[0].headings[0]),
            "Toto je nadpis prvej úrovne")
        self.assertEqual(to_unicode(document.paragraphs[0].sentences[0]),
            "Toto je prvý odstavec a to je fajn.")

        self.assertEqual(len(document.paragraphs[1].headings), 0)
        self.assertEqual(len(document.paragraphs[1].sentences), 2)

        self.assertEqual(to_unicode(document.paragraphs[1].sentences[0]),
            "Tento text je tu aby vyplnil prázdne miesto v srdci súboru.")
        self.assertEqual(to_unicode(document.paragraphs[1].sentences[1]),
            "Aj súbory majú predsa city.")
