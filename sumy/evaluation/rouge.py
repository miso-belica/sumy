

from collections import Counter

from ..models.dom import Sentence


def _get_ngrams(n, text):
    ngram_set = set()
    text_length = len(text)
    max_index_ngram_start = text_length - n
    for i in range(max_index_ngram_start + 1):
        ngram_set.add(tuple(text[i:i + n]))
    return ngram_set


def _split_into_words(sentences):
    full_text_words = []
    for s in sentences:
        if not isinstance(s, Sentence):
            raise (TypeError("Object in collection must be of type Sentence"))
        full_text_words.extend(s.words)
    return full_text_words


def _get_word_ngrams(n, sentences):
    assert (len(sentences) > 0)
    assert (n > 0)

    words = set()
    for sentence in sentences:
        words.update(_get_ngrams(n, _split_into_words([sentence])))

    return words


def _get_index_of_lcs(x, y):
    return len(x), len(y)


def _len_lcs(x, y):
    """
    Returns the length of the Longest Common Subsequence between sequences x
    and y.
    Source: http://www.algorithmist.com/index.php/Longest_Common_Subsequence

    :param x: sequence of words
    :param y: sequence of words
    :returns integer: Length of LCS between x and y
    """
    table = _lcs(x, y)
    n, m = _get_index_of_lcs(x, y)
    return table[n, m]


def _lcs(x, y):
    """
    Computes the length of the longest common subsequence (lcs) between two
    strings. The implementation below uses a DP programming algorithm and runs
    in O(nm) time where n = len(x) and m = len(y).
    Source: http://www.algorithmist.com/index.php/Longest_Common_Subsequence

    :param x: collection of words
    :param y: collection of words
    :returns table: dictionary of coord and len lcs
    """
    n, m = _get_index_of_lcs(x, y)
    table = {}
    for i in range(n + 1):
        for j in range(m + 1):
            if i == 0 or j == 0:
                table[i, j] = 0
            elif x[i - 1] == y[j - 1]:
                table[i, j] = table[i - 1, j - 1] + 1
            else:
                table[i, j] = max(table[i - 1, j], table[i, j - 1])
    return table


def _recon_lcs_with_positions(x, y):
    """
    Returns the Longest Subsequence between x and y as (item, position) pairs.
    Source: http://www.algorithmist.com/index.php/Longest_Common_Subsequence

    The position is the 1-based index of the item in `x`, which is what makes
    subsequences of different `y` comparable: two occurrences of the same word
    in `x` are distinct pairs, so they survive being collected into a set.

    :param x: sequence of words
    :param y: sequence of words
    :returns sequence: LCS of x and y as (word, position in x) pairs
    """
    table = _lcs(x, y)

    def _recon(i, j):
        if i == 0 or j == 0:
            return []
        elif x[i - 1] == y[j - 1]:
            return _recon(i - 1, j - 1) + [(x[i - 1], i)]
        elif table[i - 1, j] > table[i, j - 1]:
            return _recon(i - 1, j)
        else:
            return _recon(i, j - 1)

    i, j = _get_index_of_lcs(x, y)
    return tuple(_recon(i, j))


def _recon_lcs(x, y):
    """
    Returns the Longest Subsequence between x and y.

    :param x: sequence of words
    :param y: sequence of words
    :returns sequence: LCS of x and y
    """
    return tuple(word for word, _position in _recon_lcs_with_positions(x, y))


def rouge_n(evaluated_sentences, reference_sentences, n=2):
    """
    Computes ROUGE-N of two text collections of sentences.
    Sourece: http://research.microsoft.com/en-us/um/people/cyl/download/
    papers/rouge-working-note-v1.3.1.pdf

    :param evaluated_sentences:
        The sentences that have been picked by the summarizer
    :param reference_sentences:
        The sentences from the reference set
    :param n: Size of ngram.  Defaults to 2.
    :returns:
        float 0 <= ROUGE-N <= 1, where 0 means no overlap and 1 means
        exactly the same.
    :raises ValueError:
        raises exception if a param has len <= 0 or if the reference sentences
        are too short to hold a single n-gram of that size
    """
    if len(evaluated_sentences) <= 0 or len(reference_sentences) <= 0:
        raise (ValueError("Collections must contain at least 1 sentence."))

    evaluated_ngrams = _get_word_ngrams(n, evaluated_sentences)
    reference_ngrams = _get_word_ngrams(n, reference_sentences)
    reference_count = len(reference_ngrams)

    # ROUGE-N is a recall metric, so only the reference is a denominator. A
    # reference shorter than n words holds no n-gram at all and there is nothing
    # to recall from it. An evaluated summary without n-grams is fine and scores 0.
    if reference_count <= 0:
        raise (ValueError(f"Reference sentences must contain at least 1 n-gram of size {n}."))

    # Gets the overlapping ngrams between evaluated and reference
    overlapping_ngrams = evaluated_ngrams.intersection(reference_ngrams)
    overlapping_count = len(overlapping_ngrams)

    return overlapping_count / reference_count


def rouge_1(evaluated_sentences, reference_sentences):
    """
    Rouge-N where N=1.  This is a commonly used metric.

    :param evaluated_sentences:
        The sentences that have been picked by the summarizer
    :param reference_sentences:
        The sentences from the reference set
    :returns:
        float 0 <= ROUGE-N <= 1, where 0 means no overlap and 1 means
        exactly the same.
    """
    return rouge_n(evaluated_sentences, reference_sentences, 1)


def rouge_2(evaluated_sentences, reference_sentences):
    """
    Rouge-N where N=2.  This is a commonly used metric.

    :param evaluated_sentences:
        The sentences that have been picked by the summarizer
    :param reference_sentences:
        The sentences from the reference set
    :returns:
        float 0 <= ROUGE-N <= 1, where 0 means no overlap and 1 means
        exactly the same.
    """
    return rouge_n(evaluated_sentences, reference_sentences, 2)


def _f_lcs(llcs, m, n):
    """
    Computes the LCS-based F-measure score
    Source: http://research.microsoft.com/en-us/um/people/cyl/download/papers/
    rouge-working-note-v1.3.1.pdf

    The score is computed from R_lcs = llcs/m, P_lcs = llcs/n and
    beta = P_lcs/R_lcs as F_lcs = ((1 + beta^2)*R_lcs*P_lcs) / (R_lcs + (beta^2)*P_lcs).
    Substituting R_lcs, P_lcs and beta into that expression and cancelling
    reduces it to the closed form used below:

        F_lcs = llcs * (m^2 + n^2) / (m^3 + n^3)

    Both forms are equal for a non-empty LCS, but the closed form has no
    removable singularity at llcs == 0. Computing beta as P_lcs/R_lcs divides
    by zero whenever the LCS is empty, even though F is plainly 0 there, since
    a summary with no common subsequence has neither precision nor recall.

    :param llcs: Length of LCS
    :param m: number of words in reference summary
    :param n: number of words in candidate summary
    :returns float: LCS-based F-measure score
    """
    return llcs * (m ** 2 + n ** 2) / (m ** 3 + n ** 3)


def rouge_l_sentence_level(evaluated_sentences, reference_sentences):
    """
    Computes ROUGE-L (sentence level) of two text collections of sentences.
    http://research.microsoft.com/en-us/um/people/cyl/download/papers/
    rouge-working-note-v1.3.1.pdf

    Calculated according to:
    R_lcs = LCS(X,Y)/m
    P_lcs = LCS(X,Y)/n
    F_lcs = ((1 + beta^2)*R_lcs*P_lcs) / (R_lcs + (beta^2) * P_lcs)

    where:
    X = reference summary
    Y = Candidate summary
    m = length of reference summary
    n = length of candidate summary

    :param evaluated_sentences:
        The sentences that have been picked by the summarizer
    :param reference_sentences:
        The sentences from the reference set
    :returns float: F_lcs
    :raises ValueError: raises exception if a param has len <= 0 or holds no word
    """
    if len(evaluated_sentences) <= 0 or len(reference_sentences) <= 0:
        raise (ValueError("Collections must contain at least 1 sentence."))
    reference_words = _split_into_words(reference_sentences)
    evaluated_words = _split_into_words(evaluated_sentences)
    m = len(reference_words)
    n = len(evaluated_words)
    if m <= 0 or n <= 0:
        raise (ValueError("Collections must contain at least 1 word."))
    lcs = _len_lcs(evaluated_words, reference_words)
    return _f_lcs(lcs, m, n)


def _union_lcs_positions(evaluated_sentences, reference_sentence):
    """
    Returns the union of the longest common subsequences between the reference
    sentence r_i and every sentence of the candidate summary C, as
    (word, position in r_i) pairs.

    :param evaluated_sentences:
        The sentences that have been picked by the summarizer
    :param reference_sentence:
        One of the sentences in the reference summaries
    :returns set: the covered (word, position in r_i) pairs
    :raises ValueError: raises exception if a param has len <= 0
    """
    if len(evaluated_sentences) <= 0:
        raise (ValueError("Collections must contain at least 1 sentence."))

    lcs_union = set()
    reference_words = _split_into_words([reference_sentence])
    for eval_s in evaluated_sentences:
        evaluated_words = _split_into_words([eval_s])
        lcs_union |= set(_recon_lcs_with_positions(reference_words, evaluated_words))

    return lcs_union


def _union_lcs(evaluated_sentences, reference_sentence):
    """
    Returns LCS_u(r_i, C), the number of words of the reference sentence r_i
    covered by the union of the longest common subsequences it shares with the
    sentences of the candidate summary C. For example, if
    r_i= w1 w2 w3 w4 w5, and C contains two sentences: c1 = w1 w2 w6 w7 w8 and
    c2 = w1 w3 w8 w9 w5, then the longest common subsequence of r_i and c1 is
    “w1 w2” and the longest common subsequence of r_i and c2 is “w1 w3 w5”. The
    union longest common subsequence of r_i, c1, and c2 is “w1 w2 w3 w5”, so
    LCS_u(r_i, C) = 4 out of the 5 words of r_i.

    The count is deliberately *not* normalized here. The summary level score
    normalizes the sum over all reference sentences by the total number of
    reference words (see `rouge_l_summary_level`), so normalizing per sentence
    as well would count the reference length twice.

    :param evaluated_sentences:
        The sentences that have been picked by the summarizer
    :param reference_sentence:
        One of the sentences in the reference summaries
    :returns int: LCS_u(r_i, C)
    :raises ValueError: raises exception if a param has len <= 0
    """
    return len(_union_lcs_positions(evaluated_sentences, reference_sentence))


def rouge_l_summary_level(evaluated_sentences, reference_sentences):
    """
    Computes ROUGE-L (summary level) of two text collections of sentences.
    http://research.microsoft.com/en-us/um/people/cyl/download/papers/
    rouge-working-note-v1.3.1.pdf

    Calculated according to:
    R_lcs = SUM(1, u)[LCS<union>(r_i,C)]/m
    P_lcs = SUM(1, u)[LCS<union>(r_i,C)]/n
    F_lcs = ((1 + beta^2)*R_lcs*P_lcs) / (R_lcs + (beta^2) * P_lcs)

    where:
    SUM(i,u) = SUM from i through u
    u = number of sentences in reference summary
    C = Candidate summary made up of v sentences
    m = number of words in reference summary
    n = number of words in candidate summary

    :param evaluated_sentences:
        The sentences that have been picked by the summarizer
    :param reference_sentences:
        The sentences from the reference set
    :returns float: F_lcs
    :raises ValueError: raises exception if a param has len <= 0 or holds no word
    """
    if len(evaluated_sentences) <= 0 or len(reference_sentences) <= 0:
        raise (ValueError("Collections must contain at least 1 sentence."))

    # total number of words in reference sentences
    m = len(_split_into_words(reference_sentences))

    # total number of words in evaluated sentences
    n = len(_split_into_words(evaluated_sentences))

    if m <= 0 or n <= 0:
        raise (ValueError("Collections must contain at least 1 word."))

    # LCS_u is counted in positions of the reference sentence, so the same
    # candidate word may be covered once per reference sentence. Clip each word
    # to the number of times the candidate summary actually contains it, as
    # ROUGE-1.5.5 does, otherwise a repetitive reference inflates the sum above
    # the length of the candidate and F_lcs can exceed 1.
    covered_words = Counter()
    for ref_s in reference_sentences:
        for word, _position in _union_lcs_positions(evaluated_sentences, ref_s):
            covered_words[word] += 1

    available_words = Counter(_split_into_words(evaluated_sentences))
    union_lcs_sum_across_all_references = sum(
        min(count, available_words[word]) for word, count in covered_words.items()
    )
    return _f_lcs(union_lcs_sum_across_all_references, m, n)
