"""
Create your views here.
"""
from .forms import DeleteDataFileForm
from django.shortcuts import redirect
from django.views import generic
import ohapi


class DeleteFile(generic.FormView):
    form_class = DeleteDataFileForm
    next = '/'
    not_authorized_url = '/'

    def post(self, request):
        """
        Delete specified file in Open Humans for this project member.
        """

        if request.user.is_authenticated:
            oh_member = request.user.openhumansmember
            ohapi.api.delete_files(
                project_member_id=oh_member.oh_id,
                access_token=oh_member.get_access_token(),
                file_id=file_id)
            return redirect(self.next)
        return redirect(self.not_authorized_url)


class DeleteAllFiles(generic.FormView):
    form_class = DeleteDataFileForm
    next = '/'
    not_authorized_url = '/'

    def post(self, request):
        """
        Delete all current project files in Open Humans for this project member.
        """

        if request.user.is_authenticated:
            oh_member = request.user.openhumansmember
            ohapi.api.delete_files(
                project_member_id=oh_member.oh_id,
                access_token=oh_member.get_access_token(),
                all_files=True)
            return redirect(self.next)
        return redirect(self.not_authorized_url)
