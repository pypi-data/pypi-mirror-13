django-shell+
=================

A management command to start a shell, and auto-import all models, and the datetime module.

Usage::

    $ django-admin.py shell+


or::

    $ ./manage.py shell+

Also included: a command to update permissions.

    $ django-admin.py update_permissions

Installation::

    $ pip install django-shell-plus

And then add `shell_plus` to your `settings.INSTALLED_APPS`.

Changelog
---------

1.1.7
~~~~~
Make update_permissions use new app-loading API.

1.1.6
~~~~

Use the new (!) app-loading from django. Remove code that uses deprecated APIs.

1.1.5
~~~~~

Import `cache` from `django.core.cache`, and `reverse`,`resolve` from `django.core.urlresolvers`, because I often fire up a shell, just to do this to check something.
