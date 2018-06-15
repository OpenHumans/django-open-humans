from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^delete/(?P<file_id>\w+)/?$', views.delete_file.as_view(), name='delete'),
    url(r'^delete_all_files/?$', views.delete_all_oh_files.as_view(), name='delete_all_files')

]
