# -*- coding: utf-8 -*- 
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.db.models.functions import TruncDay
from django.http import HttpResponse
from django.views.generic import TemplateView

import json

from .forms import FilterBarForm
from .models import Call


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'phone/pages/_home.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['form'] = FilterBarForm()
        return context


@login_required
def direction(request):
    DATE_FORMAT = '%d %b'

    # get form and qs parameters
    form = FilterBarForm(request.GET)
    internal_external = request.GET.get('internal_external', None)

    # if form not valid or not valid qs parameters
    if not form.is_valid() or internal_external not in [None,'0','1']:
        # error with dates so return
        return HttpResponse(
            json.dumps({'error': 'form not valid'}),
            content_type="application/json"
        )
    
    # get dates
    date_from = form.cleaned_data['date_from']
    date_to = form.cleaned_data['date_to'] + timedelta(days=1)

    # build query
    q_objects = Q()
    q_objects &= Q(start_time__gte=date_from)
    q_objects &= Q(start_time__lt=date_to)

    if internal_external:
        q_objects &= Q(internal_external=internal_external)

    # get calls
    calls = Call.objects.filter(q_objects).annotate(date=TruncDay('start_time')).values('date', 'direction').annotate(count=Count('pk')).order_by('date', 'direction')

    # categories are each date
    categories = []
    inbound_data = []
    outbound_data = []

    # loop through results and add relevant data to
    # the correct lists.
    for call in calls:
        str_date = call['date'].strftime(DATE_FORMAT)
        if str_date not in categories:
            categories.append(str_date)

        if call['direction'] == '0':
            inbound_data.append(call['count'])
        else:
            outbound_data.append(call['count'])


    # create series object
    series = [
        {
            'name': 'Inbound',
            'data': inbound_data,
            'color': '#b01658'

        }, 
        {
            'name': 'Outbound',
            'data': outbound_data,
            'color': '#009b87',

        }
    ]

    # create results dict
    results = {
        'categories': categories,
        'series': series,
    }

    #return json
    return HttpResponse(
            json.dumps(results),
            content_type="application/json"
        )


@login_required
def internal_external(request):
    DATE_FORMAT = '%d %b'

    # get form and qs parameters
    form = FilterBarForm(request.GET)
    direction = request.GET.get('direction', None)

    # if form not valid or not valid qs parameters
    if not form.is_valid() or direction not in [None,'0','1']:
        # error with dates so return
        return HttpResponse(
            json.dumps({'error': 'form not valid'}),
            content_type="application/json"
        )
    
    # get dates
    date_from = form.cleaned_data['date_from']
    date_to = form.cleaned_data['date_to'] + timedelta(days=1)

    # build query
    q_objects = Q()
    q_objects &= Q(start_time__gte=date_from)
    q_objects &= Q(start_time__lt=date_to)

    if direction:
        q_objects &= Q(direction=direction)

    # get calls
    calls = Call.objects.filter(q_objects).annotate(date=TruncDay('start_time')).values('date', 'internal_external').annotate(count=Count('pk')).order_by('date', 'direction')

    # categories are each date
    categories = []
    internal_data = []
    external_data = []

    # loop through results and add relevant data to
    # the correct lists.
    for call in calls:
        str_date = call['date'].strftime(DATE_FORMAT)
        if str_date not in categories:
            categories.append(str_date)

        if call['internal_external'] == '0':
            internal_data.append(call['count'])
        else:
            external_data.append(call['count'])


    # create series object
    series = [
        {
            'name': 'Internal',
            'data': internal_data,
            'color': '#ecaa00'

        }, 
        {
            'name': 'External',
            'data': external_data,
            'color': '#003b4b',

        }
    ]

    # create results dict
    results = {
        'categories': categories,
        'series': series,
    }

    #return json
    return HttpResponse(
            json.dumps(results),
            content_type="application/json"
        )
