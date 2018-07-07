from datetime import timedelta
from urllib.parse import urljoin
import arrow
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
import requests
import ohapi
import os
import json
try:
    import urllib.parse as urlparse
except ImportError:
    import urlparse
from humanfriendly import parse_size
OH_BASE_URL = settings.OPENHUMANS_OH_BASE_URL
MAX_FILE_DEFAULT = parse_size('128m')
OH_BASE_URL = os.getenv('OHAPI_OH_BASE_URL', 'https://www.openhumans.org/')


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

    def message(self, subject, message):
        """Send messages."""
        ohapi.api.message(subject=subject, message=message,
                          access_token=self.get_access_token())

    def upload_stream(stream, filename, metadata, access_token,
                  base_url=OH_BASE_URL, remote_file_info=None,
                  project_member_id=None, max_bytes=MAX_FILE_DEFAULT,
                  file_identifier=None):
        """
        Upload a file object using the "direct upload" feature, which uploads to
        an S3 bucket URL provided by the Open Humans API. To learn more about this
        API endpoint see:
          * https://www.openhumans.org/direct-sharing/on-site-data-upload/
          * https://www.openhumans.org/direct-sharing/oauth2-data-upload/
        :param stream: This field is the stream (or file object) to be
            uploaded.
        :param metadata: This field is the metadata associated with the file.
            Description and tags are compulsory fields of metadata.
        :param access_token: This is user specific access token/master token.
        :param base_url: It is this URL `https://www.openhumans.org`.
        :param remote_file_info: This field is for for checking if a file with
            matching name and file size already exists. Its default value is none.
        :param project_member_id: This field is the list of project member id of
            all members of a project. Its default value is None.
        :param max_bytes: This field is the maximum file size a user can upload.
            Its default value is 128m.
        :param max_bytes: If provided, this is used in logging output. Its default
            value is None (in which case, filename is used).
        """
        if not file_identifier:
            file_identifier = filename

        # Determine a stream's size using seek.
        # f is a file-like object.
        old_position = stream.tell()
        stream.seek(0, os.SEEK_END)
        filesize = stream.tell()
        stream.seek(old_position, os.SEEK_SET)
        if filesize == 0:
            raise Exception('The submitted file is empty.')

        # Check size, and possibly remote file match.
        # if _exceeds_size(filesize, max_bytes, file_identifier):
        #     raise ValueError("Maximum file size exceeded")
        if remote_file_info:
            response = requests.get(remote_file_info['download_url'], stream=True)
            remote_size = int(response.headers['Content-Length'])
            if remote_size == filesize:
                info_msg = ('Skipping {}, remote exists with matching '
                            'file size'.format(file_identifier))
                # logging.info(info_msg)
                return(info_msg)

        url = urlparse.urljoin(
            base_url,
            '/api/direct-sharing/project/files/upload/direct/?{}'.format(
                urlparse.urlencode({'access_token': access_token})))

        if not(project_member_id):
            response = ohapi.exchange_oauth2_member(access_token)
            project_member_id = response['project_member_id']

        data = {'project_member_id': project_member_id,
                'metadata': json.dumps(metadata),
                'filename': filename}
        r1 = requests.post(url, data=data)
        # handle_error(r1, 201)
        requests.put(url=r1.json()['url'], data=stream)
        done = urlparse.urljoin(
            base_url,
            '/api/direct-sharing/project/files/upload/complete/?{}'.format(
                urlparse.urlencode({'access_token': access_token})))

        r2 = requests.post(done, data={'project_member_id': project_member_id,
                                       'file_id': r1.json()['id']})
        # handle_error(r2, 200)
        # logging.info('Upload complete: {}'.format(file_identifier))
        return r2
