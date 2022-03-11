import re

_PERFECTIVE_GROUND = r'(ив|ивши|ившись|ыв|ывши|ывшись((?<=[ая])(в|вши|вшись)))$'
# http://uk.wikipedia.org/wiki/Рефлексивне_дієслово
_REFLEXIVE = r'(с[яьи])$'
# http://uk.wikipedia.org/wiki/Прикметник + http://wapedia.mobi/uk/Прикметник
_ADJECTIVE = r'(ими|ій|ий|а|е|ова|ове|ів|є|їй|єє|еє|я|ім|ем|им|ім|их|іх|ою|йми|іми|у|ю|ого|ому|ої)$'
# http://uk.wikipedia.org/wiki/Дієприкметник
_PARTICIPLE = r'(ий|ого|ому|им|ім|а|ій|у|ою|ій|і|их|йми|их)$'
# http://uk.wikipedia.org/wiki/Дієслово
_VERB = r'(сь|ся|ив|ать|ять|у|ю|ав|али|учи|ячи|вши|ши|е|ме|ати|яти|є)$'
# http://uk.wikipedia.org/wiki/Іменник
_NOUN = r'(а|ев|ов|е|ями|ами|еи|и|ей|ой|ий|й|иям|ям|ием|ем|ам|ом|о|у|ах|иях|ях|ы|ь|ию|ью|ю|ия|ья|я|і|ові|ї|ею|єю|ою|є|еві|ем|єм|ів|їв|ю)$'
_RVRE = r'[аеиоуюяіїє]'
_DERIVATIONAL = r'[^аеиоуюяіїє][аеиоуюяіїє]+[^аеиоуюяіїє]+[аеиоуюяіїє].*(?<=о)сть?$'


def stem_word(word):
    """
    Based on https://drupal.org/project/ukstemmer and ported to Python https://github.com/Amice13/ukr_stemmer
    """
    word = _preprocess(word)
    if not re.search('[аеиоуюяіїє]', word):
        return word

    p = re.search(_RVRE, word)
    start = word[0:p.span()[1]]
    suffix = word[p.span()[1]:]

    # Step 1
    updated, suffix = _update_suffix(suffix, _PERFECTIVE_GROUND, '')
    if not updated:
        _, suffix = _update_suffix(suffix, _REFLEXIVE, '')
        updated, suffix = _update_suffix(suffix, _ADJECTIVE, '')
        if updated:
            updated, suffix = _update_suffix(suffix, _PARTICIPLE, '')
        else:
            updated, suffix = _update_suffix(suffix, _VERB, '')
            if not updated:
                _, suffix = _update_suffix(suffix, _NOUN, '')
    # Step 2
    updated, suffix = _update_suffix(suffix, 'и$', '')

    # Step 3
    if re.search(_DERIVATIONAL, suffix):
        updated, suffix = _update_suffix(suffix, 'ость$', '')

    # Step 4
    updated, suffix = _update_suffix(suffix, 'ь$', '')
    if updated:
        _, suffix = _update_suffix(suffix, 'ейше?$', '')
        _, suffix = _update_suffix(suffix, 'нн$', u'н')

    return start + suffix


def _preprocess(word):
    return word.lower().replace("'", '').replace('ё', 'е').replace('ъ', 'ї')


def _update_suffix(suffix, pattern, replacement):
    result = re.sub(pattern, replacement, suffix)
    return suffix != result, result
