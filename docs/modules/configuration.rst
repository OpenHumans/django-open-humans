#####################
Configuration Details
#####################

The :ref:`setting-up` section explains a minimal configuration of
``django-open-humans``.

This page lists the existing environment variables you can use to configure
your installation.

Environment variables
=====================

``OPENHUMANS_APP_BASE_URL`` (required)
--------------------------------------

The ``OPENHUMANS_APP_BASE_URL`` describes the base URL of where your app lives.
It is needed to correctly setup the ``redirect_uri`` for the OAuth2 handshakes.

``OPENHUMANS_CLIENT_ID`` (required)
-----------------------------------

You need to set the ``OPENHUMANS_CLIENT_ID`` to the ``CLIENT_ID`` you get from
Open Humans to enable the OAuth2 flow.

``OPENHUMANS_CLIENT_SECRET`` (required)
---------------------------------------

You need to set the ``OPENHUMANS_CLIENT_SECRET`` to the ``CLIENT_SECRET``
you get from Open Humans to enable the OAuth2 flow.


``OPENHUMANS_OH_BASE_URL``
--------------------------

By setting ``OPENHUMANS_OH_BASE_URL`` you can change the base URL used for all
API calls to Open Humans. The default is ``https://www.openhumans.org`` and
there is no reason to change it, unless you run your own Open Humans fork at
a different URL.

``OPENHUMANS_LOGIN_REDIRECT_URL``
---------------------------------

Specifies where a user should be redirected to after they have logged in into
your app with their Open Humans account. By default
``OPENHUMANS_LOGIN_REDIRECT_URL`` should link to ``/``.

``OPENHUMANS_LOGOUT_REDIRECT_URL``
----------------------------------

Specifies where a user should be redirected to after they have logged out of
your app with their Open Humans account. By default
``OPENHUMANS_LOGOUT_REDIRECT_URL`` should link to ``/``.


``OPENHUMANS_DELETE_ON_ERASURE``
--------------------------------

If you have set up the deauthorization hook on Open Humans the
``OPENHUMANS_DELETE_ON_ERASURE`` will specify how an incoming request from
this hook will be processed. If set to ``True`` an ``OpenHumansMember``
object will be only deleted if the user requested to do so.

**By setting this option to** ``False`` **member objects will not be deleted, even
if they requested it.**

Default: ``True``.

``OPENHUMANS_DELETE_ON_DEAUTH``
--------------------------------

If you have set up the deauthorization hook on Open Humans the
``OPENHUMANS_DELETE_ON_DEAUTH`` will specify how an incoming request from
this hook will be processed. If set to ``True`` an ``OpenHumansMember``
object will always be deleted, even if the member did not request this deletion.

Default: ``False``.
