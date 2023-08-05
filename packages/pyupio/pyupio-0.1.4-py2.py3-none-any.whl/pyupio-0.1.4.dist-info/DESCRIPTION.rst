===============================
pyup
===============================

.. image:: https://img.shields.io/pypi/v/pyupio.svg
        :target: https://pypi.python.org/pypi/pyupio

.. image:: https://img.shields.io/travis/pyupio/pyup.svg
        :target: https://travis-ci.org/pyupio/pyup

.. image:: https://readthedocs.org/projects/pyup/badge/?version=latest
        :target: https://readthedocs.org/projects/pyup/?badge=latest
        :alt: Documentation Status


.. image:: https://codecov.io/github/pyupio/pyup/coverage.svg?branch=master
        :target: https://codecov.io/github/pyupio/pyup?branch=master


A tool to update all your projects requirements


Quickstart
----------

To install pyup, run::

    $ pip install pyupio
    $ pip install -e git+https://github.com/jayfk/PyGithub.git@top#egg=PyGithub




History
-------

0.1.4 (2015-12-30)
---------------------

* Fixed a bug with the github provider when committing too fast.
* Requirement content replace function had a bug where not always the right requirement 
was replaced

0.1.3 (2015-12-27)
---------------------

* PyGithub should be installed as a specific dependency to keep things sane and simple until the
changes on upstream are merged.

0.1.2 (2015-12-27)
---------------------

* Use development version of pygithub.

0.1.1 (2015-12-27)
---------------------

* Fixed minor packing issue.

0.1 (2015-12-27)
---------------------

* (silent) release on PyPI.


