.. logconf-dsl documentation master file, created by
   sphinx-quickstart on Mon Feb  8 12:09:53 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Usage
=======================================

A very basic example of what logconf-dsl looks like:

.. code:: python

    from logconf import logconf, RootLogger

    logconf(
        RootLogger(level='ERROR',
                   handlers=['console']))




.. parsed-literal::

    {'root': {'level': 'ERROR'}, 'version': 1}



And here's an example of what a real logging configuration may look
like:

.. code:: python

    import logging

    from logconf import (
        logconf,
        Logger, Loggers, RootLogger,
        Handler, Handlers,
        Formatter, Formatters
    )

    LOGCONF = logconf(
        Handlers(
            Handler(name='console',
                    klass='logging.StreamHandler',
                    formatter='verbose',
                    level=logging.DEBUG)
        ),
        RootLogger(
            level=logging.ERROR,
        ),
        Loggers(
            Logger(name='foo.bar',
                   level=logging.ERROR,
                   handlers=['console']),
            Logger(name='foo.zab',
                   level=logging.DEBUG,
                   handlers=['console'])
        ),
        Formatters(
            Formatter(name='verbose',
                      format='%(asctime)s %(levelName)s %(name)s')
        )
    )

    LOGCONF




.. parsed-literal::

    {'formatters': {'verbose': {'format': '%(asctime)s %(levelName)s %(name)s'}},
     'handlers': {'console': {'class': 'logging.StreamHandler',
       'formatter': 'verbose',
       'level': 10}},
     'loggers': {'foo.bar': {'level': 40}, 'foo.zab': {'level': 10}},
     'root': {'level': 40},
     'version': 1}



And then you would apply ``LOGCONF`` to ``logging`` with

.. code:: python

    import logging.config

    logging.config.dictConfig(LOGCONF)

You can pass the most values as positional arguments to ``Logger``,
``Handler`` and ``Formatter`` as well.

.. code:: python

    logconf(
        Handlers(
            Handler('console',
                    'logging.StreamHandler',
                    'verbose',
                    logging.DEBUG)
        ),
        RootLogger(
            logging.ERROR,
        ),
        Loggers(
            Logger('foo.bar',
                   logging.ERROR,
                   ['console']),
            Logger('foo.zab',
                   logging.DEBUG,
                   ['console'])
        ),
        Formatters(
            Formatter('verbose',
                      '%(asctime)s %(levelName)s %(name)s')
        )
    )




.. parsed-literal::

    {'formatters': {'verbose': {'format': '%(asctime)s %(levelName)s %(name)s'}},
     'handlers': {'console': {'class': 'logging.StreamHandler',
       'formatter': 'verbose',
       'level': 10}},
     'loggers': {'foo.bar': {'level': 40}, 'foo.zab': {'level': 10}},
     'root': {'level': 40},
     'version': 1}



logconf-dsl is very flexible in what it allows you to do:

.. code:: python

    # You can replace the Loggers wrapper class with the keyword 'loggers'.
    logconf(
        loggers=Logger('foo', 'DEBUG', handlers=['console'])
    )
    # The same goes for 'handlers', 'formatters' and any other dict-valued key.




.. parsed-literal::

    {'loggers': {'foo': {'level': 'DEBUG'}}, 'version': 1}



.. code:: python

    # You can use addition to combine two loggers
    logconf(
        loggers=Logger('foo', 'DEBUG', ['console']) + Logger('bar', 'INFO', ['console'])
    )




.. parsed-literal::

    {'loggers': {'bar': {'level': 'INFO'}, 'foo': {'level': 'DEBUG'}},
     'version': 1}



.. code:: python

    # You can use the 'C' method to combine two loggers
    from logconf import C
    logconf(
        loggers=C(Logger('foo', 'DEBUG', ['console']),
                  Logger('bar', 'INFO', ['console']))
    )




.. parsed-literal::

    {'loggers': {'bar': {'level': 'INFO'}, 'foo': {'level': 'DEBUG'}},
     'version': 1}
