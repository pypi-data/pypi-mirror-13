Copyright (c) 2016 Gilles LEGOUX

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Description: Django Settings On Startup
        ==========================
        
        See your chosen settings on standard output when django is starting with ``runserver`` command with   
        an additional CLI option.
        
        
        For Django 1.8.5 and Python 2.7, 3.2, 3.3, 3.4.
        
        **Python package information**
        
        .. image:: https://img.shields.io/pypi/status/django-settings-startup.svg
            :target: https://pypi.python.org/pypi/django-settings-startup
            :alt: pypi-stability
        
        .. image:: https://img.shields.io/pypi/v/django-settings-startup.svg
            :target: https://pypi.python.org/pypi/django-settings-startup
            :alt: pypi-version
        
        .. image:: https://img.shields.io/pypi/pyversions/django-settings-startup.svg
            :target: https://pypi.python.org/pypi/django-settings-startup
            :alt: pypi-pythonversion
        
        .. image:: https://img.shields.io/pypi/implementation/django-settings-startup.svg
            :target: https://pypi.python.org/pypi/django-settings-startup
            :alt: pypi-implementation
        
        .. image:: https://img.shields.io/pypi/wheel/django-settings-startup.svg
            :target: https://pypi.python.org/pypi/django-settings-startup
            :alt: pypi-build
        
        **Other information**
        
        .. image:: https://travis-ci.org/glegoux/django-settings-startup.svg?branch=master
            :target: https://travis-ci.org/glegoux/django-settings-startup
            :alt: travis-status
        
        .. image:: https://img.shields.io/badge/docs-latest-brightgreen.svg
            :target: http://django-settings-startup.readthedocs.org/en/latest/
            :alt: doc
        
        .. image:: https://img.shields.io/packagist/l/doctrine/orm.svg
            :target: https://github.com/glegoux/django-settings-startup/blob/master/LICENSE
            :alt: license
        
        .. image:: https://img.shields.io/pypi/dm/django-settings-startup.svg
            :target: http://pypi-ranking.info/module/django-settings-startup
            :alt: pypi-download
        
        Usage
        -----
        
        Once installed, using this command::
        
            python manage.py runserver --config
        
        
        **Additional CLI Options**
        
        --config
          Show your settings on standard output.
        
        Please see ``python manage.py runserver --help`` for more information additional options.
        
        Install
        -------
        
        1. Download package::
        
            pip install django-settings-startup
        
        2. Add "django_settings_startup" in first rank to your INSTALLED_APPS settings like this::
        
            INSTALLED_APPS = [
                'django_settings_startup',
                ...
            ]
        
        It is important to install this app in first (before native django apps), to override the command ``runserver``.
        
        Version
        -------
        
        see `VERSION <https://github.com/glegoux/django-settings-startup/blob/master/VERSION>`_
        
        Changelog
        ---------
        
        see `CHANGELOG <https://github.com/glegoux/django-settings-startup/blob/master/CHANGELOG>`_
        
        Read The Docs : Documentation
        -----------------------------
        
        * http://django-settings-startup.readthedocs.org/en/latest/
        
        GitHub : Source Code
        --------------------
        
        * https://github.com/glegoux/django-settings-startup/
        
        PyPI : open source Python packages
        ----------------------------------
        
        * home page: https://pypi.python.org/pypi/django-settings-startup
        * ranking: http://pypi-ranking.info/module/django-settings-startup
        
        Travis CI : continous integration
        ---------------------------------
        
        * https://travis-ci.org/glegoux/django-settings-startup
        
        Coveralls : code coverage
        -------------------------
        
        * https://coveralls.io/github/glegoux/django-settings-startup
        
        Useful links
        ------------
        
        * https://github.com/django/django/blob/stable/1.8.x/django/core/management/commands/runserver.py
        * https://github.com/django/django/blob/stable/1.8.x/django/core/management/base.py
        * https://github.com/django/django/blob/stable/1.8.x/django/core/management/commands/testserver.py
        * https://docs.djangoproject.com/en/1.8/howto/custom-management-commands/
        * https://docs.djangoproject.com/en/1.8/ref/django-admin/#running-management-commands-from-your-code
        
        License
        -------
        
        see `LICENSE <https://github.com/glegoux/django-settings-startup/blob/master/LICENSE>`_
        
Keywords: django settings startup
Platform: any
Classifier: Development Status :: 5 - Production/Stable
Classifier: Environment :: Web Environment
Classifier: Framework :: Django
Classifier: Framework :: Django :: 1.8
Classifier: Intended Audience :: Developers
Classifier: License :: OSI Approved :: MIT License
Classifier: Operating System :: OS Independent
Classifier: Programming Language :: Python :: 2
Classifier: Programming Language :: Python :: 2.7
Classifier: Programming Language :: Python :: 3
Classifier: Programming Language :: Python :: 3.2
Classifier: Programming Language :: Python :: 3.3
Classifier: Programming Language :: Python :: 3.4
Classifier: Topic :: Internet :: WWW/HTTP
Classifier: Topic :: Internet :: WWW/HTTP :: Dynamic Content
