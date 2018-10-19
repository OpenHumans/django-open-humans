from datetime import timedelta
import logging
from urllib.parse import urljoin

import arrow
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
import requests
import ohapi

from .exceptions import OpenHumansAPIResponseError
from .helpers import get_redirect_uri
from .settings import openhumans_settings

OPENHUMANS_OH_BASE_URL = openhumans_settings['OPENHUMANS_OH_BASE_URL']
OPENHUMANS_CLIENT_ID = openhumans_settings['OPENHUMANS_CLIENT_ID']
OPENHUMANS_CLIENT_SECRET = openhumans_settings['OPENHUMANS_CLIENT_SECRET']

logger = logging.getLogger(__name__)
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

    @staticmethod
    def get_auth_url():
        """Gets the authentication url."""
        if OPENHUMANS_CLIENT_ID:
            auth_url = ohapi.api.oauth2_auth_url(
                client_id=OPENHUMANS_CLIENT_ID,
                redirect_uri=get_redirect_uri(),
                base_url=OPENHUMANS_OH_BASE_URL)
        else:
            auth_url = ''
        return auth_url

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

    @classmethod
    def get_create_member(cls, data):
        '''
        use the data returned by `ohapi.api.oauth2_token_exchange`
        and return an oh_member object
        '''
        oh_id = ohapi.api.exchange_oauth2_member(
            access_token=data['access_token'],
            base_url=OPENHUMANS_OH_BASE_URL)['project_member_id']
        try:
            oh_member = cls.objects.get(oh_id=oh_id)
            logger.debug('Member {} re-authorized.'.format(oh_id))
            oh_member.access_token = data['access_token']
            oh_member.refresh_token = data['refresh_token']
            oh_member.token_expires = OpenHumansMember.get_expiration(
                data['expires_in'])
        except cls.DoesNotExist:
            oh_member = cls.create(oh_id=oh_id, data=data)
            logger.debug('Member {} created.'.format(oh_id))
        oh_member.save()
        return oh_member

    @classmethod
    def oh_code_to_member(cls, code):
        """
        Exchange code for token, use this to create and return
        OpenHumansMember. If a matching OpenHumansMember already exists in db,
        update and return it.
        """
        if not code:
            raise ValueError("'code' parameter empty or not provided")
        params = {
            'client_id': OPENHUMANS_CLIENT_ID,
            'client_secret': OPENHUMANS_CLIENT_SECRET,
            'code': code,
            'base_url': OPENHUMANS_OH_BASE_URL,
        }
        params['redirect_uri'] = get_redirect_uri()
        data = ohapi.api.oauth2_token_exchange(**params)
        if 'error' in data:
            raise OpenHumansAPIResponseError(
                'Error in token exchange: {}'.format(data))

        if 'access_token' in data:
            return cls.get_create_member(data)
        else:
            raise OpenHumansAPIResponseError(
                'Neither token nor error info in Open Humans API response.')

    def __str__(self):
        return "<OpenHumansMember(oh_id='{}')>".format(
            self.oh_id)

    def get_access_token(self,
                         client_id=OPENHUMANS_CLIENT_ID,
                         client_secret=OPENHUMANS_CLIENT_SECRET):
        """
        Return access token. Refresh first if necessary.

        :param client_id: This field is the client_id of the project. Project
            info can be found at
            https://www.openhumans.org/direct-sharing/projects/manage/
        :param client_secret: This field is the client secret of the project.
            Project info can be found at
            https://www.openhumans.org/direct-sharing/projects/manage/
        """
        # Also refresh if nearly expired (less than 60s remaining).
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
            urljoin(OPENHUMANS_OH_BASE_URL, '/oauth2/token/'),
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
