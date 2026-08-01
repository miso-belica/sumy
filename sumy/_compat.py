

from collections.abc import Sequence
from itertools import filterfalse as ffilter

unicode = str
string_types = (bytes, unicode,)


def unicode_compatible(cls):
    """
    Decorator for unicode compatible classes. Method ``__unicode__``
    has to be implemented to work decorator as expected.
    """
    cls.__str__ = cls.__unicode__
    cls.__bytes__ = lambda self: self.__str__().encode("utf-8")

    return cls


def to_string(object):
    return to_unicode(object)


def to_bytes(object):
    if isinstance(object, bytes):
        return object
    elif isinstance(object, unicode):
        return object.encode("utf-8")
    else:
        # try encode instance to bytes
        return instance_to_bytes(object)


def to_unicode(object):
    if isinstance(object, unicode):
        return object
    elif isinstance(object, bytes):
        return object.decode("utf-8")
    else:
        # try decode instance to unicode
        return instance_to_unicode(object)


def instance_to_bytes(instance):
    if hasattr(instance, "__bytes__"):
        return bytes(instance)
    elif hasattr(instance, "__str__"):
        return unicode(instance).encode("utf-8")

    return to_bytes(repr(instance))


def instance_to_unicode(instance):
    if hasattr(instance, "__str__"):
        return unicode(instance)
    elif hasattr(instance, "__bytes__"):
        return bytes(instance).decode("utf-8")

    return to_unicode(repr(instance))
