# -*- coding: utf-8 -*- 
from django.conf.urls import url

from .views import AllCallView, DirectionView, DonutView, InternalExternalView, MyCallView


urlpatterns = [
    url(r'^$', MyCallView.as_view(), name='my_calls'),
    url(r'^all-calls/$', AllCallView.as_view(), name='all_calls'),

    url(r'^api/direction/$', DirectionView.as_view(), name='direction'),
    url(r'^api/internal_external/$', InternalExternalView.as_view(), name='internal_external'),
    url(r'^api/donut/$', DonutView.as_view(), name='donut'),
]
