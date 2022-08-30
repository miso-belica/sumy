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


def test_no_whitespace_before_punctuation_characters():
    text = """
    <p>In <a href="/wiki/Informatica" title="Informatica">informatica</a>, il <b>parsing</b>, 
    <b>analisi sintattica</b> o <b>parsificazione</b> è un processo che analizza un flusso 
    continuo di dati in ingresso ..."""
    parser = HtmlParser.from_string(text, "https://it.wikipedia.org/wiki/Parsing", Tokenizer("italian"))

    assert str(parser.document.paragraphs[0].sentences[0]) == (
        "In informatica, il parsing, analisi sintattica o parsificazione è un processo che analizza un flusso\n"
        "continuo di dati in ingresso ..."
    )

