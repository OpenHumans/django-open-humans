from django.views import View
from django.shortcuts import render, redirect


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
