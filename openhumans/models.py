from datetime import timedelta
from urllib.parse import urljoin
import arrow
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
import requests
import ohapi

from .settings import openhumans_settings

OH_BASE_URL = openhumans_settings['OPENHUMANS_OH_BASE_URL']

User = get_user_model()


def make_unique_username(base):
    """
    Ensure a unique username. Probably this never actually gets used.
    """
    try:
        User.objects.get(username=base)
    except User.DoesNotExist:
        return base
    counter = 2
    while True:
        name = base + str(counter)
        try:
            User.objects.get(username=name)
            counter += 1
        except User.DoesNotExist:
            return name


class OpenHumansMember(models.Model):
    """
    Data storage, auth, etc. related to an Open Humans member account.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    oh_id = models.CharField(max_length=16, primary_key=True, unique=True)
    access_token = models.CharField(max_length=256)
    refresh_token = models.CharField(max_length=256)
    token_expires = models.DateTimeField()
    public = models.BooleanField(default=False)

    @staticmethod
    def get_expiration(expires_in):
        return (arrow.now() + timedelta(seconds=expires_in)).format()

    @classmethod
    def create(cls, oh_id, data, user=None):
        """
        Create an Open Humans member, and corresponding User, if not provided.

        :param oh_id: This field is the Openhumans id.
        :param data: This field contain data related to access token and
            refresh token.
        :param user: This field's default value is None.
        """
        if not user:
            new_username = make_unique_username(
                base='{}_openhumans'.format(oh_id))
            user = User(username=new_username)
            user.save()
        oh_member = cls(
            user=user,
            oh_id=oh_id,
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
            token_expires=cls.get_expiration(data["expires_in"]))
        return oh_member

    def __str__(self):
        return "<OpenHumansMember(oh_id='{}')>".format(
            self.oh_id)

    def get_access_token(self,
                         client_id=settings.OPENHUMANS_CLIENT_ID,
                         client_secret=settings.OPENHUMANS_CLIENT_SECRET):
        """
        Return access token. Refresh first if necessary.

        :param client_id: This field is the client_id of the project. Project
            info can be found at
            https://www.openhumans.org/direct-sharing/projects/manage/
        :param client_secret: This field is the client secret of the project.
            Project info can be found at
            https://www.openhumans.org/direct-sharing/projects/manage/
        """
        delta = timedelta(seconds=60)
        if arrow.get(self.token_expires) - delta < arrow.now():
            self._refresh_tokens(client_id=client_id,
                                 client_secret=client_secret)
        return self.access_token

    def _refresh_tokens(self, client_id, client_secret):
        """
        Refresh access token.

        :param client_id: This field is the client_id of the project. Project
            info can be found at
            https://www.openhumans.org/direct-sharing/projects/manage/
        :param client_secret: This field is the client secret of the project.
            Project info can be found at
            https://www.openhumans.org/direct-sharing/projects/manage/
        """
        response = requests.post(
            urljoin(OH_BASE_URL, '/oauth2/token/'),
            data={
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token},
            auth=requests.auth.HTTPBasicAuth(client_id, client_secret))
        if response.status_code == 200:
            data = response.json()
            self.access_token = data['access_token']
            self.refresh_token = data['refresh_token']
            self.token_expires = self.get_expiration(data['expires_in'])
            self.save()

    def message(self, subject, message):
        """
        Send messages.

        :param subject: This field is the subject of the message.
        :param message: This field is the message which is to be send.
        """
        ohapi.api.message(subject=subject, message=message,
                          access_token=self.get_access_token())

    def list_files(self):
        """List files."""
        data = ohapi.api.exchange_oauth2_member(
                                    access_token=self.get_access_token())
        return data['data']

    def upload(self, stream, filename, metadata, file_identifier=None):
        """Upload file to Open Humans."""
        ohapi.api.upload_stream(stream=stream, filename=filename,
                                metadata=metadata,
                                access_token=self.get_access_token(),
                                file_identifier=file_identifier)

    def delete_single_file(self, file_id=None, file_basename=None):
        """
        Deletes a file. Specify file_id or file_basename but not both.

        :param file_id: This field is the file id of the file to be deleted.
        :param file_basename: This field is the file basename of the file to
            be deleted. It's default value is None.
        """
        if(file_id and file_basename):
            raise ValidationError("Only one of the following must be " +
                                  "specified file_id or file_basename not both"
                                  )
        if(not file_id and not file_basename):
            raise ValidationError("Either file_id or file_basename must be " +
                                  "specified")
        ohapi.api.delete_files(
            project_member_id=self.oh_id,
            access_token=self.get_access_token(),
            file_id=file_id,
            file_basename=file_basename)

    def delete_all_files(self):
        ohapi.api.delete_files(
            project_member_id=self.oh_id,
            access_token=self.get_access_token(),
            all_files=True)
