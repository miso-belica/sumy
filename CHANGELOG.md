# Changelog

## Unreleased
- **INCOMPATIBILITY** `Rouge-L (Summary Level)` scores change. `_union_lcs` normalized every reference sentence by the sum of its per-sentence LCS lengths, so `rouge_l_summary_level` summed ratios and divided them by a word count again. It now sums the number of covered reference words, as described in the ROUGE working note. A summary identical to the reference scores 1.0 instead of 0.2. Scores from previous versions are not comparable.
- **FIX:** Fixed `ZeroDivisionError` in `rouge_l_summary_level` for a reference sentence that shares no word with the summary, reported in https://github.com/miso-belica/sumy/issues/128
- **FIX:** Fixed `ZeroDivisionError` in `rouge_l_sentence_level` for a summary that shares no word with the reference. `_f_lcs` derived `beta` as `P_lcs/R_lcs`, which divides by zero on an empty LCS; it now uses the algebraically equivalent closed form `llcs * (m^2 + n^2) / (m^3 + n^3)`, which is 0 there. Reported in https://github.com/miso-belica/sumy/issues/128
- **FIX:** Fixed `KeyError` in `SumBasicSummarizer` caused by inconsistent word processing order in https://github.com/miso-belica/sumy/pull/240
- **BREAKING:** `cosine_similarity`, `unit_overlap`, `AbstractSummarizer.__init__`, `ItemsCount` and the ROUGE evaluation functions (`rouge_n`, `rouge_1`, `rouge_2`, `rouge_l_sentence_level`, `rouge_l_summary_level`) now raise `TypeError` instead of `ValueError` for invalid argument types.
- **CHORE:** Removed leftover Python 2 compatibility code (`sumy._compat.PY3` and the dead branches it guarded), now that the package only supports Python 3.8+.

## 0.12.0 (2026-02-14)
- **FEATURE:** Replace docopt with docopt-ng in https://github.com/miso-belica/sumy/pull/191
- **FEATURE:** Add Swedish stopwords in https://github.com/miso-belica/sumy/pull/195
- **FEATURE:** Add Thai language support in https://github.com/miso-belica/sumy/pull/192
- **FEATURE:** Add new Python versions in https://github.com/miso-belica/sumy/pull/212
- **FEATURE:** Migrate package metadata to pyproject.toml in https://github.com/miso-belica/sumy/pull/227
- **FEATURE:** Add Polish language support in https://github.com/miso-belica/sumy/pull/226
- **FIX** Fixed `ItemsCount` to raise `ValueError` in https://github.com/miso-belica/sumy/pull/203
- **FIX** Allow to pass language with any-case letters in https://github.com/miso-belica/sumy/pull/207
- **FIX** Add timeout to 'from_url' in https://github.com/miso-belica/sumy/pull/186
- **FIX** Fixed bug with LexRank's power iteration in https://github.com/miso-belica/sumy/pull/194

## 0.11.0 (2022-10-23)
- **FIX:** Greek stemmer bug fix in https://github.com/miso-belica/sumy/pull/175
* **FIX:** Avoid to add empty space between words and punctations. in https://github.com/miso-belica/sumy/pull/178
* **DOC:** Fix a few typos in https://github.com/miso-belica/sumy/pull/182
* **FEATURE:** Add Arabic language support in https://github.com/miso-belica/sumy/pull/181

## 0.10.0 (2022-04-21)
- **FEATURE:** Add support for Ukrainian language in https://github.com/miso-belica/sumy/pull/168
- **FEATURE:** Add support for the Greek Language in https://github.com/miso-belica/sumy/pull/169
- **FEATURE:** Return the summary size by custom callable object in https://github.com/miso-belica/sumy/pull/161
- **FIX:** Compatibility for `from collections import Sequence` for Python 3.10
- **FIX:** Fix SumBasicSummarizer with stemmer in https://github.com/miso-belica/sumy/pull/166

## 0.9.0 (2021-10-21)
- **INCOMPATIBILITY** Dropped official support for Python 2.7. It should still work if you install Python 2 compatible dependencies.
- **FEATURE:** Add basic Korean support in https://github.com/miso-belica/sumy/pull/129
- **FEATURE:** Add support for the Hebrew language in https://github.com/miso-belica/sumy/pull/151
- **FIX:** Allow words with dashes/apostrophe returned from tokenizer in https://github.com/miso-belica/sumy/pull/144
- **FIX:** Ignore empty sentences from tokenizer in https://github.com/miso-belica/sumy/pull/153
- Basic documentation in https://github.com/miso-belica/sumy/pull/133
- Speedup of the TextRank algorithm in https://github.com/miso-belica/sumy/pull/140
- Fix missing license in sdist in https://github.com/miso-belica/sumy/pull/157
- added test and call for stemmer in https://github.com/miso-belica/sumy/pull/131
- Fix simple typo: referene -> reference in https://github.com/miso-belica/sumy/pull/143
- Add codecov service to tests in https://github.com/miso-belica/sumy/pull/136
- Add gitpod config in https://github.com/miso-belica/sumy/pull/138
- Try to run Python 3.7 and 3.8 on TravisCI in https://github.com/miso-belica/sumy/pull/130
- Fix TravisCI for Python 3.4 in https://github.com/miso-belica/sumy/pull/134

## 0.8.1 (2019-05-19)
- Open files for `PlaintextParser` in UTF-8 encoding [#123](https://github.com/miso-belica/sumy/pull/123)

## 0.8.0 (2019-05-18)
- Added support for Italian language [#114](https://github.com/miso-belica/sumy/pull/114)
- Added support for ISO-639 language codes (`en`, `de`, `sk`, ...). [#106](https://github.com/miso-belica/sumy/pull/106)
- `TextRankSummarizer` uses iterative algorithm. Previous algorithm is called `ReductionSummarizer`. [#100](https://github.com/miso-belica/sumy/pull/100)

## 0.7.0 (2017-07-22)
- Added support for Chinese. [#93](https://github.com/miso-belica/sumy/pull/93)

## 0.6.0 (2017-03-05)
- Dropped support for distutils when installing sumy.
- Added support for Japanese. [#79](https://github.com/miso-belica/sumy/pull/79)
- Fixed incorrect n-grams computation for more sentences. [#84](https://github.com/miso-belica/sumy/pull/84)
- Fixed NLTK dependency for Python 3.3. NLTK 3.2 dropped support for Python 3.3 so sumy needs 3.1.

## 0.5.1 (2016-11-17)
- Fixed missing stopwords in SumBasic summarizer. [#74](https://github.com/miso-belica/sumy/pull/74)

## 0.5.0 (2016-11-12)
- Added "--text" CLI parameter to summarize text in Emacs and other tools. [#67](https://github.com/miso-belica/sumy/pull/67)
- Fixed computation of cosine similarity in LexRank summarizator. [#63](https://github.com/miso-belica/sumy/pull/63)
- Fixed resource searching in .egg packages. [#53](https://github.com/miso-belica/sumy/pull/53)

## 0.4.1 (2016-03-06)
- Added support for Portuguese and Spanish. [#49](https://github.com/miso-belica/sumy/pull/49) [#51](https://github.com/miso-belica/sumy/pull/51)
- Better error message when NLTK tokenizers are missing.

## 0.4.0 (2015-12-04)
-   Dropped support for Python 2.6 and 3.2. Only 2.7/3.3+ are officially supported now. Time to move :)
-   CLI: Better message for unknown format.
-   LexRank: fixed power method computation.
-   Added some extra abbreviations (english, german) into tokenizer for better output.
-   SumBasic: Added new summarization method - SumBasic. Thanks to [Julian Griggs](https://github.com/JulianGriggs).
-   KL: Added new summarization method - KL. Thanks to [Julian Griggs](https://github.com/JulianGriggs).
-   Added dependency [requests](http://docs.python-requests.org/en/latest/) to fix issues with downloading pages.
-   Better documentation of expected Plaintext document format.

## 0.3.0 (2014-06-07)
-   Added possibility to specify format of input document for URL & stdin. Thanks to [@Lucas-C](https://github.com/Lucas-C).
-   Added possibility to specify custom file with stop-words in CLI. Thanks to [@Lucas-C](https://github.com/Lucas-C).
-   Added support for French language (added stopwords & stemmer). Thanks to [@Lucas-C](https://github.com/Lucas-C).
-   Function `sumy.utils.get_stop_words` raises `LookupError` instead of `ValueError` for unknown language.
-   Exception `LookupError` is raised for unknown language of stemmer instead of falling silently to `null_stemmer`.

## 0.2.1 (2014-01-23)
-   Fixed installation of my own readability fork. Added `breadability` to the dependencies instead of it [#8](https://github.com/miso-belica/sumy/issues/8).
    Thanks to [@pratikpoddar](https://github.com/pratikpoddar).

## 0.2.0 (2014-01-18)
-   Removed dependency on SciPy [#7](https://github.com/miso-belica/sumy/pull/7). Use `numpy.linalg.svd` implementation.
    Thanks to [Shantanu](https://github.com/baali).

## 0.1.0 (2013-10-20)
-   First public release.
