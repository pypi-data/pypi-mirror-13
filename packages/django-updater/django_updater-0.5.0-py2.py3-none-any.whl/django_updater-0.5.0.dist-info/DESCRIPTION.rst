django-updater
--------------

.. image:: https://djangoupdater.com/static/images/logo.png
    :target: https://djangoupdater.com

------

.. image:: https://badge.fury.io/py/django-updater.png
    :target: https://pypi.python.org/pypi/django-updater
.. image:: https://travis-ci.org/jayfk/django-updater.svg?branch=master
    :target: https://travis-ci.org/jayfk/django-updater

Displays a warning message in the admin when the used Django version is insecure or outdated and
provides a management command (or celery task) that checks for updates periodically.

Documentation
-------------

The full documentation is at https://django-updater.readthedocs.org.

Quickstart
----------

Install django-updater::

    pip install django-updater

Then, add it to your `INSTALLED_APPS`::

    INSTALLED_APPS = (
        ...
        "updater",
    )

If you want to enable it in the admin area, make sure to put `updater` before `django.contrib.admin`::

    INSTALLED_APPS = (
        ...
        "updater",
        "django.contrib.admin",
    )


Usage
-----

If you have django-updater enabled in the admin area, it will display a info/warning message when
there are updates available automatically.

In order to check for updates in an automated fashion, django-updater has to be called periodically. There are two ways to accomplish that:

- Running a periodic `Celery` task
- Create a cronjob

Celery
------

If you are using `Celery` and have a celery beat daemon running, enable Celery support in your settings with::

     from datetime import timedelta

     CELERYBEAT_SCHEDULE = {
         'run-django-updater': {
             'task': 'updater.tasks.run_check',
             'schedule': timedelta(days=1),
         },
     }


And you are good to go!

Cronjob
-------

You can use a cronjob to check for updates once a day.

To set up a cronjob, run::

     crontab -e

And then add::

     30 2 * * * python /path/to/your/apps/manage.py check_for_updates


If you are using a virtual environment, you might need to point to the python executable your virtual environment is using::

     30 2 * * * /path/to/virtual/environment/bin/python /path/to/your/apps/manage.py check_for_updates



Screenshots
-----------
.. image:: https://djangoupdater.com/static/images/security_mail.png

------

.. image:: https://djangoupdater.com/static/images/update_mail.png




History
-------

0.3.3 (2015-10-23)
++++++++++++++++++

* Added a lot of tests
* Simplified management commands
* Some small refactorings

0.4.0 (2015-10-25)
++++++++++++++++++

* Now compatible with Django 1.4 - 1.9

0.3.2 (2015-10-13)
++++++++++++++++++

* Fixed an error with squashed migrations

0.3.1 (2015-10-13)
++++++++++++++++++

* Squashed migrations

0.3.0 (2015-09-24)
++++++++++++++++++

* Added registration view

0.2.2 (2015-09-24)
++++++++++++++++++

* Refactored models
* Added admin page
* Reworked registration process

0.2.1 (2015-09-14)
++++++++++++++++++

* Added callback token

0.2.0 (2015-09-09)
++++++++++++++++++

* Major refactoring

0.1.8 (2015-09-08)
++++++++++++++++++

* Fixed small typo

0.1.7 (2015-09-08)
++++++++++++++++++

* Added notification service
* Added inline documentation
* Small refactorings

0.1.6 (2015-09-07)
++++++++++++++++++

* Added online service registration
* Fixed minor issues

0.1.5 (2015-08-19)
++++++++++++++++++

* Fixed minor issues

0.1.4 (2015-08-19)
++++++++++++++++++

* Fixed packaging issue

0.1.3 (2015-08-19)
++++++++++++++++++

* Temporarily fixing piprot issue with pytz

0.1.2 (2015-08-19)
++++++++++++++++++

* Added package requirements

0.1.1 (2015-08-19)
++++++++++++++++++

* Switched to `pip.get_installed_distributions` to get a package list
* minor documentation tweaks

0.1.0 (2015-08-19)
++++++++++++++++++

* First release on PyPI.


