# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

import sys
import requests
import pkgutil

from functools import wraps
from contextlib import closing
from os.path import dirname, abspath, join
from ._compat import to_string, to_unicode, string_types

from pycountry import languages

_HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/109.0",
    # "User-Agent": "Sumy (Automatic text summarizer) Version/%s" % __version__,
}


def normalize_language(language):
    for lookup_key in ("alpha_2", "alpha_3"):
        try:
            lang = languages.get(**{lookup_key: language})
            if lang:
                language = lang.name.lower()
        except KeyError:
            pass

    return language


def fetch_url(url, timeout=(3.05, 30)):
    with closing(requests.get(url, headers=_HTTP_HEADERS, timeout=timeout)) as response:
        response.raise_for_status()
        return response.content


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


def get_stop_words(language):
    language = normalize_language(language)
    try:
        stopwords_data = pkgutil.get_data("sumy", "data/stopwords/%s.txt" % language)
    except IOError:
        raise LookupError("Stop-words are not available for language %s." % language)
    return parse_stop_words(stopwords_data)


def read_stop_words(filename):
    with open(filename, "rb") as open_file:
        return parse_stop_words(open_file.read())


def parse_stop_words(data):
    return frozenset(w.rstrip() for w in to_unicode(data).splitlines() if w)


class ItemsCount(object):
    def __init__(self, value):
        self._value = value

    def __call__(self, sequence):
        if isinstance(self._value, string_types):
            if self._value.endswith("%"):
                total_count = len(sequence)
                percentage = int(self._value[:-1])
                # at least one sentence should be chosen
                count = max(1, total_count*percentage // 100)
                return sequence[:count]
            else:
                return sequence[:int(self._value)]
        elif isinstance(self._value, (int, float)):
            return sequence[:int(self._value)]
        else:
            ValueError("Unsuported value of items count '%s'." % self._value)

    def __repr__(self):
        return to_string("<ItemsCount: %r>" % self._value)
