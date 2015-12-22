# -*- coding: utf-8 -*-
from __future__ import division, print_function, \
    unicode_literals, absolute_import

from ._summarizer import AbstractSummarizer


class StopWordsMixin(object):
    _stop_words = frozenset()

    @property
    def stop_words(self):
        return self._stop_words

    @stop_words.setter
    def stop_words(self, words):
        if not issubclass(self.__class__, AbstractSummarizer):
            raise ValueError('Class {} is not a subclass of AbstractSummarizer.'.format(self.__class__))

        self._stop_words = frozenset(map(self.normalize_word, words))

