from datetime import timedelta
from urllib.parse import urljoin
try:
    from urllib2 import HTTPError
except ImportError:
    from urllib.error import HTTPError

import arrow
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
import requests
import json

OH_BASE_URL = settings.OPENHUMANS_OH_BASE_URL
OPPENHUMANS_APP_BASE_URL = settings.OPENHUMANS_APP_BASE_URL
OH_API_BASE = OH_BASE_URL + '/api/direct-sharing'
OH_DIRECT_UPLOAD = OH_API_BASE + '/project/files/upload/direct/'
OH_DIRECT_UPLOAD_COMPLETE = OH_API_BASE + '/project/files/upload/complete/'

OH_OAUTH2_REDIRECT_URI = '{}/complete'.format(settings.OPENHUMANS_APP_BASE_URL)

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
        """
        Return access token. Refresh first if necessary.
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

    def upload(self, description, tags, filehandle):
        if filehandle is not None:
            metadata = {'tags': tags,
                        'description': description}
            upload_url = '{}?access_token={}'.format(
                OH_DIRECT_UPLOAD, self.get_access_token())
            req1 = requests.post(upload_url,
                                 data={'project_member_id': self.oh_id,
                                       'filename': filehandle.name,
                                       'metadata': json.dumps(metadata)})
            if req1.status_code != 201:
                raise HTTPError(upload_url, req1.status_code,
                                'Bad response when starting file upload.',
                                hdrs=None, fp=None)

            # Upload to S3 target.
            req2 = requests.put(url=req1.json()['url'], data=filehandle)
            if req2.status_code != 200:
                raise HTTPError(req1.json()['url'], req2.status_code,
                                'Bad response when uploading to target.',
                                hdrs=None, fp=None)

            # Report completed upload to Open Humans.
            complete_url = ('{}?access_token={}'.format(
                OH_DIRECT_UPLOAD_COMPLETE, self.get_access_token()))
            req3 = requests.post(complete_url,
                                 data={'project_member_id': self.oh_id,
                                       'file_id': req1.json()['id']})
            if req3.status_code != 200:
                raise HTTPError(complete_url, req2.status_code,
                                'Bad response when completing upload.',
                                hdrs=None, fp=None)
