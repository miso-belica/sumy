# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

import sys

from os.path import dirname, abspath, join
from ._py3k import to_string


def cached_property(getter):
    """
    Decorator that converts a method into memoized property.
    The decorator works as expected only for immutable properties.
    """
    def decorator(self):
        if not hasattr(self, "__cached_property_data"):
            self.__cached_property_data = {}

        key = getter.__name__
        if key not in self.__cached_property_data:
            self.__cached_property_data[key] = getter(self)

        return self.__cached_property_data[key]

    decorator.__name__ = getter.__name__
    decorator.__module__ = getter.__module__
    decorator.__doc__ = getter.__doc__

    return property(decorator)


def expand_resource_path(path):
    directory = dirname(sys.modules["sumy"].__file__)
    directory = abspath(directory)
    return join(directory, to_string("data"), to_string(path))
