from django.conf import settings

DEFAULTS = {
    'OPENHUMANS_OH_BASE_URL': 'https://www.openhumans.org',
}

openhumans_settings = {
    k: getattr(settings, k, DEFAULTS[k]) for k in DEFAULTS.keys()
}
