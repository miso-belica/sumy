"""The code of the stem_word function relies on the greek stemmer found in this python module
greek-stemmer-pos (https://pypi.org/project/greek-stemmer-pos/),
(https://github.com/kpech21/Greek-Stemmer).
greek-stemmer_pos is licensed under GNU Lesser General Public License v3.0.
Greek-stemmer Copyright (C) 2021 Konstantinos Pechlivanis.
The license notice is included in the same directory.
"""


def stem_word(word):
    """
    Stem_word() checks if the associated word has the correct tag and stems it.
    If it does not have the correct one then it throws an exception.
    So we check all available POS tags, until we get the correct one.
    In the future a working greek POS tagger can substitute the code of this function.
    """
    try:
        from greek_stemmer import stemmer as gr_stemmer
    except ImportError:
        raise ValueError("Greek stemmer requires greek_stemmer. Please, install it by command 'pip install greek-stemmer-pos'.")

    total_tags = {
        'DDT', 'IDT', 'NNM', 'NNF', 'NNN', 'NNSM', 'NNSF', 'NNSN', 'NNPM', 'NNPF', 
        'NNPN', 'NNPSM', 'NNPSF', 'NNPSN', 'VB', 'VBD', 'VBF', 'MD', 'VBS', 'VBDS', 
        'VBFS', 'JJM', 'JJF', 'JJN', 'JJSM', 'JJSF', 'JJSN', 'CD', 'VBG', 'VBP', 
        'VBPD', 'PRP', 'PP', 'REP', 'DP', 'IP', 'WP', 'QP', 'INP', 'RB', 'IN', 
        'CC', 'RP', 'UH', 'FW', 'DATE', 'TIME', 'AB', 'SYM'
    }
    consonants = set('ΒΓΔΖΘΚΛΜΝΞΠΡΣΤΦΧΨ')
    all_stemmed = set()
    
    if len(word) < 4:
        return word.lower()

    for tag in total_tags:
        try:
            stemmed = gr_stemmer.stem_word(word.lower(), tag)
            if stemmed[-1].upper() in consonants:
                all_stemmed.add(stemmed)
        except:
            pass

    return min(all_stemmed or [word], key = len).lower()
