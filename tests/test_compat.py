# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from case import unittest
from nose import SkipTest
from sumy import _compat as py3k


BYTES_STRING = "ľščťžáýíééäúňô €đ€Ł¤".encode("utf8")
UNICODE_STRING = "ľščťžáýíééäúňô €đ€Ł¤"


class TestPy3k(unittest.TestCase):
    def assertStringsEqual(self, str1, str2, *args):
        self.assertEqual(type(str1), type(str2), *args)
        self.assertEqual(str1, str2, *args)

    def test_bytes_to_bytes(self):
        returned = py3k.to_bytes(BYTES_STRING)
        self.assertStringsEqual(BYTES_STRING, returned)

    def test_unicode_to_bytes(self):
        returned = py3k.to_bytes(UNICODE_STRING)
        self.assertStringsEqual(BYTES_STRING, returned)

    def test_str_object_to_bytes(self):
        value = UNICODE_STRING if py3k.PY3 else BYTES_STRING
        instance = self.__build_test_instance("__str__", value)

        returned = py3k.to_bytes(instance)
        self.assertStringsEqual(BYTES_STRING, returned)

    def test_unicode_object_to_bytes(self):
        if not py3k.PY3:
            raise SkipTest("Py2 object has `__str__` method called 1st")

        instance = self.__build_test_instance("__str__", UNICODE_STRING)

        returned = py3k.to_bytes(instance)
        self.assertStringsEqual(BYTES_STRING, returned)

    def test_repr_object_to_bytes(self):
        value = UNICODE_STRING if py3k.PY3 else BYTES_STRING
        instance = self.__build_test_instance("__repr__", value)

        returned = py3k.to_bytes(instance)
        self.assertStringsEqual(BYTES_STRING, returned)

    def test_data_to_unicode(self):
        returned = py3k.to_unicode(BYTES_STRING)
        self.assertStringsEqual(UNICODE_STRING, returned)

    def test_unicode_to_unicode(self):
        returned = py3k.to_unicode(UNICODE_STRING)
        self.assertStringsEqual(UNICODE_STRING, returned)

    def test_str_object_to_unicode(self):
        value = UNICODE_STRING if py3k.PY3 else BYTES_STRING
        instance = self.__build_test_instance("__str__", value)

        returned = py3k.to_unicode(instance)
        self.assertStringsEqual(UNICODE_STRING, returned)

    def test_unicode_object_to_unicode(self):
        method = "__str__" if py3k.PY3 else "__unicode__"
        instance = self.__build_test_instance(method, UNICODE_STRING)

        returned = py3k.to_unicode(instance)
        self.assertStringsEqual(UNICODE_STRING, returned)

    def test_repr_object_to_unicode(self):
        value = UNICODE_STRING if py3k.PY3 else BYTES_STRING
        instance = self.__build_test_instance("__repr__", value)

        returned = py3k.to_unicode(instance)
        self.assertStringsEqual(UNICODE_STRING, returned)

    def __build_test_instance(self, tested_method, value):
        class Object(object):
            def __init__(self, value):
                self.value = value

        setattr(Object, tested_method, lambda self: self.value)
        return Object(value)

    def test_lambda_is_callable(self):
        self.assertTrue(py3k.callable(lambda: None))

    def test_function_is_callable(self):
        def foo(x):
            return x

        self.assertTrue(py3k.callable(foo))

    def test_method_is_callable(self):
        self.assertTrue(py3k.callable(self.test_method_is_callable))

    def test_object_is_callable(self):
        class O(object):
            def __call__(self):
                pass

        self.assertTrue(py3k.callable(O()))

    def test_extended_object_is_callable(self):
        class O(object):
            def __call__(self):
                pass

        class S(O):
            pass

        self.assertTrue(py3k.callable(S()))

    def test_int_is_not_callable(self):
        self.assertFalse(py3k.callable(1))

    def test_string_is_not_callable(self):
        self.assertFalse(py3k.callable("not callable"))

    def test_object_is_not_callable(self):
        class O(object):
            pass

        self.assertFalse(py3k.callable(O()))
