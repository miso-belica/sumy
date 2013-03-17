# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from ..models import TfDocumentModel as TfModel


def cosine_similarity(model1, model2):
    """
    Computes cosine similarity of two text documents. Each document
    has to be represented as TF model of non-empty document.

    :returns float:
        0 <= cos <= 1, where 0 means independence and 1 means
        exactly the same.
    """
    if not (isinstance(model1, TfModel) and isinstance(model2, TfModel)):
        raise ValueError(
            "Arguments has to be instances of 'sumy.models.TfDocumentModel'")

    terms = frozenset(model1.terms) | frozenset(model2.terms)

    numerator = 0.0
    for term in terms:
        numerator += model1.term_frequency(term) * model2.term_frequency(term)

    denominator = model1.magnitude * model2.magnitude
    if denominator == 0.0:
        raise ValueError("Document model can't be empty. Given %r & %r" % (
            model1, model2))

    return numerator / denominator


def unit_overlap(model1, model2):
    if not (isinstance(model1, TfModel) and isinstance(model2, TfModel)):
        raise ValueError(
            "Arguments has to be instances of 'sumy.models.TfDocumentModel'")

    terms1 = frozenset(model1.terms)
    terms2 = frozenset(model2.terms)

    if not terms1 and not terms2:
        raise ValueError(
            "Documents can't be empty. Please pass the valid documents.")

    common_terms_count = len(terms1 & terms2)
    return common_terms_count / (len(terms1) + len(terms2) - common_terms_count)
