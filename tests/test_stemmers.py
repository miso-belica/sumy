# -*- coding: utf-8 -*-

"""Simple tests to make sure all stemmers share the same API."""

from __future__ import absolute_import, division, print_function, unicode_literals

import pytest

from sumy.nlp.stemmers import null_stemmer, Stemmer


def test_missing_stemmer_language():
    with pytest.raises(LookupError):
        Stemmer("klingon")


def test_null_stemmer():
    assert "ľščťžýáíé" == null_stemmer("ľŠčŤžÝáÍé")


def test_english_stemmer():
    english_stemmer = Stemmer('english')
    assert "beauti" == english_stemmer("beautiful")


def test_german_stemmer():
    german_stemmer = Stemmer('german')
    assert "sterb" == german_stemmer("sterben")


def test_czech_stemmer():
    czech_stemmer = Stemmer('czech')
    assert "pěkn" == czech_stemmer("pěkný")


def test_french_stemmer():
    french_stemmer = Stemmer('czech')
    assert "jol" == french_stemmer("jolies")


def test_slovak_stemmer():
    expected = Stemmer("czech")
    actual = Stemmer("slovak")

    assert type(actual) is type(expected)
    assert expected.__dict__ == actual.__dict__


def test_greek_stemmer():
    greek_stemmer = Stemmer("greek")
    # The first assert covers the empty stem case.
    assert "οτ" == greek_stemmer("όταν")
    assert "εργαζ" == greek_stemmer("εργαζόμενος")
