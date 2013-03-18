# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

import math

from pprint import pformat
from collections import Sequence
from .._compat import to_unicode, to_string, unicode, string_types, Counter


class TfDocumentModel(object):
    """Term-Frequency document model (term = word)."""
    def __init__(self, words, tokenizer=None):
        if isinstance(words, string_types) and tokenizer is None:
            raise ValueError(
                "Tokenizer has to be given if ``words`` is not a sequence.")
        elif isinstance(words, string_types):
            words = tokenizer.to_words(to_unicode(words))
        elif not isinstance(words, Sequence):
            raise ValueError(
                "Parameter ``words`` has to be sequence or string with tokenizer given.")

        self._terms = Counter(map(unicode.lower, words))

    @property
    def magnitude(self):
        """
        Lenght/norm/magnitude of vector representation of document.
        This is usually denoted by ||d||.
        """
        return math.sqrt(sum(t**2 for t in self._terms.values()))

    @property
    def terms(self):
        return self._terms.keys()

    def most_frequent_terms(self, count=0):
        """
        Returns ``count`` of terms sorted by their frequency
        in descending order.

        :parameter int count:
            Max. number of returned terms. Value 0 means no limit (default).
        """
        # sort terms by number of occurrences in descending order
        terms = sorted(self._terms.items(), key=lambda i: -i[1])

        terms = tuple(i[0] for i in terms)
        if count == 0:
            return terms
        elif count > 0:
            return terms[:count]
        else:
            raise ValueError(
                "Only non-negative values are allowed for count of terms.")

    def term_frequency(self, term):
        """Returns frequency of term in document."""
        return self._terms.get(term, 0)

    def __repr__(self):
        return "<TfDocumentModel %s>" % pformat(self._terms)
