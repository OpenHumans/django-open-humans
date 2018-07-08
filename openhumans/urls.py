from django.conf.urls import url
from . import views

app_name = 'openhumans'
urlpatterns = [
    url(r'^delete_file/?$',
        views.DeleteFile.as_view(), name='delete_file'),
    url(r'^delete_all_files/?$', views.DeleteAllFiles.as_view(),
        name='delete_all_files')

]
