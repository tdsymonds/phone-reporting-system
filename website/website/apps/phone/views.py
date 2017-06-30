# -*- coding: utf-8 -*- 
from datetime import datetime, timedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncDay
from django.http import HttpResponse
from django.views.generic import TemplateView
from rest_framework.response import Response
from rest_framework.views import APIView

import json

from .choices import DIRECTION_CHOICES, INTERNAL_EXTERNAL_CHOICES
from .forms import FilterBarForm, FullFilterBarForm
from .models import Call, Chart, Page
from .utils import datetimeRange


class MyCallView(LoginRequiredMixin, TemplateView):
    template_name = 'phone/pages/_my_calls.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = FilterBarForm()
        context['only_me'] = True
        context['page'] = Page.objects.filter(name__icontains='my calls').first()
        return context


class AllCallView(LoginRequiredMixin, TemplateView):
    template_name = 'phone/pages/_all_calls.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = FullFilterBarForm()
        context['only_me'] = False
        context['page'] = Page.objects.filter(name__icontains='all calls').first()
        return context


class BaseAPIView(LoginRequiredMixin, APIView):
    date_format = '%d %b'
    direction = None
    internal_external = None
    form = None
    only_me = False

    def dispatch(self, request, *args, **kwargs):
        self.form = self._get_form()
        self._set_extra_query_params()
        return super().dispatch(request, *args, **kwargs)

    def _get_form(self):
        only_me = self.request.GET.get('only_me', False)
        if only_me == 'True':
            self.only_me = True
            return FilterBarForm(self.request.GET)

        # todo: return a different form for different views
        # for now just return the same form
        return FullFilterBarForm(self.request.GET)

    def _set_extra_query_params(self):
        internal_external = self.request.GET.get('internal_external', None)
        direction = self.request.GET.get('direction', None)

        valid_list = [None,'0','1']

        if internal_external not in valid_list or direction not in valid_list:
            self._return_error('form is not valid')
        
        self.internal_external = internal_external
        self.direction = direction

    def _validate_form(self):
        if not self.form.is_valid():
            self._return_error('form is not valid')

    def _return_error(self, msg):
        return Response({
            'error': msg
        })

    def _get_colour(self, call_info, value):
        if call_info == 'direction' and value == 0:
            return '#b01658'
        elif call_info == 'direction' and value == 1:
            return '#009b87'
        elif call_info == 'internal_external' and value == 0:
            return '#ecaa00'
        else:
            return '#003b4b'

    def _get_names(self, call_info, value):
        if call_info == 'direction':
            choices = DIRECTION_CHOICES
        else:
            choices = INTERNAL_EXTERNAL_CHOICES

        for choice in choices:
            if choice[0] == value:
                return choice[1]

        return None

    def _get_calls(self):
        date_from, date_to = self.form.cleaned_data['date_range']

        q_objects = Q()

        if date_from:
            q_objects &= Q(start_time__gte=date_from)

        if date_to:
            q_objects &= Q(start_time__lt=date_to + timedelta(days=1))

        if self.internal_external:
            q_objects &= Q(internal_external=self.internal_external)

        if self.direction:
            q_objects &= Q(direction=self.direction)

        if self.only_me:
            q_objects &= Q(user=self.request.user)

        if type(self.form) == FullFilterBarForm:
            q_user_filter_objects = Q()
            q_department_filter_objects = Q()

            for flter in self.form.cleaned_data['filters']:
                if flter[0] == 'u':
                    q_user_filter_objects |= Q(user__pk=flter[1:])
                elif flter[0] == 'd':
                    q_user_filter_objects |= Q(user__department__pk=flter[1:])

            q_objects &= q_user_filter_objects
            q_objects &= q_department_filter_objects

        return Call.objects.filter(q_objects).annotate(
                date=TruncDay('start_time')
            ).order_by('date')

    def _get_call_counts(self, call_info):
        calls = self._get_calls()
        return calls.values(
                'date', call_info
            ).annotate(
                count=Count('pk')
            ).order_by('date', call_info)
        
    def _get_categorised_calls(self, call_info):
        self._validate_form()

        # get calls
        calls = self._get_call_counts(call_info)

        # categories are each date
        categories = []
        data_0 = []
        data_1 = []

        data_0_results = {}
        data_1_results = {}
        dict_date_format = '%d %b %y'

        # loop through data to get into format for date loop
        # todo: surely there's a more efficient way to
        # to this and avoid the unnecessary double loop.
        for call in calls:
            call_date = datetime.strftime(call['date'], dict_date_format)
            
            if call[call_info] == '0':
                data_0_results[call_date] = data_0_results.get(call_date, 0) + call['count']
            else:
                data_1_results[call_date] = data_1_results.get(call_date, 0) + call['count']

        # loop through each date between the date form to date
        # to, so dates with no records will still show as zero
        date_from, date_to = self.form.cleaned_data['date_range']
        for day in datetimeRange(date_from, date_to):
            day_str = datetime.strftime(day, dict_date_format)
            categories.append(day_str)
            data_0.append(data_0_results.get(day_str, 0))
            data_1.append(data_1_results.get(day_str, 0))

        return categories, data_0, data_1

    def _get_donut_calls(self, call_info):
        self._validate_form()
        calls = self._get_calls()
        results = []

        for result in calls.values(call_info).annotate(count=Count('pk')).order_by(call_info):
            results.append({
                'name': self._get_names(call_info, int(result[call_info])),
                'y': result['count'],
                'color': self._get_colour(call_info, int(result[call_info])),
            })

        return results


class DirectionView(BaseAPIView):
    def get(self, request, format=None):
        # get categorised calls
        categories, inbound_data, outbound_data = self._get_categorised_calls('direction')

        # create series object
        series = [
            {
                'name': 'Inbound',
                'data': inbound_data,
                'color': self._get_colour('direction', 0),

            }, 
            {
                'name': 'Outbound',
                'data': outbound_data,
                'color': self._get_colour('direction', 1),
            }
        ]

        return Response({
            'categories': categories,
            'series': series,
        })


class InternalExternalView(BaseAPIView):
    def get(self, request, format=None):
        # get categorised calls
        categories, internal_data, external_data = self._get_categorised_calls('internal_external')

        # create series object
        series = [
            {
                'name': 'Internal',
                'data': internal_data,
                'color': self._get_colour('internal_external', 0),

            }, 
            {
                'name': 'External',
                'data': external_data,
                'color': self._get_colour('internal_external', 1),

            }
        ]

        return Response({
            'categories': categories,
            'series': series,
        })


class DonutView(BaseAPIView):
    def get(self, request, format=None):
        results = self._get_donut_calls(request.GET.get('type'))
        return Response(results)
