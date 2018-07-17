"""
Create your views here.
"""
from django.shortcuts import render, redirect
from django.views import View


class list_files(View):

    list_template = 'main/list.html'
    not_authorized_url = 'index'

    def get(self, request):
        """List files."""
        if request.user.is_authenticated:
            oh_member = request.user.openhumansmember
            context = oh_member.list_files()
            return render(request, self.list_template,
                          context=context)
        return redirect(self.not_authorized_url)
