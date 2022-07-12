# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from sumy._compat import to_unicode
from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.html import HtmlParser
from .utils import expand_resource_path


def test_annotated_text():
    path = expand_resource_path("snippets/paragraphs.html")
    url = "http://www.snippet.org/paragraphs.html"
    parser = HtmlParser.from_file(path, url, Tokenizer("czech"))

    document = parser.document

    assert len(document.paragraphs) == 2

    assert len(document.paragraphs[0].headings) == 1
    assert len(document.paragraphs[0].sentences) == 1

    assert to_unicode(document.paragraphs[0].headings[0]) == "Toto je nadpis prvej úrovne"
    assert to_unicode(document.paragraphs[0].sentences[0]) == "Toto je prvý odstavec a to je fajn."

    assert len(document.paragraphs[1].headings) == 0
    assert len(document.paragraphs[1].sentences) == 2

    assert to_unicode(document.paragraphs[1].sentences[0]) == "Tento text je tu aby vyplnil prázdne miesto v srdci súboru."
    assert to_unicode(document.paragraphs[1].sentences[1]) == "Aj súbory majú predsa city."

def test_from_url():
    url = "https://it.wikipedia.org/wiki/Parsing"
    LANG = "italian"
    parser = HtmlParser.from_url(url, Tokenizer(LANG))
    document = parser.document
    test_str = "In informatica, il parsing, analisi sintattica o parsificazione è un processo che analizza un flusso continuo di dati in ingresso ( input, letti per esempio da un file o una tastiera) in modo da determinare la correttezza della sua struttura grazie ad una data grammatica formale."

    assert document.paragraphs[0].sentences[0]._text == test_str, "There should not be empty space between words and punctations."

