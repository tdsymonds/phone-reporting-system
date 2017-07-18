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
        
        if request.user.is_superuser:
            # superusers can see all
            departments = Department.objects.all()
            users = CustomUser.objects.all()
        else:
            # else only show the departments they're authorised to see
            departments = request.user.departments_can_view.all()
            department_pks = departments.values_list('pk', flat=True)
            users = CustomUser.objects.filter(department__pk__in=department_pks)

        myfilters = [('u%s' % u.pk, u.get_full_name()) for u in users]
        myfilters += [('d%s'% d.pk, d.name) for d in departments]
        myfilters = sorted(myfilters, key=lambda x: x[1])

        self.fields['filters'] = forms.MultipleChoiceField(required=False, choices=myfilters)
