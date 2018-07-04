"""
Create your views here.
"""
from django.views import View
from django.shortcuts import redirect


class DeleteFile(View):

    def post(self, request, file_id=None, file_basename=None, next='/'):
        """
        Delete specified file in Open Humans for this project member.
        """
        if request.user.is_authenticated:
            oh_member = request.user.openhumansmember
            oh_member = request.user.openhumansmember
            oh_member.delete_single_file(
                file_id=file_id,
                file_basename=file_basename)
            return redirect(next)
        return redirect(next)


class DeleteAllFiles(View):

    def post(self, request, next='/'):
        """
        Delete all project files in Open Humans for this project member.
        """
        if request.user.is_authenticated:
            oh_member = request.user.openhumansmember
            oh_member.delete_all_files()
            return redirect(next)
        return redirect(next)
