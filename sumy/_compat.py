# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from sys import version_info


PY3 = version_info[0] == 3


if PY3:
    bytes = bytes
    unicode = str
else:
    bytes = str
    unicode = unicode
string_types = (bytes, unicode,)


try:
    from itertools import ifilterfalse as ffilter
except ImportError:
    from itertools import filterfalse as ffilter


try:
    from collections import Counter
except ImportError:
    # Python < 2.7
    from itertools import groupby

    def Counter(iterable):
        iterable = sorted(iterable)
        return dict((key, len(tuple(group))) for key, group in groupby(iterable))


def unicode_compatible(cls):
    """
    Decorator for unicode compatible classes. Method ``__unicode__``
    has to be implemented to work decorator as expected.
    """
    if PY3:
        cls.__str__ = cls.__unicode__
        cls.__bytes__ = lambda self: self.__str__().encode("utf8")
    else:
        cls.__str__ = lambda self: self.__unicode__().encode("utf8")

    return cls


def to_string(object):
    return to_unicode(object) if PY3 else to_bytes(object)


def to_bytes(object):
    if isinstance(object, bytes):
        return object
    elif isinstance(object, unicode):
        return object.encode("utf8")
    else:
        # try encode instance to bytes
        return instance_to_bytes(object)


def to_unicode(object):
    if isinstance(object, unicode):
        return object
    elif isinstance(object, bytes):
        return object.decode("utf8")
    else:
        # try decode instance to unicode
        return instance_to_unicode(object)


def instance_to_bytes(instance):
    if PY3:
        if hasattr(instance, "__bytes__"):
            return bytes(instance)
        elif hasattr(instance, "__str__"):
            return unicode(instance).encode("utf8")
    else:
        if hasattr(instance, "__str__"):
            return bytes(instance)
        elif hasattr(instance, "__unicode__"):
            return unicode(instance).encode("utf8")

    return to_bytes(repr(instance))


def instance_to_unicode(instance):
    if PY3:
        if hasattr(instance, "__str__"):
            return unicode(instance)
        elif hasattr(instance, "__bytes__"):
            return bytes(instance).decode("utf8")
    else:
        if hasattr(instance, "__unicode__"):
            return unicode(instance)
        elif hasattr(instance, "__str__"):
            return bytes(instance).decode("utf8")

    return to_unicode(repr(instance))
