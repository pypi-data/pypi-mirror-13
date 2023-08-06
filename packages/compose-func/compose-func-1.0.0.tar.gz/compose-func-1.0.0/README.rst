===============================================
Compose: No frills Python function composition.
===============================================


  *Important*
  If you prefer to write Python code in a more functional style you may find the
  toolz_ package to be more useful, it includes a `compose` function as well as
  several functions conducive to writing functional code in Python.

.. _toolz: https://pypi.python.org/pypi/toolz

No magic operators or special objects just a function with unit tests. Here is a
wonderfully contrived example to whet your appetite:

.. code-block:: pycon

   >>> import json
   >>> from compose import compose
   >>> from operator import itemgetter
   >>> compose((3).__mul__, next, iter, itemgetter('b'), json.loads)('{"a": 1, "b": [2, 3]}')
   6


Contribute
==========

See http://github.com/jonathanj/compose for development.


Installation
============

.. code-block:: console

    $ pip install compose
