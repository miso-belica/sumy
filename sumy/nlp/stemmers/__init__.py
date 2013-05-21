# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from ..._compat import to_unicode


def null_stemmer(object):
    "Converts given object to unicode with lower letters."
    return to_unicode(object).lower()
