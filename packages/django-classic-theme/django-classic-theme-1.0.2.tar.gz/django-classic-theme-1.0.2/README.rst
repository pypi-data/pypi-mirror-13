django-classic-theme is the classic theme for the admin interface that was
included in Django until Django 1.9.

The source is taken from the Django master branch just before the new flat theme
replaced the classic theme (commit e176de25127a2750ea1c6a705b2c0983b5782b41).

This app overrides the default admin's CSS and image files.

Installation
------------

1. Install via pip: ``pip install django-classic-theme``

2. Put ``classic_theme`` app in your *INSTALLED\_APPS* **before**
   ``django.contrib.admin``:
   ::

       INSTALLED_APPS = (
           ...
           'classic_theme',
           'django.contrib.admin',
           ...
       )

3. Enjoy!

Compatibility
-------------

Works on Django 1.9.
