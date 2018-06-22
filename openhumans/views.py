"""
Create your views here.
"""
from .forms import DeleteDataFileForm
from django.shortcuts import redirect
from django.views import generic
from django.http import HttpResponse


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
            if form.is_valid():
                oh_member.delete_single_file(form.cleaned_data['file_id'])
            else:
                return HttpResponse("The form submitted is not valid. %s" %
                                    form.errors)
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
