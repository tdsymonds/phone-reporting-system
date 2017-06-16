# -*- coding: utf-8 -*- 
from django.conf import settings
from django import forms

from .fields import DateRangeField


class FilterBarForm(forms.Form):
    date_range = DateRangeField(required=False, input_formats=settings.DATE_INPUT_FORMATS,
        widget=forms.TextInput(attrs={
            'placeholder': 'Date range', 
            'class': 'form-control datepicker'
        }))