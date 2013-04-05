# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

import sys

from functools import wraps
from os.path import dirname, abspath, join, exists
from ._compat import to_string, to_unicode, string_types


def cached_property(getter):
    """
    Decorator that converts a method into memoized property.
    The decorator works as expected only for classes with
    attribute '__dict__' and immutable properties.
    """
    @wraps(getter)
    def decorator(self):
        key = "_cached_property_" + getter.__name__

        if not hasattr(self, key):
            setattr(self, key, getter(self))

        return getattr(self, key)

    return property(decorator)


def expand_resource_path(path):
    directory = dirname(sys.modules["sumy"].__file__)
    directory = abspath(directory)
    return join(directory, to_string("data"), to_string(path))


def get_stop_word(language):
    path = expand_resource_path("stopwords/%s.txt" % language)
    if not exists(path):
        raise ValueError("Stop-words are not available for language %s." % language)

    with open(path, "rb") as file:
        return frozenset(to_unicode(w.rstrip()) for w in file.readlines())
