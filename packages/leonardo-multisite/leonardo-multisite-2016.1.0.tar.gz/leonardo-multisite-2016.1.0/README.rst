
==================
Leonardo Multisite
==================

Full support for multisite with security. Uses reuqest processing for filtering page and ``django-allowedsites`` for ALLOWED_HOSTS based on the domains in django.contrib.sites.

.. contents::
    :local:

Installation
------------

.. code-block:: bash

    pip install leonardo-multisite

And enable it in the admin or add ``MULTI_SITE_ENABLED`` to your settings.

or as leonardo bundle

.. code-block:: bash

    pip install django-leonardo[multisite]

For FeinCMS users
-----------------

settings.py::

    MULTI_SITE_ENABLED = True

    MIDDLEWARES += ('leonardo_multisite.middleware.MultiSiteMiddleware',)

    from allowedsites import CachedAllowedSites

    ALLOWED_HOSTS = CachedAllowedSites()

Read More
---------

* https://github.com/django-leonardo/django-leonardo
* https://github.com/feincms/feincms
* https://github.com/kezabelle/django-allowedsites
