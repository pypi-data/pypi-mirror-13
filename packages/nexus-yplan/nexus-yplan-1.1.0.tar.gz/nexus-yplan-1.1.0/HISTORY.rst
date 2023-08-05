.. :changelog:

=======
History
=======

Pending Release
---------------

* New release notes here

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
