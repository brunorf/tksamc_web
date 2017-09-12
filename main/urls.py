from django.conf.urls import include, url
from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^results$', views.results, name='results'),
    url(r'^theory$', views.theory, name='theory'),
    url(r'^submit$', views.submit, name='submit'),
    url(r'^check_job/([a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}\Z)$', views.check_job, name='check_job'),
    url(r'^googlecc98d7b5a37f2c7d.html$', views.google_search_console, name='google_search_console'),
    url(r'^sitemap.xml$', views.sitemap, name='sitemap'),
]
