import json
import ohapi
import requests
try:
    from urllib2 import HTTPError
except ImportError:
    from urllib.error import HTTPError
from django.conf import settings
from django.shortcuts import redirect, render
from django.views import View
OH_BASE_URL = settings.OPENHUMANS_OH_BASE_URL
OH_API_BASE = OH_BASE_URL + '/api/direct-sharing'
OH_DIRECT_UPLOAD = OH_API_BASE + '/project/files/upload/direct/'
OH_DIRECT_UPLOAD_COMPLETE = OH_API_BASE + '/project/files/upload/complete/'

OH_OAUTH2_REDIRECT_URI = '{}/complete'.format(settings.OPENHUMANS_APP_BASE_URL)


class upload(View):
    success_url = 'index'
    not_authorized_url = 'index'
    upload_template = 'main/upload.html'

    def get(self, request):
        """Check if user is authenticated."""
        if request.user.is_authenticated:
            return render(request, self.upload_template)
        return redirect(self.not_authorized_url)

    def post(self, request):
        """
        This demonstrates using the Open Humans "large file" upload process.
        The small file upload process is simpler, but it can time out. This
        alternate approach is required for large files, and still appropriate
        for small files.
        This process is "direct to S3" using three steps:
        1. get S3 target URL from Open Humans
        2. Perform the upload
        3. Notify Open Humans when complete.
        """
        if request.user.is_authenticated:
            desc = request.POST['file_desc']
            tags = request.POST['file_tags'].split(',')
            filehandle = request.FILES.get('data_file')
            oh_member = request.user.openhumansmember
            if filehandle is not None:
                metadata = {'tags': tags,
                            'description': desc}
                upload_url = '{}?access_token={}'.format(
                    OH_DIRECT_UPLOAD, oh_member.get_access_token())
                req1 = requests.post(upload_url,
                                     data={'project_member_id':
                                           oh_member.oh_id,
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
                    OH_DIRECT_UPLOAD_COMPLETE, oh_member.get_access_token()))
                req3 = requests.post(complete_url,
                                     data={'project_member_id':
                                           oh_member.oh_id,
                                           'file_id': req1.json()['id']})
                if req3.status_code != 200:
                    raise HTTPError(complete_url, req2.status_code,
                                    'Bad response when completing upload.',
                                    hdrs=None, fp=None)
            return redirect(self.success_url)
        return redirect(self.not_authorized_url)
