from django.conf.urls import url
from . import views

app_name = 'openhumans'
urlpatterns = [
    url(r'^complete/?$', views.complete, name='complete')
]
