# -*- coding: utf-8 -*- 

DIRECTION_CHOICES = [
    [0, 'Inbound'],
    [1, 'Outbound'],
]

INTERNAL_EXTERNAL_CHOICES = [
    [0, 'Internal'],
    [1, 'External'],
]

CHART_TYPE_CHOICES = [
    ['columnChart', 'Column'],
    ['count', 'Count'],
    ['donut', 'Donut'],
    ['line', 'Line'],
    ['stackedChart', 'Stacked'],

]

CHART_URL_CHOICES = [
    ['count', 'count'],
    ['daily_call_time', 'daily_call_time'],
    ['daily_count', 'daily_count'],
    ['department', 'department'],
    ['donut', 'donut'],
]

NUMBER_OF_CHART_CHOICES = [
    ['1', '1'],
    ['2', '2'],
    ['4', '4'],
]