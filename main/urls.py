from django.conf.urls import include, url
from . import views


urlpatterns = [
    url(r'^$', views.index),
    url(r'^submit$', views.submit, name='submit'),
    url(r'^check_job/([0-9]{,4})$', views.check_job, name='check_job'),
]
