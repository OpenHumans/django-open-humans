"""
Create your views here.
"""
from .forms import DeleteDataFileForm
from django.shortcuts import redirect
from django.views import generic


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
            form = self.form_class(request.POST, request.FILES)
            oh_member.delete_single_file(form.data['file_id'])
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
            oh_member.delete_all_files()
            return redirect(self.next)
        return redirect(self.not_authorized_url)
