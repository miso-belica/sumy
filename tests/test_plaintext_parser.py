# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.plaintext import PlaintextParser


def test_parse_plaintext():
    parser = PlaintextParser.from_string("""
        Ako sa máš? Ja dobre! A ty? No
        mohlo to byť aj lepšie!!! Ale pohodička.


        TOTO JE AKOŽE NADPIS
        A toto je text pod ním, ktorý je textový.
        A tak ďalej...
    """, Tokenizer("czech"))

    document = parser.document

    assert len(document.paragraphs) == 2

    assert len(document.paragraphs[0].headings) == 0
    assert len(document.paragraphs[0].sentences) == 5

    assert len(document.paragraphs[1].headings) == 1
    assert len(document.paragraphs[1].sentences) == 2


def test_parse_plaintext_long():
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

    assert len(document.paragraphs) == 5

    assert len(document.paragraphs[0].headings) == 0
    assert len(document.paragraphs[0].sentences) == 5

    assert len(document.paragraphs[1].headings) == 1
    assert len(document.paragraphs[1].sentences) == 2

    assert len(document.paragraphs[2].headings) == 1
    assert len(document.paragraphs[2].sentences) == 3

    assert len(document.paragraphs[3].headings) == 0
    assert len(document.paragraphs[3].sentences) == 1

    assert len(document.paragraphs[4].headings) == 0
    assert len(document.paragraphs[4].sentences) == 1
