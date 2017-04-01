# -*- coding: utf-8 -*- 
from django.conf.urls import url

from .views import HomeView, direction, internal_external


urlpatterns = [
    url(r'^$', HomeView.as_view(), name='home'),

    url(r'^direction/$', direction, name='direction'),
    url(r'^internal_external/$', internal_external, name='internal_external'),
]
