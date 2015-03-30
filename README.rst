.. _Python: http://www.python.org/

=========================
Automatic text summarizer
=========================
.. image:: https://api.travis-ci.org/miso-belica/sumy.png?branch=master
   :target: https://travis-ci.org/miso-belica/sumy

Simple library and command line utility for extracting summary from HTML pages or plain texts. The package also contains simple evaluation framework for text summaries. Implemented summarization methods:

- **Luhn** - heurestic method, `reference <http://ieeexplore.ieee.org/xpl/articleDetails.jsp?arnumber=5392672>`_
- **Edmundson** heurestic method with previous statistic research, `reference <http://dl.acm.org/citation.cfm?doid=321510.321519>`_
- **Latent Semantic Analysis, LSA** - one of the algorithm from http://scholar.google.com/citations?user=0fTuW_YAAAAJ&hl=en I think the author is using more advanced algorithms now. `Steinberger, J. a Ježek, K. Using latent semantic an and summary evaluation. In In Proceedings ISIM '04. 2004. S. 93-100. <http://www.kiv.zcu.cz/~jstein/publikace/isim2004.pdf>`_
- **LexRank** and **TextRank** - these two are some sort of combination of a few resources that I found on the internet. I really don't remember the sources. Probably `Wikipedia <https://en.wikipedia.org/wiki/Automatic_summarization#Unsupervised_approaches:_TextRank_and_LexRank>`_ and some papers in 1st page of Google :)

Here are some other summarizers:

- https://github.com/thavelick/summarize/ - Python, TF (very simple)
- `Reduction <https://github.com/adamfabish/Reduction>`_ - Python, TextRank (simple)
- `Open Text Summarizer <http://libots.sourceforge.net/>`_ - C, TF without normalization
- `Simple program that summarize text <https://github.com/xhresko/text-summarizer>`_ - Python, TF without normalization
- `Intro to Computational Linguistics <https://github.com/kylehardgrave/summarizer>`_ - Java, LexRank

- `Sumtract: Second project for UW LING 572 <https://github.com/stefanbehr/sumtract>`_ - Python
- `TextTeaser <https://github.com/MojoJolo/textteaser>`_ - Scala
-  `PyTeaser <https://github.com/xiaoxu193/PyTeaser>`_ - TextTeaser port in Python
- `Automatic Document Summarizer <https://github.com/himanshujindal/Automatic-Text-Summarizer>`_ - Java, Bipartite HITS (no sources)
- `Pythia <https://github.com/giorgosera/pythia/blob/dev/analysis/summarization/summarization.py>`_ - Python, LexRank & Centroid
- `SWING <https://github.com/WING-NUS/SWING>`_ - Ruby
- `Topic Networks <https://github.com/bobflagg/Topic-Networks>`_ - R, topic models & bipartite graphs
- `Almus: Automatic Text Summarizer <http://textmining.zcu.cz/?lang=en&section=download>`_ - Java, LSA (without source code)
- `Musutelsa <http://www.musutelsa.jamstudio.eu/>`_ - Java, LSA (always freezes)
- http://mff.bajecni.cz/index.php - C++
- `MEAD <http://www.summarization.com/mead/>`_ - Perl, various methods + evaluation framework


Installation
------------
Make sure you have Python_ 2.6+/3.2+ and `pip <https://crate.io/packages/pip/>`_
(`Windows <http://docs.python-guide.org/en/latest/starting/install/win/>`_,
`Linux <http://docs.python-guide.org/en/latest/starting/install/linux/>`_) installed.
Run simply (preferred way):

.. code-block:: bash

    $ [sudo] pip install sumy


Or for the fresh version:

.. code-block:: bash

    $ [sudo] pip install git+git://github.com/miso-belica/sumy.git


Or if you have to:

.. code-block:: bash

    $ wget https://github.com/miso-belica/sumy/archive/master.zip # download the sources
    $ unzip master.zip # extract the downloaded file
    $ cd sumy-master/
    $ [sudo] python setup.py install # install the package


Usage
-----
Sumy contains command line utility for quick summarization of documents.

.. code-block:: bash

    $ sumy lex-rank --length=10 --url=http://en.wikipedia.org/wiki/Automatic_summarization # what's summarization?
    $ sumy luhn --language=czech --url=http://www.zdrojak.cz/clanky/automaticke-zabezpeceni/
    $ sumy edmundson --language=czech --length=3% --url=http://cs.wikipedia.org/wiki/Bitva_u_Lipan
    $ sumy --help # for more info

Various evaluation methods for some summarization method can be executed by
commands below:

.. code-block:: bash

    $ sumy_eval lex-rank reference_summary.txt --url=http://en.wikipedia.org/wiki/Automatic_summarization
    $ sumy_eval lsa reference_summary.txt --language=czech --url=http://www.zdrojak.cz/clanky/automaticke-zabezpeceni/
    $ sumy_eval edmundson reference_summary.txt --language=czech --url=http://cs.wikipedia.org/wiki/Bitva_u_Lipan
    $ sumy_eval --help # for more info


Python API
----------
Or you can use sumy like a library in your project.

.. code-block:: python

    # -*- coding: utf8 -*-

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
Run tests via

.. code-block:: bash

    $ nosetests-2.6 && nosetests-3.2 && nosetests-2.7 && nosetests-3.3
