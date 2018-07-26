from datetime import timedelta
from urllib.parse import urljoin
import arrow
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
import requests
import ohapi

try:
    from urllib2 import HTTPError
except ImportError:
    from urllib.error import HTTPError
OH_BASE_URL = settings.OPENHUMANS_OH_BASE_URL

OPPENHUMANS_APP_BASE_URL = settings.OPENHUMANS_APP_BASE_URL

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
        """Return access token. Refresh first if necessary."""
        # Also refresh if nearly expired (less than 60s remaining).
        delta = timedelta(seconds=60)
        if arrow.get(self.token_expires) - delta < arrow.now():
            self._refresh_tokens(client_id=client_id,
                                 client_secret=client_secret)
        return self.access_token

    def _refresh_tokens(self, client_id, client_secret):
        """Refresh access token."""
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

    def delete_single_file(self, file_id=None, file_basename=None):
        """Deletes a file.
           Specify file_id or file_basename but not both """
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

    def message(self, subject, message):
        """Send messages."""
        ohapi.api.message(subject=subject, message=message,
                          access_token=self.get_access_token())

    def upload(self, stream, filename, metadata, file_identifier=None):
        """Upload file to Open Humans."""
        ohapi.api.upload_stream(stream=stream, filename=filename,
                                metadata=metadata,
                                access_token=self.get_access_token(),
                                file_identifier=file_identifier)
