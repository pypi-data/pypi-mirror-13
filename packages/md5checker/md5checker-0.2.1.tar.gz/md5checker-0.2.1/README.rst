.. image:: https://travis-ci.org/trendsetter37/md5-checker.svg?branch=master
   :target: https://travis-ci.org/trendsetter37/md5-checker
   :width: 50%

.. image:: https://codecov.io/github/trendsetter37/md5-checker/coverage.svg?branch=master
   :target: https://codecov.io/github/trendsetter37/md5-checker?branch=master
   :width: 50%


MD5Checker
==========

This module is a simple utility to examine a file's checksum

Install
-------

One-liner
~~~~~~~~~
::

  pip install md5checker

Other ways
~~~~~~~~~~~
::

  git clone https://github.com/trendsetter37/md5-checker
  cd md5-checker

Followed by:

::

  python setup.py install

or

::

  pip install .

Testing (Development)
---------------------

Inside the root directory, run


::

  pip install -r requirements.txt
  pip install -e .
  py.test

or

::

  pip install -r requirements.txt
  pip install -e .
  python setup.py test

Usage
-----

Command Line
~~~~~~~~~~~~
::

  md5checker "Space containing directory/path-to-file.extension"

Surround path with double quotes if it contains spaces. Otherwise
quotations are unnecessary.

::

  md5checker space-containing-directory/path-to-file.extension

Options
^^^^^^^
Get version.

::

  md5checker -v
  0.2.0

List hash algorithms.

::

  md5checker -a

Use alternate hash algorithm.

::

  md5checker setup.cfg -a sha1
  bf72c7d5ca4a4b2731bde5cfcc323ce64b533865

Module
~~~~~~
::

  >>> from md5checker import make_hash
  >>> make_hash('setup.cfg')
  ad895e8b0bd7d47e2a793dca3730aead
  >>> make_hash('setup.cfg', algo='sha1')
  bf72c7d5ca4a4b2731bde5cfcc323ce64b533865

Available algorithms
~~~~~~~~~~~~~~~~~~~~
* MD5
* SHA1
* SHA224
* SHA256
* SHA384
* SHA512
