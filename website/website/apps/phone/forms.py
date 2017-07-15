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
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request')

        super().__init__(*args, **kwargs)
        
        departments = Department.my_objects.viewable_by(request.user)
        users = CustomUser.objects.in_departments(departments)

        myfilters = [('u%s' % u.pk, u.get_full_name()) for u in users]
        myfilters += [('d%s'% d.pk, d.name) for d in departments]

        myfilters = sorted(myfilters, key=lambda x: x[1])

        self.fields['filters'] = forms.MultipleChoiceField(required=False, choices=myfilters)
