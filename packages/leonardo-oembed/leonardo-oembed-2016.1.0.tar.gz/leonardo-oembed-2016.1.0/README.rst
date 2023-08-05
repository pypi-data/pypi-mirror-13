
===============
Leonardo Oembed
===============

Leonardo wrapper for feincms-oembed converts standard URLs from more than 200 content providers into embedded videos, images and rich article previews by letting Embedly or another OEmbed provider to the hard work.

Thanks @matthiask

.. contents::
    :local:

Installation
============

.. code-block:: bash

    pip install leonardo-oembed

or as leonardo bundle

.. code-block:: bash

    pip install django-leonardo["oembed"]

Configuration
=============

Add ``leonardo_module_oembed`` to APPS list, in the ``local_settings.py``::

    APPS = [
        ...
        'leonardo_oembed'
        ...
    ]

Sync static
-----------

.. code-block:: bash

    python manage.py makemigrations --noinput
    python manage.py migrate --noinput
    python manage.py sync_all

Extends
=======

If you want to customize the Embedly_ request or use another OEmbed provider,
set ``settings.OEMBED_PROVIDER`` to a function receiving the URL and a dict
with additional arguments and returning a suitable URL which returns OEmbed
JSON on access. ``OEMBED_PROVIDER`` must either be a dotted python path or a
callable::

    from feincms_oembed.providers import embedly_oembed_provider
    def my_provider(url, kwargs):
        kwargs['wmode'] = 'opaque'
        return embedly_oembed_provider(url, kwargs)

    OEMBED_PROVIDER = 'path.to.module.my_provider'
    # OEMBED_PROVIDER = my_provider # The function can be used too, not only
                                    # the dotted python path.


Read More
=========

* https://github.com/feincms/feincms-oembed
* https://github.com/django-leonardo/django-leonardo


