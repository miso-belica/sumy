# -*- coding: utf8 -*-

"""
Czech stemmer
Copyright © 2010 Luís Gomes <luismsgomes@gmail.com>.

Ported from the Java implementation available at:
    http://members.unine.ch/jacques.savoy/clef/index.html

Usage:
    czech_stemmer.py light|aggressive
"""

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

import re
import sys

from warnings import warn
from ..._compat import unicode


WORD_PATTERN = re.compile(r"^\w+$", re.UNICODE)


def stem_word(word, aggressive=False):
    if not isinstance(word, unicode):
        word = word.decode("utf8")

    if not WORD_PATTERN.match(word):
        return word

    if not word.islower() and not word.istitle() and not word.isupper():
        warn("skipping word with mixed case: " + word)
        return word

    stem = word.lower()
    stem = _remove_case(stem)
    stem = _remove_possessives(stem)

    if aggressive:
        stem = _remove_comparative(stem)
        stem = _remove_diminutive(stem)
        stem = _remove_augmentative(stem)
        stem = _remove_derivational(stem)

    if word.isupper():
        return stem.upper()
    if word.istitle():
        return stem.title()

    return stem


def _remove_case(word):
    if len(word) > 7 and word.endswith("atech"):
        return word[:-5]

    if len(word) > 6:
        if word.endswith("ětem"):
            return _palatalize(word[:-3])
        if word.endswith("atům"):
            return word[:-4]

    if len(word) > 5:
        if word[-3:] in ("ech", "ich", "ích", "ého", "ěmi", "emi", "ému",
                         "ete", "eti", "iho", "ího", "ími", "imu"):
            return _palatalize(word[:-2])
        if word[-3:] in ("ách", "ata", "aty", "ých", "ama", "ami",
                         "ové", "ovi", "ými"):
            return word[:-3]

    if len(word) > 4:
        if word.endswith("em"):
            return _palatalize(word[:-1])
        if word[-2:] in ("es", "ém", "ím"):
            return _palatalize(word[:-2])
        if word[-2:] in ("ům", "at", "ám", "os", "us", "ým", "mi", "ou"):
            return word[:-2]

    if len(word) > 3:
        if word[-1] in "eiíě":
            return _palatalize(word)
        if word[-1] in "uyůaoáéý":
            return word[:-1]

    return word


def _remove_possessives(word):
    if len(word) > 5:
        if word[-2:] in ("ov", "ův"):
            return word[:-2]
        if word.endswith("in"):
            return _palatalize(word[:-1])
    return word


def _remove_comparative(word):
    if len(word) > 5:
        if word[-3:] in ("ejš", "ějš"):
            return _palatalize(word[:-2])
    return word


def _remove_diminutive(word):
    if len(word) > 7 and word.endswith("oušek"):
        return word[:-5]
    if len(word) > 6:
        if word[-4:] in ("eček", "éček", "iček", "íček", "enek", "ének",
                         "inek", "ínek"):
            return _palatalize(word[:-3])
        if word[-4:] in ("áček", "aček", "oček", "uček", "anek", "onek",
                         "unek", "ánek"):
            return _palatalize(word[:-4])
    if len(word) > 5:
        if word[-3:] in ("ečk", "éčk", "ičk", "íčk", "enk", "énk",
                         "ink", "ínk"):
            return _palatalize(word[:-3])
        if word[-3:] in ("áčk", "ačk", "očk", "učk", "ank", "onk",
                         "unk", "átk", "ánk", "ušk"):
            return word[:-3]
    if len(word) > 4:
        if word[-2:] in ("ek", "ék", "ík", "ik"):
            return _palatalize(word[:-1])
        if word[-2:] in ("ák", "ak", "ok", "uk"):
            return word[:-1]
    if len(word) > 3 and word[-1] == "k":
        return word[:-1]
    return word


def _remove_augmentative(word):
    if len(word) > 6 and word.endswith("ajzn"):
        return word[:-4]
    if len(word) > 5 and word[-3:] in ("izn", "isk"):
        return _palatalize(word[:-2])
    if len(word) > 4 and word.endswith("ák"):
        return word[:-2]
    return word


def _remove_derivational(word):
    if len(word) > 8 and word.endswith("obinec"):
        return word[:-6]
    if len(word) > 7:
        if word.endswith("ionář"):
            return _palatalize(word[:-4])
        if word[-5:] in ("ovisk", "ovstv", "ovišt", "ovník"):
            return word[:-5]
    if len(word) > 6:
        if word[-4:] in ("ásek", "loun", "nost", "teln", "ovec", "ovík",
                         "ovtv", "ovin", "štin"):
            return word[:-4]
        if word[-4:] in ("enic", "inec", "itel"):
            return _palatalize(word[:-3])
    if len(word) > 5:
        if word.endswith("árn"):
            return word[:-3]
        if word[-3:] in ("ěnk", "ián", "ist", "isk", "išt", "itb", "írn"):
            return _palatalize(word[:-2])
        if word[-3:] in ("och", "ost", "ovn", "oun", "out", "ouš",
                         "ušk", "kyn", "čan", "kář", "néř", "ník",
                         "ctv", "stv"):
            return word[:-3]
    if len(word) > 4:
        if word[-2:] in ("áč", "ač", "án", "an", "ář", "as"):
            return word[:-2]
        if word[-2:] in ("ec", "en", "ěn", "éř", "íř", "ic", "in", "ín",
                         "it", "iv"):
            return _palatalize(word[:-1])
        if word[-2:] in ("ob", "ot", "ov", "oň", "ul", "yn", "čk", "čn",
                         "dl", "nk", "tv", "tk", "vk"):
            return word[:-2]
    if len(word) > 3 and word[-1] in "cčklnt":
        return word[:-1]
    return word


def _palatalize(word):
    if word[-2:] in ("ci", "ce", "či", "če"):
        return word[:-2] + "k"

    if word[-2:] in ("zi", "ze", "ži", "že"):
        return word[:-2] + "h"

    if word[-3:] in ("čtě", "čti", "čtí"):
        return word[:-3] + "ck"

    if word[-3:] in ("ště", "šti", "ští"):
        return word[:-3] + "sk"

    return word[:-1]


if __name__ == '__main__':
    if len(sys.argv) != 2 or sys.argv[1] not in ("light", "aggressive"):
        sys.exit(__doc__.encode("utf8"))

    aggressive_stemming = bool(sys.argv[1] == "aggressive")
    for line in sys.stdin:
        words = tuple(w.decode("utf8") + " " + stem_word(w, aggressive_stemming) for w in line.split())
        print(*map(lambda s: s.encode("utf8"), words))
