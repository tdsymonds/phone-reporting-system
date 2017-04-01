# -*- coding: utf-8 -*- 
from datetime import datetime, timedelta
from django import forms
from django.forms.extras.widgets import SelectDateWidget


class FilterBarForm(forms.Form):
    date_from = forms.DateField(widget=SelectDateWidget(years=range(2016, datetime.now().year+1)), initial=(datetime.now()-timedelta(days=7)))
    date_to = forms.DateField(widget=SelectDateWidget(years=range(2016, datetime.now().year+1)), initial=datetime.now())
