from django.conf.urls import include, url
from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^results$', views.results, name='results'),
    url(r'^theory$', views.theory, name='theory'),
    url(r'^submit$', views.submit, name='submit'),
    url(r'^check_job/([0-9]{,4})$', views.check_job, name='check_job'),
    url(r'^googlecc98d7b5a37f2c7d.html$', views.google_search_console, name='google_search_console'),
    url(r'^sitemap.xml$', views.sitemap, name='sitemap'),
]
