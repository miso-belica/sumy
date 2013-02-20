# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from .._py3k import to_unicode


null_stemmer = lambda o: to_unicode(o).lower()
