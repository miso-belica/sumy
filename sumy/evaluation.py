# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals


def precision(evaluated_sentences, reference_sentences):
    """
    Intrinsic method of evaluation for extracts. It is computed as
    P(E) = A / B, where:

    - A is count of common sentences occurring in both extracts.
    - B is count of sentences in evaluated extract.

    :parameter iterable evaluated_sentences:
        Sentences of evaluated extract.
    :parameter iterable reference_sentences:
        Sentences of reference extract.
    :returns float:
        Returns 0.0 <= P(E) <= 1.0
    """
    return _divide_evaluation(reference_sentences, evaluated_sentences)


def recall(evaluated_sentences, reference_sentences):
    """
    Intrinsic method of evaluation for extracts. It is computed as
    R(E) = A / C, where:

    - A is count of common sentences in both extracts.
    - C is count of sentences in reference extract.

    :parameter iterable evaluated_sentences:
        Sentences of evaluated extract.
    :parameter iterable reference_sentences:
        Sentences of reference extract.
    :returns float:
        Returns 0.0 <= R(E) <= 1.0
    """
    return _divide_evaluation(evaluated_sentences, reference_sentences)


def _divide_evaluation(numerator_sentences, denominator_sentences):
    denominator_sentences = frozenset(denominator_sentences)
    numerator_sentences = frozenset(numerator_sentences)

    common_count = len(denominator_sentences & numerator_sentences)
    choosen_count = len(denominator_sentences)

    return 0.0 if choosen_count == 0 else common_count / choosen_count
