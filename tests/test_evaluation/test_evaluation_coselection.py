# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

import pytest
from pytest import approx

from sumy.evaluation import precision, recall, f_score


def test_precision_empty_evaluated():
    with pytest.raises(ValueError):
        precision((), ("s1", "s2", "s3", "s4", "s5"))


def test_precision_empty_reference():
    with pytest.raises(ValueError):
        precision(("s1", "s2", "s3", "s4", "s5"), ())


def test_precision_no_match():
    result = precision(("s1", "s2", "s3", "s4", "s5"), ("s6", "s7", "s8"))

    assert result == 0.0


def test_precision_reference_smaller():
    result = precision(("s1", "s2", "s3", "s4", "s5"), ("s1",))

    assert result == approx(0.2)


def test_precision_evaluated_smaller():
    result = precision(("s1",), ("s1", "s2", "s3", "s4", "s5"))

    assert result == approx(1.0)


def test_precision_equals():
    sentences = ("s1", "s2", "s3", "s4", "s5")
    result = precision(sentences, sentences)

    assert result == approx(1.0)


def test_recall_empty_evaluated():
    with pytest.raises(ValueError):
        recall((), ("s1", "s2", "s3", "s4", "s5"))


def test_recall_empty_reference():
    with pytest.raises(ValueError):
        recall(("s1", "s2", "s3", "s4", "s5"), ())


def test_recall_no_match():
    result = recall(("s1", "s2", "s3", "s4", "s5"), ("s6", "s7", "s8"))

    assert result == 0.0


def test_recall_reference_smaller():
    result = recall(("s1", "s2", "s3", "s4", "s5"), ("s1",))

    assert result == approx(1.0)


def test_recall_evaluated_smaller():
    result = recall(("s1",), ("s1", "s2", "s3", "s4", "s5"))

    assert result == approx(0.20)


def test_recall_equals():
    sentences = ("s1", "s2", "s3", "s4", "s5")
    result = recall(sentences, sentences)

    assert result == approx(1.0)


def test_basic_f_score_empty_evaluated():
    with pytest.raises(ValueError):
        f_score((), ("s1", "s2", "s3", "s4", "s5"))


def test_basic_f_score_empty_reference():
    with pytest.raises(ValueError):
        f_score(("s1", "s2", "s3", "s4", "s5"), ())


def test_basic_f_score_no_match():
    result = f_score(("s1", "s2", "s3", "s4", "s5"), ("s6", "s7", "s8"))

    assert result == 0.0


def test_basic_f_score_reference_smaller():
    result = f_score(("s1", "s2", "s3", "s4", "s5"), ("s1",))

    assert result == approx(1/3)


def test_basic_f_score_evaluated_smaller():
    result = f_score(("s1",), ("s1", "s2", "s3", "s4", "s5"))

    assert result == approx(1/3)


def test_basic_f_score_equals():
    sentences = ("s1", "s2", "s3", "s4", "s5")
    result = f_score(sentences, sentences)

    assert result == approx(1.0)


def test_f_score_1():
    sentences = (("s1",), ("s1", "s2", "s3", "s4", "s5"))
    result = f_score(*sentences, weight=2.0)

    p = 1/1
    r = 1/5
    # ( (W^2 + 1) * P * R ) / ( W^2 * P + R )
    expected = (5 * p * r) / (4 * p + r)

    assert result == approx(expected)


def test_f_score_2():
    sentences = (("s1", "s3", "s6"), ("s1", "s2", "s3", "s4", "s5"))
    result = f_score(*sentences, weight=0.5)

    p = 2/3
    r = 2/5
    # ( (W^2 + 1) * P * R ) / ( W^2 * P + R )
    expected = (1.25 * p * r) / (0.25 * p + r)

    assert result == approx(expected)
