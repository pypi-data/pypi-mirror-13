PyUQ
========

Python client library for `UQ <https://github.com/buaazp/uq>`_ cluster.

.. image:: https://badge.fury.io/py/uq.svg
    :target: https://badge.fury.io/py/uq
.. image:: https://travis-ci.org/amyangfei/pyuq.svg?branch=master
    :target: https://travis-ci.org/amyangfei/pyuq

Installation
------------

pyuq requires a running uq server, in either standalone mode or cluster mode.
See `UQ's getting-started <https://github.com/buaazp/uq#getting-started>`_
for installation instructions.

To install pyuq, simply:

.. code-block:: bash

    $ pip install uq

or from source:

.. code-block:: bash

    python setup.py install


Getting Started
---------------

.. code-block:: pycon

    >>> import uq, datetime
    >>> cli = uq.UqClient(protocol='http', ip='127.0.0.1', port=8808)
    >>> cli.add('foo')
    (True, '')
    >>> cli.add('foo', 'x', datetime.timedelta(seconds=10))
    (True, '')
    >>> cli.push('foo', 'hello')
    (True, '')
    >>> cli.pop('foo/x')
    (True, '127.0.0.1:8808/foo/x/0', u'hello')
    >>> cli.remove('127.0.0.1:8808/foo/x/0')
    (True, '')
