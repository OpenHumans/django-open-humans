from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^list/?$', views.list_files.as_view(), name='list'),
]
