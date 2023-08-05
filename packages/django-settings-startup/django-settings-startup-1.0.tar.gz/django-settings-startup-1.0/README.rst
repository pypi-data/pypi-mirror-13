Django Settings On Startup
==========================

See your chosen settings on output when django is starting with ``runserver`` command,  
an additional CLI option.


For Django 1.8.5 and python 3.4.

Usage
-----

Once installed, using this command::

    python manage.py runserver --config


Additional CLI Options
~~~~~~~~~~~~~~~~~~~~~~

--config
  Show your settings on output.

Please see ``python manage.py runserver --help`` for more information additional options.

Install
-------

1. Download package::

    pip install django-settings-startup

2. Add "settings-startup" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'django_settings_startup',
    ]

Lastest Version
---------------

0.1

Code Source
-----------

https://github.com/glegoux/django-settings-startup/

PyPI
----

https://pypi.python.org/pypi/django-settings-startup
