from django.conf.urls import include, url
from . import views


urlpatterns = [
    url(r'^$', views.index),
    url(r'^submit$', views.submit, name='submit')
]
