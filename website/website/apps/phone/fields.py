# -*- coding: utf-8 -*-
from django import forms


class DateRangeField(forms.DateField):
    def to_python(self, value):
        if not value:
            return None, None
        values = value.split(' - ')
        from_date = super().to_python(values[0])
        to_date = super().to_python(values[1])
        return from_date, to_date
