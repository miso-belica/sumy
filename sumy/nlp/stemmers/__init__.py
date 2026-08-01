

from typing import ClassVar

import nltk.stem.snowball as nltk_stemmers_module

from ..._compat import to_unicode
from ...utils import normalize_language
from .czech import stem_word as czech_stemmer
from .greek import stem_word as greek_stemmer
from .polish import stem_word as polish_stemmer
from .ukrainian import stem_word as ukrainian_stemmer


def null_stemmer(object):
    """Converts given object to unicode with lower letters."""
    return to_unicode(object).lower()


class Stemmer:
    SPECIAL_STEMMERS: ClassVar[dict] = {
        'czech': czech_stemmer,
        'slovak': czech_stemmer,
        'hebrew': null_stemmer,
        'chinese': null_stemmer,
        'japanese': null_stemmer,
        'korean': null_stemmer,
        'ukrainian': ukrainian_stemmer,
        'greek': greek_stemmer,
        'polish': polish_stemmer,
    }

    def __init__(self, language):
        language = normalize_language(language)
        self._stemmer = null_stemmer
        if language.lower() in self.SPECIAL_STEMMERS:
            self._stemmer = self.SPECIAL_STEMMERS[language.lower()]
            return
        stemmer_classname = language.capitalize() + 'Stemmer'
        try:
            stemmer_class = getattr(nltk_stemmers_module, stemmer_classname)
        except AttributeError:
            raise LookupError(f"Stemmer is not available for language {language}.")
        self._stemmer = stemmer_class().stem

    def __call__(self, word):
        return self._stemmer(word)