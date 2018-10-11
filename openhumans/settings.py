from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


DEFAULTS = {
    'OPENHUMANS_OH_BASE_URL': 'https://www.openhumans.org',
    'OPENHUMANS_LOGIN_REDIRECT_URL': getattr(
        settings, 'LOGIN_REDIRECT_URL', '/'),
    'OPENHUMANS_LOGOUT_REDIRECT_URL': getattr(
        settings, 'LOGOUT_REDIRECT_URL', '/'),
    'OPENHUMANS_APP_BASE_URL': None,
    'OPENHUMANS_CLIENT_ID': None,
    'OPENHUMANS_CLIENT_SECRET': None,
    'OPENHUMANS_DELETE_ON_ERASURE': True,
    'OPENHUMANS_DELETE_ON_DEAUTH': False,
}


def compile_settings():
    init = {k: getattr(settings, k, DEFAULTS[k]) for k in DEFAULTS.keys()}

    required_settings = [
        'OPENHUMANS_APP_BASE_URL', 'OPENHUMANS_CLIENT_ID',
        'OPENHUMANS_CLIENT_SECRET']
    req_err_msg = (
        "One or more of the following required Django project "
        "settings is missing: {}".format(', '.join(required_settings)))
    for setting in required_settings:
        if not init[setting]:
            raise ImproperlyConfigured(req_err_msg)

    return init


openhumans_settings = compile_settings()
