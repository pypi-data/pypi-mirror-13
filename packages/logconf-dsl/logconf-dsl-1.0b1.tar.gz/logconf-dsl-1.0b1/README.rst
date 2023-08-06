================================================================================
 logconf-dsl
================================================================================

A DSL for configuration of Python's ``logging`` module.

--------------------------------------------------------------------------------
 Installation
--------------------------------------------------------------------------------

From ``PyPI` with ``pip``:

.. code-block:: bash

    pip install logconf-dsl

directly from git, with ``pip``.

.. code-block:: bash

    pip install -e git+git@github.com:joar/logconf.git


--------------------------------------------------------------------------------
 Usage
--------------------------------------------------------------------------------


.. code-block:: python

    import logconf
    from logconf.dsl import Logger, Handler

    logconf.configure(
        handlers=Handler('default',
                         'logging.StreamHandler',
                         level='DEBUG'),
        root=Logger(level='ERROR',
                    handlers=['default']),
        loggers=[
            Logger('foo',
                   'DEBUG',
                   handlers=['default'])
        ]
    )
