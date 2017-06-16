# -*- coding: utf-8 -*- 
from django.conf import settings
from django import forms
from website.apps.authentication.models import CustomUser

from .fields import DateRangeField
from .models import Department


class FilterBarForm(forms.Form):
    date_range = DateRangeField(required=False, input_formats=settings.DATE_INPUT_FORMATS,
        widget=forms.TextInput(attrs={
            'placeholder': 'Date range', 
            'class': 'form-control datepicker'
        }))


class FullFilterBarForm(FilterBarForm):
    myfilters = [('u%s' % u.pk, u.get_full_name()) for u in CustomUser.objects.all()]
    myfilters += [('d%s'% d.pk, d.name) for d in Department.objects.all()]

    myfilters = sorted(myfilters, key=lambda x: x[1])

    filters = forms.MultipleChoiceField(required=False, choices=myfilters)
