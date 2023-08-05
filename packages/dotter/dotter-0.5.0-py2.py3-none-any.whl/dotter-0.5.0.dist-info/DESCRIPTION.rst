dotter
======

.. image:: https://travis-ci.org/paetzke/dotter.png?branch=master
  :target: https://travis-ci.org/paetzke/dotter
.. image:: https://coveralls.io/repos/paetzke/dotter/badge.svg?branch=master&service=github
  :target: https://coveralls.io/r/paetzke/dotter?branch=master
.. image:: https://badge.fury.io/py/dotter.svg
  :target: https://pypi.python.org/pypi/dotter/

Dotter is a graphviz wrapper for Python 2 and 3. In order to use it you need graphviz.
On Debian/Ubuntu you can install it by typing:

.. code:: bash

    $ apt-get install graphviz

After that install ``dotter`` via ``pip``.

.. code:: bash

    $ pip install dotter

.. image:: https://raw.githubusercontent.com/paetzke/dotter/master/docs/dotter.png

An usage example:

.. code:: python

    from dotter import Dotter


    dotter = Dotter()

    dotter.add_node('a', label='b')
    dotter.add_node('b', label='c')
    dotter.add_edge('a', 'b')
    dotter.close()

Bugs and improvements
---------------------

Feel free to open tickets or send pull requests with improvements.
These `contributors <https://github.com/paetzke/dotter/graphs/contributors>`_ have done so.

Copyright
---------

Copyright (c) 2013-2015 Friedrich Pätzke.
See `LICENSE <LICENSE>`_ for further details.

See you. `Friedrich <https://twitter.com/paetzke>`_.


