# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from ._compat import to_string, to_bytes, unicode


class Object(object):
    __slots__ = ()

    def __to_unicode(self):
        text = self._to_string()
        assert isinstance(text, unicode)
        return text

    def _to_string(self):
        """"""
        raise NotImplementedError("You have to override method `_to_string`")

    def __bytes__(self):
        return to_bytes(self.__to_unicode())

    def __str__(self):
        return to_string(self.__to_unicode())

    def __unicode__(self):
        return self.__to_unicode()

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.__str__())
