

from itertools import chain

from ..._compat import unicode_compatible
from ...utils import cached_property
from ._sentence import Sentence


@unicode_compatible
class Paragraph:
    __slots__ = (
        "_cached_property_headings",
        "_cached_property_sentences",
        "_cached_property_words",
        "_sentences",
    )

    def __init__(self, sentences):
        sentences = tuple(sentences)
        for sentence in sentences:
            if not isinstance(sentence, Sentence):
                raise TypeError("Only instances of class 'Sentence' are allowed.")

        self._sentences = sentences

    @cached_property
    def sentences(self):
        return tuple(s for s in self._sentences if not s.is_heading)

    @cached_property
    def headings(self):
        return tuple(s for s in self._sentences if s.is_heading)

    @cached_property
    def words(self):
        return tuple(chain(*(s.words for s in self._sentences)))

    def __unicode__(self):
        return f"<Paragraph with {len(self.headings):d} headings & {len(self.sentences):d} sentences>"

    def __repr__(self):
        return self.__str__()
