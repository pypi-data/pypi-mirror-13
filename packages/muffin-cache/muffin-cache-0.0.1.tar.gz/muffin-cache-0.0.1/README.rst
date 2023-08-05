Muffin-Cache
############

.. _description:

Muffin-Cache -- A simple cache tools for muffin_ framework.

.. _badges:

.. image:: http://img.shields.io/travis/drgarcia1986/muffin-cache.svg?style=flat-square
    :target: http://travis-ci.org/drgarcia1986/muffin-cache
    :alt: Build Status

.. image:: http://img.shields.io/coveralls/drgarcia1986/muffin-cache.svg?style=flat-square
    :target: https://coveralls.io/r/drgarcia1986/muffin-cache
    :alt: Coverals

.. _requirements:

Requirements
=============

- python >= 3.4
- muffin >= 0.5.5
- muffin-redis >= 0.3.0

.. _installation:

Installation
=============

**Muffin-Cache** should be installed using pip: ::

    pip install git+https://github.com/drgarcia1986/muffin-cache.git

.. _usage:

Usage
=====

Add Muffin-Redis_ and Muffin-Cache to muffin plugin list:

.. code-block:: python

    import muffin


    app = muffin.Application(
        'example',

        PLUGINS=(
            'muffin_redis',
            'muffin_cache',
        )
    )

And use *CacheHandler* for class based views: 

.. code-block:: python

    from muffin_cache import CacheHandler 
    
    @app.register('/cached')
    class Example(CacheHandler):

        def get(self, request):
            return 'text'
    
Or *cache_view* for functions based views:

.. code-block:: python
    
    from muffin_cache import cache_view

    @app.register('/cached')
    @cache_view
    def example(request):
        return 'text'

The cache lifetime is determined by *CACHE_LIFETIME* setting of muffin application.
(the default lifetime is 30 minutes).

.. _bugtracker:

Bug tracker
===========

If you have any suggestions, bug reports or
annoyances please report them to the issue tracker
at https://github.com/drgarcia1986/muffin-cache/issues

.. _contributing:

Contributing
============

Development of Muffin-Cache happens at: https://github.com/drgarcia1986/muffin-cache


Contributors
=============

* drgarcia1986_ (Diego Garcia)

.. _license:

License
=======

Licensed under a `MIT license`_.

.. _links:


.. _muffin: https://github.com/klen/muffin
.. _muffin-redis: https://github.com/klen/muffin-redis
.. _drgarcia1986: https://github.com/drgarcia1986
.. _MIT license: http://opensource.org/licenses/MIT

