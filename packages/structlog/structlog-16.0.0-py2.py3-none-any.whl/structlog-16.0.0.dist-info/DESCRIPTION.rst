========================================
structlog: Structured Logging for Python
========================================

.. image:: https://travis-ci.org/hynek/structlog.svg?branch=master
   :target: https://travis-ci.org/hynek/structlog

.. image:: https://codecov.io/github/hynek/structlog/coverage.svg?branch=master
   :target: https://codecov.io/github/hynek/structlog?branch=master

.. image:: https://www.irccloud.com/invite-svg?channel=%23structlog&amp;hostname=irc.freenode.net&amp;port=6697&amp;ssl=1
   :target: https://www.irccloud.com/invite?channel=%23structlog&amp;hostname=irc.freenode.net&amp;port=6697&amp;ssl=1

``structlog`` makes structured logging in Python easy by *augmenting* your *existing* logger.
It allows you to split your log entries up into key/value pairs and build them incrementally without annoying boilerplate code.

.. code-block:: pycon

   >>> from structlog import get_logger
   >>> log = get_logger()
   >>> log.info("key_value_logging", out_of_the_box=True, effort=0)
   out_of_the_box=True effort=0 event='key_value_logging'
   >>> log = log.bind(user='anonymous', some_key=23)
   >>> log = log.bind(user='hynek', another_key=42)
   >>> log.info('user.logged_in', happy=True)
   some_key=23 user='hynek' another_key=42 happy=True event='user.logged_in'

.. begin

It's dual-licensed under `Apache License, version 2 <http://choosealicense.com/licenses/apache/>`_ and `MIT <http://choosealicense.com/licenses/mit/>`_, available from `PyPI <https://pypi.python.org/pypi/structlog/>`_, the source code can be found on `GitHub <https://github.com/hynek/structlog>`_, the documentation at http://www.structlog.org/.

``structlog`` targets Python 2.6, 2.7, 3.3 and newer, and PyPy.

If you need any help, visit us on ``#structlog`` on `Freenode <https://freenode.net>`_!


Release Information
===================

16.0.0 (2016-01-28)
-------------------

Changes:
^^^^^^^^

- ``structlog.processors.ExceptionPrettyPrinter`` and ``structlog.processors.format_exc_info`` now support passing of Exceptions on Python 3.
- Clean up the context when exiting ``structlog.threadlocal.tmp_bind`` in case of exceptions.
  [`64 <https://github.com/hynek/structlog/issues/64>`_]
- Be more more lenient about missing ``__name__``\ s.
  [`62 <https://github.com/hynek/structlog/pull/62>`_]
- Add ``structlog.dev.ConsoleRenderer`` that renders the event dictionary aligned and with colors.
- Use `six <https://pythonhosted.org/six/>`_ for compatibility.
- Add ``structlog.processors.UnicodeDecoder`` that will decode all byte string values in an event dictionary to Unicode.
- Add ``serializer`` parameter to ``structlog.processors.JSONRenderer`` which allows for using different (possibly faster) JSON encoders than the standard library.

`Full changelog <http://structlog.readthedocs.org/en/stable/changelog.html>`_.

Authors
=======

``structlog`` is written and maintained by `Hynek Schlawack <https://hynek.me/>`_.
It’s inspired by previous work done by `Jean-Paul Calderone <http://as.ynchrono.us/>`_ and `David Reid <https://dreid.org/>`_.

The development is kindly supported by `Variomedia AG <https://www.variomedia.de/>`_.

A full list of contributors can be found on GitHub’s `overview <https://github.com/hynek/structlog/graphs/contributors>`_.
Some of them disapprove of the addition of thread local context data. :)


