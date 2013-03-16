============================
Automatic text summarization
============================
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
::

    pip install git+git://github.com/miso-belica/sumy.git


Tests
-----
Run tests via

.. code-block:: bash

    $ nosetests --with-coverage --cover-package=sumy --cover-erase tests
    $ nosetests-3.3 --with-coverage --cover-package=sumy --cover-erase tests
