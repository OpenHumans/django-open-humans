############
Introduction
############

This application implements a *OAuth2* login flow that creates regular *Django* ``User`` objects with an
associated ``OpenHumansMember`` object to interface with `Open Humans <https://www.openhumans.org/>`_.
It furthermore offers a variety of methods to interact with those members and their data.

This project is it's own small *Django* application that you can re-use in your own larger *Django* project.
Under the hood it is using the Python library `open-humans-api <https://github.com/openhumans/open-humans-api>`_
to interface with the APIs of *Open Humans*.


Features
========

* Allow users to login your app with an Open Humans account
* Handles all of the *OAuth2* workflow for you
* Manage your project's files on Open Humans

  * Upload files
  * Delete files
  * Access existing files

* Message users
* Provide a hook to automatically delete data from members that de-authorize you on Open Humans

Example use cases
=================

This library has been used in a variety of projects that interface with Open Humans. Here are some examples:

* `Personal API <https://tzovar.as/a-personal-api/>`_
* `Fitbit Intraday Access <https://github.com/openhumans/oh-fitbit-intraday>`_
* `Google Fit Integration <https://github.com/carolinux/oh-googlefit>`_


Getting in touch
================

Our `code is on GitHub <https://github.com/OpenHumans/django-open-humans>`_ and we are always
happy about code & documentation contributions as well as bug reports! To get in touch more directly
you can `join us on Slack <http://slackin.openhumans.org>`_!
