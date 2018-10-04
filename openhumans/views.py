from urllib.parse import urljoin

from django.conf import settings
from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.views import View

from .models import OpenHumansMember
from .settings import openhumans_settings

OPENHUMANS_OH_BASE_URL = openhumans_settings['OPENHUMANS_OH_BASE_URL']
OH_API_BASE = urljoin(OPENHUMANS_OH_BASE_URL, '/api/direct-sharing')


def login_member(request):
    code = request.GET.get('code', '')
    try:
        oh_member = OpenHumansMember.oh_code_to_member(code=code)
    except Exception as error:
        if settings.DEBUG:
            raise error
        oh_member = None
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
        return redirect(openhumans_settings['OPENHUMANS_LOGOUT_REDIRECT_URL'])
    else:
        return redirect(openhumans_settings['OPENHUMANS_LOGIN_REDIRECT_URL'])


class DeleteFile(View):

    def post(self, request):
        """
        Delete specified file in Open Humans for this project member.
        """
        if request.user.is_authenticated:
            oh_member = request.user.openhumansmember
            file_id = None
            file_basename = None
            if "file_id" in request.POST:
                file_id = request.POST["file_id"]
            if "file_basename" in request.POST:
                file_basename = request.POST["file_basename"]
            oh_member.delete_single_file(file_id=file_id,
                                         file_basename=file_basename)
            next = request.POST["next"]
            return redirect(next)
        return redirect(next)


class DeleteAllFiles(View):

    def post(self, request):
        """
        Delete all project files in Open Humans for this project member.
        """
        if request.user.is_authenticated:
            next = request.POST["next"]
            oh_member = request.user.openhumansmember
            oh_member.delete_all_files()
            return redirect(next)
        return redirect(next)


class list_files(View):

    list_template = 'main/list.html'
    not_authorized_url = 'index'

    def get(self, request):
        """List files."""
        if request.user.is_authenticated:
            oh_member = request.user.openhumansmember
            context = {'files': oh_member.list_files()}
            return render(request, self.list_template,
                          context=context)
        return redirect(self.not_authorized_url)
