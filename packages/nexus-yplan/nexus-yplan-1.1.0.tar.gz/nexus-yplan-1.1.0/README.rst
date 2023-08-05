=====
Nexus
=====

.. image:: https://img.shields.io/pypi/v/nexus-yplan.svg
    :target: https://pypi.python.org/pypi/nexus-yplan

.. image:: https://travis-ci.org/YPlan/nexus.svg?branch=master
        :target: https://travis-ci.org/YPlan/nexus

Nexus is a pluggable admin application in Django. It's designed to give you a simple design and architecture for
building admin applications.

It was originally created by `Disqus <https://github.com/disqus/nexus>`_, but due to the inactivity we at YPlan have taken over maintenance on this fork.

Screenshot
----------

.. image:: https://raw.github.com/YPlan/nexus/master/screenshot.png

Requirements
------------

Tested with all combinations of:

* Python: 2.7, 3.4, 3.5
* Django: 1.7 (up to Python 3.4 only), 1.8, 1.9

Install
-------

Install it with pip (or easy_install):

.. code-block:: bash

	pip install nexus-yplan

Make sure you ``pip uninstall nexus`` first if you're upgrading from the original to this fork - the packages clash.

Config
------

You'll need to enable it much like you would ``django.contrib.admin``.

First, add it to your ``INSTALLED_APPS`` setting:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'nexus',
    )

Now you'll want to include it within your ``urls.py``:

.. code-block:: python

	import nexus

	# sets up the default nexus site by detecting all nexus_modules.py files
	nexus.autodiscover()

	# urls.py
	urlpatterns = patterns('',
	    ('^nexus/', include(nexus.site.urls)),
	)

By default Nexus requires ``django.contrib.auth`` and ``django.contrib.sessions``. If you are using a custom auth
system you can skip these requirements by using the setting ``NEXUS_SKIP_INSTALLED_APPS_REQUIREMENTS = True`` in your
django settings.

Settings
--------

Nexus' behaviour can be customized by adding some values to your Django settings.

Login
~~~~~

Until Version 1.1, Nexus included a login/logout functionality. Unfortunately these were copied and adapted from an old
version of the code in Django Admin, and were thus not up to date with security changes in newer Django versions. Since
keeping them up to date would be a burden, and most sites use Django Admin for adminstrator login, the login/logout
functions have been removed.

Nexus now relies on Django Admin login, or for users to visit it having logged in through another route.

Media
~~~~~

By default Nexus serves its media files itself through Python, avoiding any configuration to integrate with your
project. This is convenient but can be slow. You can control where the media files are served from with the setting
``NEXUS_MEDIA_PREFIX``, for example:

.. code-block:: python

    NEXUS_MEDIA_PREFIX = '/served/here/'

Modules
-------

Applications which provide Nexus modules:

* `Gargoyle (YPlan fork) <https://github.com/YPlan/gargoyle>`_
* `Memcache <https://github.com/dcramer/nexus-memcache>`_
* `Redis <https://github.com/dcramer/nexus-redis>`_
* `django-debug-logging <https://github.com/lincolnloop/django-debug-logging>`_
* `Django-Experiments <https://github.com/mixcloud/django-experiments>`_

N.B. Those that have not been forked by YPlan probably aren't up to date to work with newer Django versions.

If you want to write a module, see ``HelloWorldModule`` in ``tests/testapp/nexus_modules.py``, plus its templates, for
a simple hello world implementation. Also the source code shouldn't be too hard to understand.
