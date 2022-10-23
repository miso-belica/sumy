# Changelog

## 0.11.0 (2022-10-23)
- **FIX:** Greek stemmer bug fix by @NC0DER in https://github.com/miso-belica/sumy/pull/175
* **FIX:** Avoid to add empty space between words and punctations. by @gianpd in https://github.com/miso-belica/sumy/pull/178
* **DOC:** Fix a few typos by @timgates42 in https://github.com/miso-belica/sumy/pull/182
* **FEATURE:** Add Arabic language support by @issam9 in https://github.com/miso-belica/sumy/pull/181

## 0.10.0 (2022-04-21)
- **FEATURE:** Add support for Ukrainian language in https://github.com/miso-belica/sumy/pull/168
- **FEATURE:** Add support for the Greek Language by @NC0DER in https://github.com/miso-belica/sumy/pull/169
- **FEATURE:** Return the summary size by custom callable object in https://github.com/miso-belica/sumy/pull/161
- **FIX:** Compatibility for `from collections import Sequence` for Python 3.10
- **FIX:** Fix SumBasicSummarizer with stemmer in https://github.com/miso-belica/sumy/pull/166

## 0.9.0 (2021-10-21)
- **INCOMPATIBILITY** Dropped official support for Python 2.7. It should still work if you install Python 2 compatible dependencies.
- **FEATURE:** Add basic Korean support by @kimbyungnam in https://github.com/miso-belica/sumy/pull/129
- **FEATURE:** Add support for the Hebrew language by @miso-belica in https://github.com/miso-belica/sumy/pull/151
- **FIX:** Allow words with dashes/apostrophe returned from tokenizer by @miso-belica in https://github.com/miso-belica/sumy/pull/144
- **FIX:** Ignore empty sentences from tokenizer by @miso-belica in https://github.com/miso-belica/sumy/pull/153
- Basic documentation by @miso-belica in https://github.com/miso-belica/sumy/pull/133
- Speedup of the TextRank algorithm by @miso-belica in https://github.com/miso-belica/sumy/pull/140
- Fix missing license in sdist by @dopplershift in https://github.com/miso-belica/sumy/pull/157
- added test and call for stemmer by @bdalal in https://github.com/miso-belica/sumy/pull/131
- Fix simple typo: referene -> reference by @timgates42 in https://github.com/miso-belica/sumy/pull/143
- Add codecov service to tests by @miso-belica in https://github.com/miso-belica/sumy/pull/136
- Add gitpod config by @miso-belica in https://github.com/miso-belica/sumy/pull/138
- Try to run Python 3.7 and 3.8 on TravisCI by @miso-belica in https://github.com/miso-belica/sumy/pull/130
- Fix TravisCI for Python 3.4 by @miso-belica in https://github.com/miso-belica/sumy/pull/134

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
