Molo Commenting
===============

.. image:: https://travis-ci.org/praekelt/molo.commenting.svg?branch=develop
    :target: https://travis-ci.org/praekelt/molo.commenting
    :alt: Continuous Integration

.. image:: https://coveralls.io/repos/praekelt/molo.commenting/badge.png?branch=develop
    :target: https://coveralls.io/r/praekelt/molo.commenting?branch=develop
    :alt: Code Coverage

Installation::

   pip install molo.commenting


Django setup::

   INSTALLED_APPS = INSTALLED_APPS + (
      'mptt',
      'django_comments',
      'django.contrib.sites',
      'molo.commenting'
   )

   COMMENTS_APP = 'molo.commenting'
   SITE_ID = 1

In your urls.py::

   urlpatterns += patterns('',
       url(r'^commenting/', include('molo.commenting.urls')),
   )
