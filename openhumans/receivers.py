from urllib.parse import urljoin

import requests

from django.conf import settings
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from .models import OpenHumansMember
from .settings import openhumans_settings
from .signals import member_deauth

OPENHUMANS_DEAUTH_ON_DELETE = openhumans_settings['OPENHUMANS_DEAUTH_ON_DELETE']

OPENHUMANS_DELETE_ON_ERASURE = openhumans_settings[
    'OPENHUMANS_DELETE_ON_ERASURE']

OPENHUMANS_DELETE_ON_DEAUTH = openhumans_settings[
    'OPENHUMANS_DELETE_ON_DEAUTH']

OPENHUMANS_OH_BASE_URL = openhumans_settings['OPENHUMANS_OH_BASE_URL']


@receiver(member_deauth)
def handle_deauth(sender, open_humans_member, erasure_requested, **kwargs):
    """
    Simple handling of deauth according to module configuration.

    Default module behavior is to do the following:
        If erasure_requested is true:
            call delete() on the OpenHumansMember object

    Default settings are for OPENHUMANS_DELETE_ON_DEAUTH to be false
    and for OPENHUMANS_DELETE_ON_ERASURE to be true.

    If OPENHUMANS_DELETE_ON_DEAUTH is true, delete() is called regardless of
    the value of erasure_requested.

    If both OPENHUMANS_DELETE_ON_DEAUTH and OPENHUMANS_DELETE_ON_ERASURE are
    false, no action is taken.
    """
    delete = (
        OPENHUMANS_DELETE_ON_DEAUTH or
        (OPENHUMANS_DELETE_ON_ERASURE and erasure_requested))
    if delete:
        try:
            open_humans_member.delete()
        except Exception as error:
            if settings.DEBUG:
                raise error
    else:
        # Note that member has deauthorized, but data remains.
        open_humans_member.oh_deauth = True
        open_humans_member.save()


@receiver(pre_delete, sender=OpenHumansMember)
def deauth_on_delete(**kwargs):
    """
    Deauthorize on Open Humans before deleting locally.
    """
    if OPENHUMANS_DEAUTH_ON_DELETE:
        instance = kwargs['instance']
        instance.deauth()
