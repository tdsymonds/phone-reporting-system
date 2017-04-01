# -*- coding: utf-8 -*- 
from django.conf.urls import url

from .views import HomeView, direction


urlpatterns = [
    url(r'^$', HomeView.as_view(), name='home'),

    url(r'^direction/$', direction, name='direction'),
]
