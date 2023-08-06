jsonrpcserver
*************

Process incoming `JSON-RPC <http://www.jsonrpc.org/>`__ requests in Python 2.7
and 3.3+.

.. sourcecode:: python

    >>> dispatch([cat, dog], {'jsonrpc': '2.0', 'method': 'cat', 'id': 1})
    'meow'

Full documentation is available at `readthedocs
<https://jsonrpcserver.readthedocs.org/>`__.
