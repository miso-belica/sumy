# Changelog

## 0.8.0 (unreleased yet)
- `TextRankSummarizer` uses iterative algorithm. Previous algorithm is called `ReductionSummarizer` [#100](https://github.com/miso-belica/sumy/pull/100). Thanks to [@kmkurn](https://github.com/kmkurn).

## 0.7.0 (2017-07-22)
- Added support for Chinese. Thanks to [@astropeak](https://github.com/astropeak).

## 0.6.0 (2017-03-05)
- Dropped support for distutils when installing sumy.
- Added support for Japanese. Thanks to [@tuvistavie](https://github.com/tuvistavie).
- Fixed incorrect n-grams computation for more sentences. Thanks to [@odek53r](https://github.com/odek53r).
- Fixed NLTK dependency for Python 3.3. NLTK 3.2 dropped support for Python 3.3 so sumy needs 3.1.

## 0.5.1 (2016-11-17)
- Fixed missing stopwords in SumBasic summarizer.

## 0.5.0 (2016-11-12)
- Added "--text" CLI parameter to summarize text in Emacs and other tools. Thanks to [@FrancisMurillo](https://github.com/FrancisMurillo).
- Fixed computation of cosine similarity in LexRank summarizator.
- Fixed resource searching in .egg packages. Thanks to [@heni](https://github.com/heni).

## 0.4.1 (2016-03-06)
- Added support for Portuguese and Spanish.
- Better error mesage when NLTK tokenizers are missing.

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
