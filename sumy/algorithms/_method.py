# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals


from collections import namedtuple
from operator import attrgetter
from .._py3k import to_unicode


SentenceInfo = namedtuple("SentenceInfo", ("sentence", "order", "rating",))


def null_stemmer(object):
    return to_unicode(object).lower()


class AbstractSummarizationMethod(object):
    def __init__(self, document, stemmer=null_stemmer):
        self._document = document
        self._stemmer = stemmer

    def __call__(self, sentences_count):
        raise NotImplementedError("This method should be overriden in subclass")

    def stem_word(self, word):
        return self._stemmer(self.normalize_word(word))

    def normalize_word(self, word):
        return to_unicode(word).lower()

    def _get_best_sentences(self, rated_sentences, count):
        infos = (SentenceInfo(s, o, r) for o, (s, r,) in enumerate(rated_sentences))

        # sort sentences by rating in descending order
        infos = sorted(infos, key=attrgetter("rating"), reverse=True)
        # get `count` first best rated sentences
        infos = infos[:count]
        # sort sentences by their order in document
        infos = sorted(infos, key=attrgetter("order"))

        return tuple(i.sentence for i in infos)
