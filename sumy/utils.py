# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals


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
