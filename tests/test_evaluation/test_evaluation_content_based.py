# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

import pytest
from pytest import approx

from sumy.evaluation import cosine_similarity, unit_overlap
from sumy.models import TfDocumentModel
from sumy.nlp.tokenizers import Tokenizer


def test_wrong_arguments():
    text = "Toto je moja veta, to sa nedá poprieť."
    model = TfDocumentModel(text, Tokenizer("czech"))

    with pytest.raises(ValueError):
        cosine_similarity(text, text)
    with pytest.raises(ValueError):
        cosine_similarity(text, model)
    with pytest.raises(ValueError):
        cosine_similarity(model, text)


def test_empty_model():
    text = "Toto je moja veta, to sa nedá poprieť."
    model = TfDocumentModel(text, Tokenizer("czech"))
    empty_model = TfDocumentModel([])

    with pytest.raises(ValueError):
        cosine_similarity(empty_model, empty_model)
    with pytest.raises(ValueError):
        cosine_similarity(empty_model, model)
    with pytest.raises(ValueError):
        cosine_similarity(model, empty_model)


def test_cosine_exact_match():
    text = "Toto je moja veta, to sa nedá poprieť."
    model = TfDocumentModel(text, Tokenizer("czech"))

    assert cosine_similarity(model, model) == approx(1.0)


def test_cosine_no_match():
    tokenizer = Tokenizer("czech")
    model1 = TfDocumentModel("Toto je moja veta. To sa nedá poprieť!", tokenizer)
    model2 = TfDocumentModel("Hento bolo jeho slovo, ale možno klame.", tokenizer)

    assert cosine_similarity(model1, model2) == approx(0.0)


def test_cosine_half_match():
    tokenizer = Tokenizer("czech")
    model1 = TfDocumentModel("Veta aká sa tu len veľmi ťažko hľadá", tokenizer)
    model2 = TfDocumentModel("Teta ktorá sa tu iba veľmi zle hľadá", tokenizer)

    assert cosine_similarity(model1, model2) == approx(0.5)


def test_unit_overlap_empty():
    tokenizer = Tokenizer("english")
    model = TfDocumentModel("", tokenizer)

    with pytest.raises(ValueError):
        unit_overlap(model, model)


def test_unit_overlap_wrong_arguments():
    tokenizer = Tokenizer("english")
    model = TfDocumentModel("", tokenizer)

    with pytest.raises(ValueError):
        unit_overlap("model", "model")
    with pytest.raises(ValueError):
        unit_overlap("model", model)
    with pytest.raises(ValueError):
        unit_overlap(model, "model")


def test_unit_overlap_exact_match():
    tokenizer = Tokenizer("czech")
    model = TfDocumentModel("Veta aká sa len veľmi ťažko hľadá.", tokenizer)

    assert unit_overlap(model, model) == approx(1.0)


def test_unit_overlap_no_match():
    tokenizer = Tokenizer("czech")
    model1 = TfDocumentModel("Toto je moja veta. To sa nedá poprieť!", tokenizer)
    model2 = TfDocumentModel("Hento bolo jeho slovo, ale možno klame.", tokenizer)

    assert unit_overlap(model1, model2) == approx(0.0)


def test_unit_overlap_half_match():
    tokenizer = Tokenizer("czech")
    model1 = TfDocumentModel("Veta aká sa tu len veľmi ťažko hľadá", tokenizer)
    model2 = TfDocumentModel("Teta ktorá sa tu iba veľmi zle hľadá", tokenizer)

    assert unit_overlap(model1, model2) == approx(1/3)
