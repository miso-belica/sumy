# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import pytest

from sumy import _compat as py3k


BYTES_STRING = "ľščťžáýíééäúňô €đ€Ł¤".encode("utf-8")
UNICODE_STRING = "ľščťžáýíééäúňô €đ€Ł¤"


def _build_test_instance(tested_method, value):
    class Object(object):
        def __init__(self, value):
            self.value = value

    setattr(Object, tested_method, lambda self: self.value)
    return Object(value)


def _assert_strings_equal(str1, str2):
    assert type(str1) is type(str2)
    assert str1 == str2


def test_bytes_to_bytes():
    returned = py3k.to_bytes(BYTES_STRING)
    _assert_strings_equal(BYTES_STRING, returned)


def test_unicode_to_bytes():
    returned = py3k.to_bytes(UNICODE_STRING)
    _assert_strings_equal(BYTES_STRING, returned)


def test_str_object_to_bytes():
    value = UNICODE_STRING if py3k.PY3 else BYTES_STRING
    instance = _build_test_instance("__str__", value)

    returned = py3k.to_bytes(instance)
    _assert_strings_equal(BYTES_STRING, returned)


@pytest.mark.skipif(not py3k.PY3, reason="Py2 object has `__str__` method called 1st")
def test_unicode_object_to_bytes():
    instance = _build_test_instance("__str__", UNICODE_STRING)

    returned = py3k.to_bytes(instance)
    _assert_strings_equal(BYTES_STRING, returned)


def test_repr_object_to_bytes():
    value = UNICODE_STRING if py3k.PY3 else BYTES_STRING
    instance = _build_test_instance("__repr__", value)

    returned = py3k.to_bytes(instance)
    _assert_strings_equal(BYTES_STRING, returned)


def test_data_to_unicode():
    returned = py3k.to_unicode(BYTES_STRING)
    _assert_strings_equal(UNICODE_STRING, returned)


def test_unicode_to_unicode():
    returned = py3k.to_unicode(UNICODE_STRING)
    _assert_strings_equal(UNICODE_STRING, returned)


def test_str_object_to_unicode():
    value = UNICODE_STRING if py3k.PY3 else BYTES_STRING
    instance = _build_test_instance("__str__", value)

    returned = py3k.to_unicode(instance)
    _assert_strings_equal(UNICODE_STRING, returned)


def test_unicode_object_to_unicode():
    method = "__str__" if py3k.PY3 else "__unicode__"
    instance = _build_test_instance(method, UNICODE_STRING)

    returned = py3k.to_unicode(instance)
    _assert_strings_equal(UNICODE_STRING, returned)


def test_repr_object_to_unicode():
    value = UNICODE_STRING if py3k.PY3 else BYTES_STRING
    instance = _build_test_instance("__repr__", value)

    returned = py3k.to_unicode(instance)
    _assert_strings_equal(UNICODE_STRING, returned)
