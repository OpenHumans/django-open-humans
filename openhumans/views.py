from django.conf import settings
from django.contrib.auth import login
from django.shortcuts import redirect

from .helpers import oh_code_to_member
OH_BASE_URL = settings.OPENHUMANS_OH_BASE_URL
OH_API_BASE = OH_BASE_URL + '/api/direct-sharing'
OH_OAUTH2_REDIRECT_URI = '{}/complete'.format(settings.OPENHUMANS_APP_BASE_URL)


def login_member(request):
    code = request.GET.get('code', '')
    try:
        oh_member = oh_code_to_member(code=code)
    except Exception:
        oh_member = None
        print("exception while logging in")
    if oh_member:
        # Log in the user.
        user = oh_member.user
        login(request, user,
              backend='django.contrib.auth.backends.ModelBackend')


def complete(request):
    """
    Receive user from Open Humans. Store data, start data upload task.
    """
    # logger.debug("Received user returning from Open Humans.")

    login_member(request)
    if not request.user.is_authenticated:
        # logger.debug('Invalid code exchange. User returned to start page.')
        print('Invalid code exchange. User returned to start page.')
        return redirect('/')
    else:
        return redirect('overview')
