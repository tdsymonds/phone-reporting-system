# -*- coding: utf-8 -*- 
from django.conf.urls import url

from .views import DirectionView, InternalExternalView, MyCallView


urlpatterns = [
    url(r'^$', MyCallView.as_view(), name='my_calls'),

    url(r'^api/direction/$', DirectionView.as_view(), name='direction'),
    url(r'^api/internal_external/$', InternalExternalView.as_view(), name='internal_external'),
]
