from django.conf.urls import url
from . import views

app_name = 'openhumans'
urlpatterns = [
    url(r'^message/?$', views.Message.as_view(), name='message')

]
