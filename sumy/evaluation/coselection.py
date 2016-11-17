# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals


def f_score(evaluated_sentences, reference_sentences, weight=1.0):
    """
    Computation of F-Score measure. It is computed as
    F(E) = ( (W^2 + 1) * P(E) * R(E) ) / ( W^2 * P(E) + R(E) ), where:

    - P(E) is precision metrics of extract E.
    - R(E) is recall metrics of extract E.
    - W is a weighting factor that favours P(E) metrics
      when W > 1 and favours R(E) metrics when W < 1.

    If W = 1.0 (default value) basic F-Score is computed.
    It is equivalent to F(E) = (2 * P(E) * R(E)) / (P(E) + R(E)).

    :parameter iterable evaluated_sentences:
        Sentences of evaluated extract.
    :parameter iterable reference_sentences:
        Sentences of reference extract.
    :returns float:
        Returns 0.0 <= P(E) <= 1.0
    """
    p = precision(evaluated_sentences, reference_sentences)
    r = recall(evaluated_sentences, reference_sentences)

    weight **= 2 # weight = weight^2
    denominator = weight * p + r
    if denominator == 0.0:
        return 0.0
    else:
        return ((weight + 1) * p * r) / denominator


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

    if len(numerator_sentences) == 0 or len(denominator_sentences) == 0:
        raise ValueError("Both collections have to contain at least 1 sentence.")

    common_count = len(denominator_sentences & numerator_sentences)
    choosen_count = len(denominator_sentences)

    assert choosen_count != 0
    return common_count / choosen_count
