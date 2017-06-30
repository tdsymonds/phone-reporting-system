# -*- coding: utf-8 -*- 
from django.conf.urls import url

from .views import (AllCallView, CountView, DailyCallTimeView, DailyCountView, 
    DonutView, MyCallView)


urlpatterns = [
    url(r'^$', MyCallView.as_view(), name='my_calls'),
    url(r'^all-calls/$', AllCallView.as_view(), name='all_calls'),

    url(r'^api/count/$', CountView.as_view(), name='count'),
    url(r'^api/daily-count/$', DailyCountView.as_view(), name='daily_count'),
    url(r'^api/daily-call-time/$', DailyCallTimeView.as_view(), name='daily_call_time'),
    url(r'^api/donut/$', DonutView.as_view(), name='donut'),
]
