import json
from urllib.parse import urljoin

from django.conf import settings
from django.contrib.auth import login
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import redirect, render
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from .models import OpenHumansMember
from .settings import openhumans_settings
from .signals import member_deauth

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
    login_member(request)
    if not request.user.is_authenticated:
        return redirect(openhumans_settings['OPENHUMANS_LOGOUT_REDIRECT_URL'])
    else:
        return redirect(openhumans_settings['OPENHUMANS_LOGIN_REDIRECT_URL'])


@csrf_exempt
def deauth(request):
    """
    Receive and act on deauthorization notification from Open Humans.
    """
    if request.method == 'POST':
        json_str = json.loads(request.body.decode('utf-8'))
        deauth_data = json.loads(json_str)
        oh_member = OpenHumansMember.objects.get(
            oh_id=deauth_data['project_member_id'])
        member_deauth.send(
            sender=OpenHumansMember,
            open_humans_member=oh_member,
            erasure_requested=deauth_data['erasure_requested'])
        return HttpResponse('Received')
    return HttpResponseNotAllowed()


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
