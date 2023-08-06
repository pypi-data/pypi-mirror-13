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
* Django: 1.8, 1.9

Installation
------------

Install it with **pip**:

.. code-block:: bash

    pip install nexus-yplan

Make sure you ``pip uninstall nexus`` first if you're upgrading from the original to this fork - the packages clash.

You'll need to enable it much like you would ``django.contrib.admin``.

First, add it to your ``INSTALLED_APPS`` setting:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'nexus',
    )

``nexus`` has three dependencies from core Django - ``django.contrib.admin``, ``django.contrib.auth``, and
``django.contrib.sessions``. If these applications are not in your ``INSTALLED_APPS``, add them; or if you are using a
custom auth system you can skip these requirements by adding the line ``NEXUS_SKIP_INSTALLED_APPS_REQUIREMENTS = True``
to your settings.

Second, include nexus at some url in your ``urls.py``:

.. code-block:: python

    import nexus

    # urls.py
    urlpatterns = patterns('',
        ('^nexus/', include(nexus.site.urls)),
    )

Nexus has autodiscovery similar to Django Admin - it will look in each of your ``INSTALLED_APPS`` for a
``nexus_modules`` submodule, and import that. This is where the app should declare a ``NexusModule`` subclass and use
``nexus.site.register`` to add it to the main Nexus site. Thus to add functionality you should install some packages
with modules, or write your own.


Available Modules
-----------------

The following modules are tested against ``nexus-yplan``:

* `Gargoyle (YPlan fork) <https://github.com/YPlan/gargoyle>`_

There are also some older applications that provide Nexus modules, however these were only developed against Disqus'
Nexus and not this fork; your mileage may vary:

* `nexus-memcache <https://github.com/dcramer/nexus-memcache>`_
* `nexus-redis <https://github.com/dcramer/nexus-redis>`_

If you want to write a module, there are a couple of example modules in ``tests/testapp/nexus_modules.py``, with
templates in ``tests/testapp/templates/nexus/example``. Also the source code shouldn't be too hard to understand.


A Note on Login
---------------

Until Version 1.1, Nexus included a login/logout functionality. Unfortunately these were copied and adapted from an old
version of the code in Django Admin, and were thus not up to date with security changes in newer Django versions. Since
keeping them up to date would be a burden, and most sites use Django Admin for adminstrator login, the login/logout
functions have been removed.

Nexus now relies on Django Admin login, or for users to visit it having logged in through another route.


Settings
--------

Nexus' behaviour can be customized by adding some values to your Django settings.

Media
~~~~~

By default Nexus serves its media files itself through Python, avoiding any configuration to integrate with your
project. This is convenient but can be slow. You can control where the media files are served from with the setting
``NEXUS_MEDIA_PREFIX``, for example:

.. code-block:: python

    NEXUS_MEDIA_PREFIX = '/served/here/'

This will make Nexus write its media URLs using this prefix, where it assumes you have set up serving its files.
