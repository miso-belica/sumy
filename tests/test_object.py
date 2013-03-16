# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from case import unittest
from nose import SkipTest
from sumy import _py3k as py3k
from sumy._object import Object


BYTES_STRING = "ľščťžáýíééäúňô €đ€Ł¤".encode("utf8")
UNICODE_STRING = "ľščťžáýíééäúňô €đ€Ł¤"
NATIVE_STRING = py3k.to_string(UNICODE_STRING)


class O(Object):
    def _to_string(self):
        return UNICODE_STRING


class TestObject(unittest.TestCase):
    def setUp(self):
        self.o = O()

    def assertStringsEqual(self, str1, str2, *args):
        self.assertEqual(type(str1), type(str2), *args)
        self.assertEqual(str1, str2, *args)

    def test_native_bytes(self):
        if not py3k.PY3:
            raise SkipTest("Python 2 doesn't support method `__bytes__`")

        returned = bytes(self.o)
        self.assertStringsEqual(BYTES_STRING, returned)

    def test_native_unicode(self):
        if py3k.PY3:
            raise SkipTest("Python 3 doesn't support method `__unicode__`")

        returned = unicode(self.o)
        self.assertStringsEqual(UNICODE_STRING, returned)

    def test_to_bytes(self):
        returned = py3k.to_bytes(self.o)
        self.assertStringsEqual(BYTES_STRING, returned)

    def test_to_string(self):
        returned = py3k.to_string(self.o)
        self.assertStringsEqual(NATIVE_STRING, returned)

    def test_to_unicode(self):
        returned = py3k.to_unicode(self.o)
        self.assertStringsEqual(UNICODE_STRING, returned)
