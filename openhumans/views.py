"""
Create your views here.
"""

from django.shortcuts import redirect
import ohapi


def oh_client_info():
    client_info = {
        'client_id': settings.OPENHUMANS_CLIENT_ID,
        'client_secret': settings.OPENHUMANS_CLIENT_SECRET,
    }
    return client_info


def delete_file(request, file_id, success_template='list', not_authorized_template='index'):
    """
    Delete specified file in Open Humans for this project member.
    """
    if request.user.is_authenticated and request.user.username != 'admin':
        oh_member = request.user.openhumansmember
        ohapi.api.delete_files(
            project_member_id=oh_member.oh_id,
            access_token=oh_member.get_access_token(),
            file_id=file_id)
        return redirect(success_template)
    return redirect(not_authorized_template)


def delete_all_oh_files(oh_member):
    """
    Delete all current project files in Open Humans for this project member.
    """
    ohapi.api.delete_files(
        project_member_id=oh_member.oh_id,
        access_token=oh_member.get_access_token(),
        all_files=True)
