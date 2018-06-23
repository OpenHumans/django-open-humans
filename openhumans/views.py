"""
Create your views here.
"""
from .forms import MessageProjectMembersForm
from django.shortcuts import redirect, render
from django.views import generic


class Message(generic.FormView):
    form_class = MessageProjectMembersForm
    success_url = '/'
    message_template = 'main/message.html'
    not_authorized_url = '/'

    def get(self, request):
        """Check if user is authenticated."""
        if request.user.is_authenticated:
            form = self.form_class()
            return render(request, self.message_template, {'form': form})
        return redirect(self.not_authorized_url)

    def post(self, request):
        """Message individual or multiple project members."""
        if request.user.is_authenticated:
            oh_member = request.user.openhumansmember
            form = self.form_class(request.POST)
            if form.is_valid():
                oh_member.message(form.cleaned_data['subject'],
                                  form.cleaned_data['message'],
                                  form.cleaned_data['access_token'],
                                  form.cleaned_data['all_members'],
                                  form.cleaned_data['project_member_ids'])
            else:
                form = self.form_class()
                return render(request, self.message_template, {'form': form}, )
            return redirect(self.success_url)
        return redirect(self.not_authorized_url)
