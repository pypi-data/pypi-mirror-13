************
Know It's Ok
************

The purpose of Know It's Ok is to make it as easy as possible to run your tests 
while you're debugging your code.  In particular, it's main features are:

1. It finds your tests from anywhere in your repository.
2. It runs your tests with arguments tailored towards debugging.
3. It only requires typing two letters: ``ok``

Installation
============
Know It's Ok is available from PyPI::

   $ pip install know_its_ok

It's only dependencies are pytest and pytest-cov, which should both be 
installed automatically.

Usage
=====
You can run Know It's Ok from anywhere in your package's repository::

   $ ok

You can also specify individual tests to run (by default they will all be run).  
You don't need to specify the complete name of a test, any substring of a test 
will be understood.  For example, if you have a test called ``test_foo.py``, 
you can use this command to run it::

   $ ok foo

You can also specify arguments that should be passed through to ``pytest`` 
(this won't work if the argument to ``pytest`` also matches the name of one of 
your tests, but in practice this is never a problem)::

   $ ok --pdb

In order to discover your tests simply, Know It's Ok is very opinionated about 
the organization of your code.  In particular:

1. Your code must be version controlled using ``git``.
2. Your tests must be stored in a directory called ``tests/``, which itself 
   must be located in the top level of your repository.
3. Inside the ``tests/`` directory, your tests must match the pattern: 
   ``??_test_*.py``.
4. Your tests must be written using the ``pytest`` framework.
5. Your package must be located in a directory containing and ``__init__.py`` 
   file.

If any of these expectations are not met, the code should raise an exception.
