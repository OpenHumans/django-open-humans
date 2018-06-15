"""
Create your views here.
"""

from django.shortcuts import redirect
import ohapi
from django.views import View


class delete_file(View):
    success_url = 'list'
    not_authorized_url = 'index'

    def get(self, request, file_id):
        """
        Delete specified file in Open Humans for this project member.
        """

        if request.user.is_authenticated and request.user.username != 'admin':
            oh_member = request.user.openhumansmember
            ohapi.api.delete_files(
                project_member_id=oh_member.oh_id,
                access_token=oh_member.get_access_token(),
                file_id=file_id)
            return redirect(self.success_url)
        return redirect(self.not_authorized_url)


class delete_all_oh_files(View):
    success_url = 'list'
    not_authorized_url = 'index'

    def get(self, request):
        """
        Delete all current project files in Open Humans for this project member.
        """

        if request.user.is_authenticated and request.user.username != 'admin':
            oh_member = request.user.openhumansmember
            ohapi.api.delete_files(
                project_member_id=oh_member.oh_id,
                access_token=oh_member.get_access_token(),
                all_files=True)
            return redirect(self.success_url)
        return redirect(self.not_authorized_url)
