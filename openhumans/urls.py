from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^delete/(?P<file_id>\w+)/?$', views.delete_file, name='delete')
]
