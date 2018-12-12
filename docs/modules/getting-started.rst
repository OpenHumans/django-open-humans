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


Setting up ``django-open-humans``
=================================

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
