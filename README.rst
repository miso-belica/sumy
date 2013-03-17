============================
Automatic text summarization
============================
.. image:: https://api.travis-ci.org/miso-belica/sumy.png?branch=master
   :target: https://travis-ci.org/miso-belica/sumy

Here are some other summarizators:

- https://github.com/thavelick/summarize/ (very simple)
- http://pypi.python.org/pypi/ots
- http://libots.sourceforge.net/
- http://textmining.zcu.cz/?lang=en&section=download
- http://www.musutelsa.jamstudio.eu/
- http://mff.bajecni.cz/index.php
- http://www.summarization.com/mead/


Installation
------------
Currently only from git repo

.. code-block:: bash

    $ [sudo] pip install git+git://github.com/miso-belica/sumy.git


Tests
-----
Run tests via

.. code-block:: bash

    $ nosetests --with-coverage --cover-package=sumy --cover-erase tests
    $ nosetests-3.3 --with-coverage --cover-package=sumy --cover-erase tests
