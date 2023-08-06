urly: nice URLs for python
==========================

Sometimes it feels like working with URLs is harder than it should be. Urly is a little wrapper around the werkzeug URL class to make things easy and pleasant. One module to pip install, one import, and then everything is easy. For instance:

.. code-block:: python

    >>> from urly import URL
    >>> url = URL('http://example.com/old/path?a=b')
    >>> url.path = '/new/path'
    >>> url.add_param('a', 'c')
    >>> print(url)
    http://example.com/new/path?a=b&a=c
    >>> print(url.relative_url)
    /new/path?a=b&a=c

Common tasks like changing a path, adding a parameter, and getting the relative URL, are all simple.

Urly also lets you parse URLs the way a browser would. For instance:

.. code-block:: python

    >>> url = URL('example.com', parse_like_browser=True)
    >>> print(url)
    http://example.com

Documentation
-------------

Full documentation is at `https://urly.readthedocs.org <https://urly.readthedocs.org>`_.


Install
-------

Simply install with `pip <https://pip.pypa.io>`_::

    $ pip install urly
