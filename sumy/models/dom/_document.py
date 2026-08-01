

from itertools import chain

from ..._compat import unicode_compatible
from ...utils import cached_property


@unicode_compatible
class ObjectDocumentModel:
    def __init__(self, paragraphs):
        self._paragraphs = tuple(paragraphs)

    @property
    def paragraphs(self):
        return self._paragraphs

    @cached_property
    def sentences(self):
        sentences = (p.sentences for p in self._paragraphs)
        return tuple(chain(*sentences))

    @cached_property
    def headings(self):
        headings = (p.headings for p in self._paragraphs)
        return tuple(chain(*headings))

    @cached_property
    def words(self):
        words = (p.words for p in self._paragraphs)
        return tuple(chain(*words))

    def __unicode__(self):
        return f"<DOM with {len(self.paragraphs):d} paragraphs>"

    def __repr__(self):
        return self.__str__()
