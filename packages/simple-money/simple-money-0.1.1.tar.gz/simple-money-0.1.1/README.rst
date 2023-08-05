Simple Money
============

|Build Status| |codecov.io|

.. |Build Status| image:: https://travis-ci.org/Stranger6667/simple-money.png?branch=master
   :target: https://travis-ci.org/Stranger6667/simple-money
.. |codecov.io| image:: https://codecov.io/github/Stranger6667/simple-money/coverage.svg?branch=master
   :target: https://codecov.io/github/Stranger6667/simple-money?branch=master

A simple interface to work with money-related entities.

Installation
------------

The current stable release:

::

    pip install simple_money

or:

::

    easy_install simple_money

or from source:

::

    $ sudo python setup.py install

Usage
-----

Arithmetic operations:


.. code:: python

    >>> Money(100, 'EUR') + Money(50, 'EUR')
    150 EUR
    >>> Money(100, 'EUR') - Money(50, 'EUR')
    50 EUR
    >>> Money(100, 'EUR') * 2
    200 EUR


Also you can manipulate with money in different currencies:

.. code:: python

    >>> Money(100, 'EUR') + Money(50, 'USD')
    100 EUR, 50 USD
    >>> Money(100, 'EUR') - Money(50, 'USD')
    100 EUR, -50 USD
    >>> (Money(100, 'EUR') - Money(50, 'USD')) * 2
    200 EUR, -100 USD

With multiply currencies you are able to get concrete currency value in the following way:

.. code:: python

    >>> value = Money(100, 'EUR') + Money(50, 'USD')
    >>> value.EUR
    100 EUR
    >>> value.USD
    50 EUR
