# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from ..models import TfDocumentModel as TfModel


def cosine_similarity(evaluated_model, reference_model):
    """
    Computes cosine similarity of two text documents. Each document
    has to be represented as TF model of non-empty document.

    :returns float:
        0 <= cos <= 1, where 0 means independence and 1 means
        exactly the same.
    """
    if not (isinstance(evaluated_model, TfModel) and isinstance(reference_model, TfModel)):
        raise ValueError(
            "Arguments has to be instances of 'sumy.models.TfDocumentModel'")

    terms = frozenset(evaluated_model.terms) | frozenset(reference_model.terms)

    numerator = 0.0
    for term in terms:
        numerator += evaluated_model.term_frequency(term) * reference_model.term_frequency(term)

    denominator = evaluated_model.magnitude * reference_model.magnitude
    if denominator == 0.0:
        raise ValueError("Document model can't be empty. Given %r & %r" % (
            evaluated_model, reference_model))

    return numerator / denominator


def unit_overlap(evaluated_model, reference_model):
    """
    Computes unit overlap of two text documents. Documents
    has to be represented as TF models of non-empty document.

    :returns float:
        0 <= overlap <= 1, where 0 means no match and 1 means
        exactly the same.
    """
    if not (isinstance(evaluated_model, TfModel) and isinstance(reference_model, TfModel)):
        raise ValueError(
            "Arguments has to be instances of 'sumy.models.TfDocumentModel'")

    terms1 = frozenset(evaluated_model.terms)
    terms2 = frozenset(reference_model.terms)

    if not terms1 and not terms2:
        raise ValueError(
            "Documents can't be empty. Please pass the valid documents.")

    common_terms_count = len(terms1 & terms2)
    return common_terms_count / (len(terms1) + len(terms2) - common_terms_count)
