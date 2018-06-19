import json
import ohapi
import requests
try:
    from urllib2 import HTTPError
except ImportError:
    from urllib.error import HTTPError
from django.conf import settings
from django.shortcuts import redirect, render
from django.views import generic
from .forms import FileUploadForm

OH_BASE_URL = settings.OPENHUMANS_OH_BASE_URL
OH_API_BASE = OH_BASE_URL + '/api/direct-sharing'
OH_DIRECT_UPLOAD = OH_API_BASE + '/project/files/upload/direct/'
OH_DIRECT_UPLOAD_COMPLETE = OH_API_BASE + '/project/files/upload/complete/'

OH_OAUTH2_REDIRECT_URI = '{}/complete'.format(settings.OPENHUMANS_APP_BASE_URL)


class upload(generic.FormView):
    form_class = FileUploadForm
    success_url = 'index'
    not_authorized_url = 'index'
    template_name = 'main/upload.html'

    def post(self, request):
        if request.user.is_authenticated:
            form = self.form_class(request.POST, request.FILES)
            desc = form.get_description()
            tags = form.get_tags().split(',')
            filehandle = form.get_file()
            oh_member = request.user.openhumansmember
            if filehandle is not None:
                metadata = {'tags': tags,
                            'description': desc}
                upload_url = '{}?access_token={}'.format(
                    OH_DIRECT_UPLOAD, oh_member.get_access_token())
                req1 = requests.post(upload_url,
                                     data={'project_member_id': oh_member.oh_id,
                                           'filename': filehandle.name,
                                           'metadata': json.dumps(metadata)})
                if req1.status_code != 201:
                    raise HTTPError(upload_url, req1.status_code,
                    'Bad response when starting file upload.', hdrs=None, fp=None)

                # Upload to S3 target.
                req2 = requests.put(url=req1.json()['url'], data=filehandle)
                if req2.status_code != 200:
                    raise HTTPError(req1.json()['url'], req2.status_code,
                    'Bad response when uploading to target.', hdrs=None, fp=None)

                # Report completed upload to Open Humans.
                complete_url = ('{}?access_token={}'.format(
                    OH_DIRECT_UPLOAD_COMPLETE, oh_member.get_access_token()))
                req3 = requests.post(complete_url,
                                     data={'project_member_id': oh_member.oh_id,
                                           'file_id': req1.json()['id']})
                if req3.status_code != 200:
                    raise HTTPError(complete_url, req2.status_code,
                    'Bad response when completing upload.', hdrs=None, fp=None)
            return redirect(self.success_url)
        return redirect(self.not_authorized_url)
