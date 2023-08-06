
Muffin-DogpileCache
#################

.. _description:

Muffin-DogpileCache -- A simple DogpileCache helper plugin for muffin_ framework.

.. _requirements:

Requirements
=============

- python >= 3.4
- muffin >= 0.5.5

.. _installation:

Installation
=============

**Muffin-DogpileCache** should be installed using pip: ::

    pip install muffin-dogpilecache

.. _usage:

Usage
=====

Add *muffin-dogpilecache* to muffin plugin list:

.. code-block:: python

    import muffin


    app = muffin.Application(
        'example',

        PLUGINS=(
            'muffin_dogpilecache',
        )
    )

Add your *configurations* for ``dogpile.cache``:

.. code-block:: python

    DOGPILECACHE_CONFIGS = {
        'cache.local.backend': 'dogpile.cache.dbm',
        'cache.local.arguments.filename': './dbmfile.dbm',
        'cache.redis.backend': 'dogpile.cache.redis',
        'cache.redis.arguments.host': 'localhost',
        'cache.redis.arguments.port': 6379,
    }

Associate each configuration with a ``dogpile.cache`` *region*:

.. code-block:: python

    DOGPILECACHE_REGIONS = {
        'default': 'cache.local.',
        'redis': 'cache.redis.',
    }

Decorate your functions:

.. code-block:: python

    @app.ps.dogpilecache.default.cache_on_arguments()
    def my_local_cached_function():
        ...

    @app.ps.dogpilecache.redis.cache_on_arguments()
    def my_redis_cached_function():
        ...

.. _options:

Options
-------

========================== ==============================================================
 *DOGPILECACHE_CONFIGS*    Configurations for regions
========================== ==============================================================
 *DOGPILECACHE_REGIONS*    Regions related with the configurations prefix
========================== ==============================================================
 *DOGPILECACHE_TEST*       If true, set regions with ``dogpile.cache.null``
========================== ==============================================================

License
=======

Licensed under a `MIT license`_.

.. _links:


.. _muffin: https://github.com/klen/muffin
.. _abnerpc: https://github.com/abnerpc
.. _MIT license: http://opensource.org/licenses/MIT
