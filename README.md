# Automatic text summarizer

[![image](https://api.travis-ci.org/miso-belica/sumy.png?branch=master)](https://travis-ci.org/miso-belica/sumy)

Simple library and command line utility for extracting summary from HTML
pages or plain texts. The package also contains simple evaluation
framework for text summaries. Implemented summarization methods are described in the [documentation](docs/summarizators.md).

Here are some other summarizers:

-   <https://github.com/thavelick/summarize/> - Python, TF (very simple)
-   [Reduction](https://github.com/adamfabish/Reduction) - Python,
    TextRank (simple)
-   [Open Text Summarizer](http://libots.sourceforge.net/) - C, TF
    without normalization
-   [Simple program that summarize
    text](https://github.com/xhresko/text-summarizer) - Python, TF
    without normalization
-   [Intro to Computational
    Linguistics](https://github.com/kylehardgrave/summarizer) - Java,
    LexRank
-   [Sumtract: Second project for UW LING
    572](https://github.com/stefanbehr/sumtract) - Python
-   [TextTeaser](https://github.com/MojoJolo/textteaser) - Scala
-   [PyTeaser](https://github.com/xiaoxu193/PyTeaser) - TextTeaser port
    in Python
-   [Automatic Document
    Summarizer](https://github.com/himanshujindal/Automatic-Text-Summarizer) -
    Java, Bipartite HITS (no sources)
-   [Pythia](https://github.com/giorgosera/pythia/blob/dev/analysis/summarization/summarization.py) -
    Python, LexRank & Centroid
-   [SWING](https://github.com/WING-NUS/SWING) - Ruby
-   [Topic Networks](https://github.com/bobflagg/Topic-Networks) - R,
    topic models & bipartite graphs
-   [Almus: Automatic Text
    Summarizer](http://textmining.zcu.cz/?lang=en&section=download) -
    Java, LSA (without source code)
-   [Musutelsa](http://www.musutelsa.jamstudio.eu/) - Java, LSA
    (always freezes)
-   <http://mff.bajecni.cz/index.php> - C++
-   [MEAD](http://www.summarization.com/mead/) - Perl, various methods +
    evaluation framework

## Installation

Make sure you have [Python](http://www.python.org/) 2.7/3.3+ and
[pip](https://crate.io/packages/pip/)
([Windows](http://docs.python-guide.org/en/latest/starting/install/win/),
[Linux](http://docs.python-guide.org/en/latest/starting/install/linux/))
installed. Run simply (preferred way):

```sh
$ [sudo] pip install sumy
```

Or for the fresh version:

```sh
$ [sudo] pip install git+git://github.com/miso-belica/sumy.git
```

## Usage

Sumy contains command line utility for quick summarization of documents.

```sh
$ sumy lex-rank --length=10 --url=http://en.wikipedia.org/wiki/Automatic_summarization # what's summarization?
$ sumy luhn --language=czech --url=http://www.zdrojak.cz/clanky/automaticke-zabezpeceni/
$ sumy edmundson --language=czech --length=3% --url=http://cs.wikipedia.org/wiki/Bitva_u_Lipan
$ sumy --help # for more info
```

Various evaluation methods for some summarization method can be executed
by commands below:

```sh
$ sumy_eval lex-rank reference_summary.txt --url=http://en.wikipedia.org/wiki/Automatic_summarization
$ sumy_eval lsa reference_summary.txt --language=czech --url=http://www.zdrojak.cz/clanky/automaticke-zabezpeceni/
$ sumy_eval edmundson reference_summary.txt --language=czech --url=http://cs.wikipedia.org/wiki/Bitva_u_Lipan
$ sumy_eval --help # for more info
```

## Python API

Or you can use sumy like a library in your project. Create file `sumy_example.py` ([don't name it `sumy.py`](https://stackoverflow.com/questions/41334622/python-sumy-no-module-named-sumy-parsers-html)) with the code below to test it.

```python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from sumy.parsers.html import HtmlParser
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words


LANGUAGE = "english"
SENTENCES_COUNT = 10


if __name__ == "__main__":
    url = "https://en.wikipedia.org/wiki/Automatic_summarization"
    parser = HtmlParser.from_url(url, Tokenizer(LANGUAGE))
    # or for plain text files
    # parser = PlaintextParser.from_file("document.txt", Tokenizer(LANGUAGE))
    # parser = PlaintextParser.from_string("Check this out.", Tokenizer(LANGUAGE))
    stemmer = Stemmer(LANGUAGE)

    summarizer = Summarizer(stemmer)
    summarizer.stop_words = get_stop_words(LANGUAGE)

    for sentence in summarizer(parser.document, SENTENCES_COUNT):
        print(sentence)
```

## Interesting projects using sumy

I found some interesting projects while browsing the interner or sometimes people wrote me an e-mail with questions and I was curious how they use the sumy :)

* [Learning to generate questions from text](https://software.intel.com/en-us/articles/using-natural-language-processing-for-smart-question-generation) - https://github.com/adityasarvaiya/Automatic_Question_Generation
* Summarize your video to any duration - https://github.com/aswanthkoleri/VideoMash and similar https://github.com/OpenGenus/vidsum
* Tool for collectively summarizing large discussions - https://github.com/amyxzhang/wikum
