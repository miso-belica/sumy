# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals


from collections import namedtuple
from operator import attrgetter
from .._py3k import to_unicode


SentenceInfo = namedtuple("SentenceInfo", ("sentence", "order", "rating",))


class AbstractSummarizationMethod(object):
    def __init__(self, document, stemmer):
        self._document = document
        self._stemmer = stemmer

    def __call__(self, sentences_count):
        raise NotImplementedError("This method should be overriden in subclass")

    def stem_word(self, word):
        return self._stemmer(to_unicode(word).lower())

    def _get_best_sentences(self, rated_sentences, count):
        infos = (SentenceInfo(s, o, r) for o, (s, r,) in enumerate(rated_sentences))

        # sort sentences by rating in descending order
        infos = sorted(infos, key=attrgetter("rating"), reverse=True)
        # get `count` first best rated sentences
        infos = infos[:count]
        # sort sentences by their order in document
        infos = sorted(infos, key=attrgetter("order"))

        return tuple(i.sentence for i in infos)
