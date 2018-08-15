import json
import logging
try:
    from urllib2 import HTTPError
except ImportError:
    from urllib.error import HTTPError

from django.conf import settings
from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.contrib import messages
from django.utils.safestring import mark_safe

import ohapi
import requests

from .helpers import oh_code_to_member, oh_client_info
from django.views import View
from django.shortcuts import render, redirect

OH_BASE_URL = settings.OPENHUMANS_OH_BASE_URL
OH_API_BASE = OH_BASE_URL + '/api/direct-sharing'

def login_member(request):
    code = request.GET.get('code', '')
    try:
        oh_member = oh_code_to_member(code=code)
    except Exception:
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
        # logger.debug('Invalid code exchange. User returned to start page.')
        print('Invalid code exchange. User returned to start page.')
        return redirect('/')
    else:
        return redirect('overview')

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
