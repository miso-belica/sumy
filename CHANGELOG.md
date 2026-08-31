# Changelog

## Unreleased
- **FEATURE:** sumy runs in the browser. `micropip.install("sumy")` now works under Pyodide/PyEmscripten ([PEP 783](https://peps.python.org/pep-0783/)), and there is a live demo at https://miso-belica.github.io/sumy/demo/. See [running sumy in the browser](docs/in-the-browser.md).
- **FEATURE:** `breadability`, `lxml-html-clean`, `requests`, `setuptools` and `docopt-ng` are no longer installed on Emscripten, where they cannot be resolved or cannot work. Every other platform installs them as before.
- **FEATURE:** `sumy.utils.fetch_url` works in the browser, using Pyodide's synchronous `XMLHttpRequest` client instead of `requests`. Only same-origin or CORS-enabled URLs can answer, and `timeout` does not apply there.
- **FIX:** `sumy.utils` and `sumy.parsers.html` no longer import `requests` and `breadability` at import time; both now raise `ValueError` naming what to install, as the rest of sumy does for a missing optional dependency, and the HTML one repeats the underlying import error so a missing `lxml` is not reported as a missing `breadability`.
- **CHORE:** Rebuilt the Docker image with all language extras, a multi-stage `uv sync` build, and a non-root user.

## 0.13.0 (2026-08-12)
- **INCOMPATIBILITY:** `cosine_similarity`, `unit_overlap`, `AbstractSummarizer.__init__`, `ItemsCount` and the ROUGE evaluation functions raise `TypeError` instead of `ValueError` for invalid argument types.
- **INCOMPATIBILITY:** `Rouge-L (Summary Level)` scores change to match the official `ROUGE-1.5.5.pl`.
- **INCOMPATIBILITY:** ROUGE-L functions raise `ValueError`, not `ZeroDivisionError`, when either input has no words.
- **INCOMPATIBILITY:** `nltk>=3.9` is now required, since 3.8.2 withdrew the `punkt` pickle over CVE-2024-39705. See https://github.com/miso-belica/sumy/issues/216
- **INCOMPATIBILITY:** Gave every dependency a lower bound, so installing sumy alongside an old release no longer silently produces a broken environment.
- **FIX:** Excluded `nltk==3.10.1`, which fails to import when the venv sits inside the working directory. See https://github.com/nltk/nltk/issues/3730
- **FIX:** Raised the `setuptools` floor to 70.0.0 (78.1.1 on Python 3.9+) to fix two advisories, GHSA-cx63-2mw6-8hw5 and GHSA-5rjg-fvgr-3xxf. Python 3.8 stays on 70.0.0 and remains exposed to the second, as 75.3.4 is its last installable setuptools.
- **FIX:** Capped `setuptools<82`, since breadability imports `pkg_resources`, which v82 removed. See https://github.com/miso-belica/sumy/issues/235
- **FIX:** Fixed `ZeroDivisionError` in `rouge_l_sentence_level` and `rouge_l_summary_level` when the summary and reference share no words. See https://github.com/miso-belica/sumy/issues/128
- **FIX:** Fixed `ZeroDivisionError` in `rouge_n` for a reference shorter than the n-gram size; it now raises `ValueError`.
- **FIX:** Fixed `Rouge-L` losing repeated reference words, which capped even a perfect summary below 1.0.
- **FIX:** Fixed `Rouge-L (Summary Level)` scoring above 1.0 for a repetitive reference; hits are now clipped to the candidate's word counts, as `ROUGE-1.5.5.pl` does.
- **FIX:** Fixed `PlaintextParser` treating an ordinary sentence in a caseless script as a heading. See https://github.com/miso-belica/sumy/issues/110 and https://github.com/miso-belica/sumy/issues/215
- **FIX:** Fixed `KeyError` in `SumBasicSummarizer` from inconsistent word processing order. See https://github.com/miso-belica/sumy/pull/240
- **CHORE:** Removed leftover Python 2 compatibility code.

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
