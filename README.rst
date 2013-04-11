=========================
Automatic text summarizer
=========================
.. image:: https://api.travis-ci.org/miso-belica/sumy.png?branch=master
   :target: https://travis-ci.org/miso-belica/sumy

Here are some other summarizers:

- https://github.com/thavelick/summarize/ - Python, TF (very simple)
- `Open Text Summarizer <http://libots.sourceforge.net/>`_ - C, TF*IDF
- `Almus: Automatic Text Summarizer <http://textmining.zcu.cz/?lang=en&section=download>`_ - Java, LSA (without source code)
- `Musutelsa <http://www.musutelsa.jamstudio.eu/>`_ - Java, LSA (always freezes)
- http://mff.bajecni.cz/index.php - C++
- `MEAD <http://www.summarization.com/mead/>`_ - Perl, various methods + evaluation framework


Installation
------------
Currently only from git repo

.. code-block:: bash

    $ [sudo] pip install git+git://github.com/miso-belica/sumy.git


Usage
-----
Sumy contains command line utility for quick summarization of documents.

.. code-block:: bash

    $ sumy luhn --url=http://www.zdrojak.cz/clanky/automaticke-zabezpeceni/
    $ sumy edmundson --length=3% --url=http://cs.wikipedia.org/wiki/Bitva_u_Lipan
    $ sumy --help # for more info


Tests
-----
Run tests via

.. code-block:: bash

    $ nosetests --with-coverage --cover-package=sumy --cover-erase tests
    $ nosetests-3.3 --with-coverage --cover-package=sumy --cover-erase tests
