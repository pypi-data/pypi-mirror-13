.. :changelog:

=======
History
=======

Pending Release
---------------

* New release notes here

1.3.1 (2016-02-25)
------------------

* Theme updated a bit more to make buttons look nice

1.3.0 (2016-02-24)
------------------

* New Logo and theme, thanks @emache.
* The login logic no longer sends users without permission to see Nexus through a redirect loop, thanks @ChunYin for
  the report.

1.2.0 (2016-02-12)
------------------

* Removed support for Django 1.7
* Removed the need to add a call to ``nexus.autodiscover()`` in your URLConf by using the ``AppConfig``, similar to
  Django Admin from Django 1.7+
* Upgraded jQuery to 1.6.4
* Upgraded Facebox to its master version

1.1.0 (2016-01-13)
------------------

* Removed support for old Django versions
* Fixed all deprecation warnings on Django 1.7 and 1.8
* Added Django 1.9 support
* Added Python 3.4 and 3.5 support
* Historically Nexus had a module that embedded Django Admin; this has not worked since Django 1.3 due to removal of
  the ``adminmedia`` template tag that the templates were still using. Because it seems that no one has been using it,
  it has been removed. Users are encourage to just use the normal Django Admin instead. Nexus thus ships with no
  modules included.
* Removed the login/logout pages, which were copied and adapted from an old version of Django Admin, and likely no
  longer secure. If you are not logged in Nexus will now redirect you to Django Admin - thus Django Admin is now
  required by Nexus.
* Fixed Nexus CSRF protection to work if you have changed the CSRF cookie name,
  thanks to a PR on the original Nexus from Github users @karech and
  @graingert.
* Removed all inline javascript, thanks @graingert.

1.0.0 (2015-12-09)
------------------

* First publication on PyPI as ``nexus-yplan``
* Django 1.8 compatibility

0.3.1 (2015-01-22)
------------------

* Better support for Django 1.7 and Python 3

0.2.3 (2011-12-19)
------------------

* Ensure on exempt views we still send .
* Downgrade CSRF ajax to work with older versions of jQuery.

0.2.2 (2011-12-19)
------------------

* Update AJAX CSRF set to work against correct origins.

0.2.1 (2011-12-19)
------------------

* Added version to Nexus footer.
