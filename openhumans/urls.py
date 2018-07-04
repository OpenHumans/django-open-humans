from django.conf.urls import url
from . import views

app_name = 'openhumans'
urlpatterns = [
    url(r'^delete/(?P<file_id>\w+)/(?P<next>.)/?$',
        views.DeleteFile.as_view(), name='delete_file'),
    url(r'^delete/(?P<file_basename>\w+)/(?P<next>.)/?$',
        views.DeleteFile.as_view(), name='delete_file'),
    url(r'^delete_all_files/(?P<next>.)/?$', views.DeleteAllFiles.as_view(),
        name='delete_all_files')

]
