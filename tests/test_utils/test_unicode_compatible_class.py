# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import pytest

from sumy import _compat as compat


BYTES_STRING = "ľščťžáýíééäúňô €đ€Ł¤".encode("utf-8")
UNICODE_STRING = "ľščťžáýíééäúňô €đ€Ł¤"
NATIVE_STRING = compat.to_string(UNICODE_STRING)


@compat.unicode_compatible
class O(object):
    def __unicode__(self):
        return UNICODE_STRING


def _assert_strings_equal(str1, str2):
    assert type(str1) is type(str2)
    assert str1 == str2


@pytest.mark.skipif(not compat.PY3, reason="Python 2 doesn't support method `__bytes__`")
def test_native_bytes():
    returned = bytes(O())
    _assert_strings_equal(BYTES_STRING, returned)


@pytest.mark.skipif(compat.PY3, reason="Python 3 doesn't support method `__unicode__`")
def test_native_unicode():
    returned = unicode(O())
    _assert_strings_equal(UNICODE_STRING, returned)


def test_to_bytes():
    returned = compat.to_bytes(O())
    _assert_strings_equal(BYTES_STRING, returned)


def test_to_string():
    returned = compat.to_string(O())
    _assert_strings_equal(NATIVE_STRING, returned)


def test_to_unicode():
    returned = compat.to_unicode(O())
    _assert_strings_equal(UNICODE_STRING, returned)
