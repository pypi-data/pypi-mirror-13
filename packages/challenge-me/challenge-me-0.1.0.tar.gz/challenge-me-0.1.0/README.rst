========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis| |appveyor| |requires|
        | |codecov|
        | |scrutinizer| |codacy| |codeclimate|
    * - package
      - |version| |downloads| |wheel| |versions| |implementations|

.. |docs| image:: https://img.shields.io/badge/docs-latest-brightgreen.svg?style=flat
    :target: https://challenge-me.readthedocs.org/en/latest/
    :alt: Documentation Status

.. |travis| image:: https://travis-ci.org/julien-hadleyjack/challenge-me.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/julien-hadleyjack/challenge-me

.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/github/julien-hadleyjack/challenge-me?branch=master&svg=true
    :alt: AppVeyor Build Status
    :target: https://ci.appveyor.com/project/julien-hadleyjack/challenge-me

.. |requires| image:: https://requires.io/github/julien-hadleyjack/challenge-me/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/julien-hadleyjack/challenge-me/requirements/?branch=master

.. |codecov| image:: https://codecov.io/github/julien-hadleyjack/challenge-me/coverage.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/julien-hadleyjack/challenge-me

.. |codacy| image:: https://img.shields.io/codacy/cfacce47c4b84eb385822e262efab73a.svg?style=flat
    :target: https://www.codacy.com/app/julien-hadleyjack/challenge-me/dashboard
    :alt: Codacy Code Quality Status

.. |codeclimate| image:: https://codeclimate.com/github/julien-hadleyjack/challenge-me/badges/gpa.svg
   :target: https://codeclimate.com/github/julien-hadleyjack/challenge-me
   :alt: CodeClimate Quality Status

.. |version| image:: https://img.shields.io/pypi/v/challenge-me.svg?style=flat
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/challenge-me

.. |downloads| image:: https://img.shields.io/pypi/dm/challenge-me.svg?style=flat
    :alt: PyPI Package monthly downloads
    :target: https://pypi.python.org/pypi/challenge-me

.. |wheel| image:: https://img.shields.io/pypi/wheel/challenge-me.svg?style=flat
    :alt: PyPI Wheel
    :target: https://pypi.python.org/pypi/challenge-me

.. |versions| image:: https://img.shields.io/pypi/pyversions/challenge-me.svg?style=flat
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/challenge-me

.. |implementations| image:: https://img.shields.io/pypi/implementation/challenge-me.svg?style=flat
    :alt: Supported implementations
    :target: https://pypi.python.org/pypi/challenge-me

.. |scrutinizer| image:: https://img.shields.io/scrutinizer/g/julien-hadleyjack/challenge-me/master.svg?style=flat
    :alt: Scrutinizer Status
    :target: https://scrutinizer-ci.com/g/julien-hadleyjack/challenge-me/


.. end-badges

A command line tool for running programming challenges. This is still an early version which can have unwanted side
effects like accidentally deleting a wrong file. Use with care.

Installation
============

::

    pip install challenge-me

Documentation
=============

https://challenge-me.readthedocs.org/en/latest/

Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox

