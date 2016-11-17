Automatic text summarizer
=========================

|image|

Simple library and command line utility for extracting summary from HTML
pages or plain texts. The package also contains simple evaluation
framework for text summaries. Implemented summarization methods:

-  **Luhn** - heurestic method,
   `reference <http://ieeexplore.ieee.org/xpl/articleDetails.jsp?arnumber=5392672>`__
-  **Edmundson** heurestic method with previous statistic research,
   `reference <http://dl.acm.org/citation.cfm?doid=321510.321519>`__
-  **Latent Semantic Analysis, LSA** - one of the algorithm from
   http://scholar.google.com/citations?user=0fTuW_YAAAAJ&hl=en I think
   the author is using more advanced algorithms now. `Steinberger, J. a
   Ježek, K. Using latent semantic an and summary evaluation. In In
   Proceedings ISIM '04. 2004. S.
   93-100. <http://www.kiv.zcu.cz/~jstein/publikace/isim2004.pdf>`__
-  **LexRank** - Unsupervised approach inspired by algorithms PageRank
   and HITS,
   `reference <http://tangra.si.umich.edu/~radev/lexrank/lexrank.pdf>`__
-  **TextRank** - some sort of combination of a few resources that I
   found on the internet. I really don't remember the sources. Probably
   `Wikipedia <https://en.wikipedia.org/wiki/Automatic_summarization#Unsupervised_approaches:_TextRank_and_LexRank>`__
   and some papers in 1st page of Google :)
-  **SumBasic** - Method that is often used as a baseline in the
   literature. Source: `Read about
   SumBasic <http://www.cis.upenn.edu/~nenkova/papers/ipm.pdf>`__
-  **KL-Sum** - Method that greedily adds sentences to a summary so long
   as it decreases the KL Divergence. Source: `Read about
   KL-Sum <http://www.aclweb.org/anthology/N09-1041>`__

Here are some other summarizers:

-  https://github.com/thavelick/summarize/ - Python, TF (very simple)
-  `Reduction <https://github.com/adamfabish/Reduction>`__ - Python,
   TextRank (simple)
-  `Open Text Summarizer <http://libots.sourceforge.net/>`__ - C, TF
   without normalization
-  `Simple program that summarize
   text <https://github.com/xhresko/text-summarizer>`__ - Python, TF
   without normalization
-  `Intro to Computational
   Linguistics <https://github.com/kylehardgrave/summarizer>`__ - Java,
   LexRank
-  `Sumtract: Second project for UW LING
   572 <https://github.com/stefanbehr/sumtract>`__ - Python
-  `TextTeaser <https://github.com/MojoJolo/textteaser>`__ - Scala
-  `PyTeaser <https://github.com/xiaoxu193/PyTeaser>`__ - TextTeaser
   port in Python
-  `Automatic Document
   Summarizer <https://github.com/himanshujindal/Automatic-Text-Summarizer>`__
   - Java, Bipartite HITS (no sources)
-  `Pythia <https://github.com/giorgosera/pythia/blob/dev/analysis/summarization/summarization.py>`__
   - Python, LexRank & Centroid
-  `SWING <https://github.com/WING-NUS/SWING>`__ - Ruby
-  `Topic Networks <https://github.com/bobflagg/Topic-Networks>`__ - R,
   topic models & bipartite graphs
-  `Almus: Automatic Text
   Summarizer <http://textmining.zcu.cz/?lang=en&section=download>`__ -
   Java, LSA (without source code)
-  `Musutelsa <http://www.musutelsa.jamstudio.eu/>`__ - Java, LSA
   (always freezes)
-  http://mff.bajecni.cz/index.php - C++
-  `MEAD <http://www.summarization.com/mead/>`__ - Perl, various methods
   + evaluation framework

Installation
------------

Make sure you have `Python <http://www.python.org/>`__ 2.7/3.3+ and
`pip <https://crate.io/packages/pip/>`__
(`Windows <http://docs.python-guide.org/en/latest/starting/install/win/>`__,
`Linux <http://docs.python-guide.org/en/latest/starting/install/linux/>`__)
installed. Run simply (preferred way):

.. code:: sh

    $ [sudo] pip install sumy

Or for the fresh version:

.. code:: sh

    $ [sudo] pip install git+git://github.com/miso-belica/sumy.git

Usage
-----

Sumy contains command line utility for quick summarization of documents.

.. code:: sh

    $ sumy lex-rank --length=10 --url=http://en.wikipedia.org/wiki/Automatic_summarization # what's summarization?
    $ sumy luhn --language=czech --url=http://www.zdrojak.cz/clanky/automaticke-zabezpeceni/
    $ sumy edmundson --language=czech --length=3% --url=http://cs.wikipedia.org/wiki/Bitva_u_Lipan
    $ sumy --help # for more info

Various evaluation methods for some summarization method can be executed
by commands below:

.. code:: sh

    $ sumy_eval lex-rank reference_summary.txt --url=http://en.wikipedia.org/wiki/Automatic_summarization
    $ sumy_eval lsa reference_summary.txt --language=czech --url=http://www.zdrojak.cz/clanky/automaticke-zabezpeceni/
    $ sumy_eval edmundson reference_summary.txt --language=czech --url=http://cs.wikipedia.org/wiki/Bitva_u_Lipan
    $ sumy_eval --help # for more info

Python API
----------

Or you can use sumy like a library in your project.

.. code:: python

    # -*- coding: utf-8 -*-

    from __future__ import absolute_import
    from __future__ import division, print_function, unicode_literals

    from sumy.parsers.html import HtmlParser
    from sumy.parsers.plaintext import PlaintextParser
    from sumy.nlp.tokenizers import Tokenizer
    from sumy.summarizers.lsa import LsaSummarizer as Summarizer
    from sumy.nlp.stemmers import Stemmer
    from sumy.utils import get_stop_words


    LANGUAGE = "czech"
    SENTENCES_COUNT = 10


    if __name__ == "__main__":
        url = "http://www.zsstritezuct.estranky.cz/clanky/predmety/cteni/jak-naucit-dite-spravne-cist.html"
        parser = HtmlParser.from_url(url, Tokenizer(LANGUAGE))
        # or for plain text files
        # parser = PlaintextParser.from_file("document.txt", Tokenizer(LANGUAGE))
        stemmer = Stemmer(LANGUAGE)

        summarizer = Summarizer(stemmer)
        summarizer.stop_words = get_stop_words(LANGUAGE)

        for sentence in summarizer(parser.document, SENTENCES_COUNT):
            print(sentence)

Tests
-----

Setup:

.. code:: sh

    $ pip install pytest pytest-cov

Run tests via

.. code:: sh

    $ py.test-2.7 && py.test-3.3 && py.test-3.4 && py.test-3.5

.. |image| image:: https://api.travis-ci.org/miso-belica/sumy.png?branch=master
   :target: https://travis-ci.org/miso-belica/sumy
