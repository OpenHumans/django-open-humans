###############
Getting Started
###############

This guide assumes you are using ``Django`` as your web framework, want to start a new project and are using
`pipenv <https://pipenv.readthedocs.io/en/latest/>`_ to manage your dependencies.

The guide is written to work for most UNIX systems.

Installing ``django-open-humans``
=================================

Let's start by installing ``pipenv`` if you haven't done so before:

.. code-block:: shell

  pip install pipenv

Now we can install ``Django`` along with ``django-open-humans`` in a virtual environment:

.. code-block:: shell

  mkdir our_project
  cd our_project
  pipenv install django
  pipenv install django-open-humans
  pipenv shell

This installs ``django`` and ``django-open-humans`` in our new project ``our_project``
and starts the new virtual environment. With this we start a new django project:

.. code-block:: shell

  django-admin startproject our_project .


.. _setting-up:

Setting up ``django-open-humans``
=================================

Set up ``settings.py``
----------------------

Now that we have installed everything we can get started to add ``django-open-humans`` to
the ``INSTALLED_APPS`` of our Django project:

.. code-block:: python
   :lineno-start: 33
   :caption: our_project/our_project/settings.py
   :emphasize-lines: 8

    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'openhumans'
    ]

Before we can run make and run the migrations we need to add some environment variables that
``django-open-humans`` needs to properly work. At a minimum we need to set up the ``OPENHUMANS_APP_BASE_URL``,
``OPENHUMANS_CLIENT_ID`` and ``OPENHUMANS_CLIENT_SECRET``. To do so we add a few lines to our ``settings.py``:

.. code-block:: Python
  :caption: our_project/our_project/settings.py
  :lineno-start: 13

  import os

  OPENHUMANS_APP_BASE_URL = os.getenv('OPENHUMANS_APP_BASE_URL', 'http://localhost:5000')
  OPENHUMANS_CLIENT_ID = os.getenv('OPENHUMANS_CLIENT_ID', 'your_client_id')
  OPENHUMANS_CLIENT_SECRET = os.getenv('OPENHUMANS_CLIENT_SECRET', 'your_client_secret')


This code reads the ``OPENHUMANS_APP_BASE_URL``,
``OPENHUMANS_CLIENT_ID`` and ``OPENHUMANS_CLIENT_SECRET`` from the correspondingly named environment variables
you should set using e.g. ``export OPENHUMANS_CLIENT_SECRET='my_client_secret'``.

To get your own ``client_id`` and ``client_secret`` you can
`head to Open Humans <https://www.openhumans.org/direct-sharing/projects/manage/>`_
and make your own OAuth2 data request project.


Set up ``urls.py``
------------------

To add django-open-humans URLs to your project, update your root ``urls.py`` configuration
file (i.e. the file specified by ``settings.ROOT_URLCONF``) as follows:

.. code-block:: python
   :lineno-start: 1
   :caption: our_project/our_project/urls.py
   :emphasize-lines: 9-11

   from django.contrib import admin
   from django.urls import include, path

   urlpatterns = [
       path('', include('main.urls')),
       path('admin/', admin.site.urls),
   ]

   urlpatterns += [
       path('openhumans/', include('openhumans.urls')),
   ]


Run database migrations
-----------------------

Now we can migrate our tables. Those migrations will create the ``User`` and ``OpenHumansMember`` tables for us:

.. code-block:: shell

  ./manage.py migrate

And that's all to get the basic configuration and integration into your Django project done.


Setting up your Open Humans project
===================================

For the login with *Open Humans* to work you need to correctly configure the ``REDIRECT_URL``
of the OAuth2 process on Open Humans. The URL path that ``django-open-humans`` creates for redirects is

.. code-block:: python

  /openhumans/complete

This means if you want to develop locally and
your ``OPENHUMANS_APP_BASE_URL`` is ``http://localhost:5000``, your *Redirect URL* should be
``http://localhost:5000/openhumans/complete``.

Similarly, there is a deauthorization hook that you can setup on *Open Humans* which will automatically inform you
when people have de-authorized your application. ``django-open-humans`` accepts deauthorization requests at ``/openhumans/deauth``.
