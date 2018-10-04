from urllib.parse import urljoin

from django.conf import settings
from django.urls import reverse

from .settings import openhumans_settings

OH_OAUTH2_REDIRECT_URI = '{}/complete'.format(settings.OPENHUMANS_APP_BASE_URL)
OH_BASE_URL = openhumans_settings['OPENHUMANS_OH_BASE_URL']


def get_redirect_uri():
    '''
    Construct redirect_uri based on the app's base URL and completion URL
    '''
    return urljoin(openhumans_settings['OPENHUMANS_APP_BASE_URL'],
                   reverse("openhumans:complete"))
