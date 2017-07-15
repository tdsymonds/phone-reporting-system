# -*- coding: utf-8 -*- 
from datetime import datetime, timedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Count, IntegerField, OuterRef, Q, Subquery, Sum, Value as V
from django.db.models.functions import Concat, TruncDay
from django.http import HttpResponse
from django.views.generic import TemplateView
from rest_framework.response import Response
from rest_framework.views import APIView

import json

from .choices import DIRECTION_CHOICES, INTERNAL_EXTERNAL_CHOICES
from .forms import FilterBarForm, FullFilterBarForm
from .models import Call, Chart, DepartmentUser, Page
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
        context['form'] = FullFilterBarForm(request=self.request)
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

        return FullFilterBarForm(self.request.GET, request=self.request)

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

    def _get_colour(self, direction, internal_external):
        if int(direction) == 0 and int(internal_external) == 0:
            return '#b01658'
        elif int(direction) == 0 and int(internal_external) == 1:
            return '#009b87'
        elif int(direction) == 1 and int(internal_external) == 0:
            return '#ecaa00'
        else:
            return '#003b4b'

    def _get_names(self, direction, internal_external):
        name = ''

        for choice in DIRECTION_CHOICES:
            if choice[0] == int(direction):
                name += choice[1]
                break

        for choice in INTERNAL_EXTERNAL_CHOICES:
            if choice[0] == int(internal_external):
                name += '/%s' % choice[1]
                break

        return name

    def _get_call_q_objects(self):
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
                    q_department_filter_objects |= Q(user__department__pk=flter[1:])

            q_objects &= q_user_filter_objects
            q_objects &= q_department_filter_objects
        
        return q_objects

    def _get_calls(self):
        return Call.objects.filter(self._get_call_q_objects()).annotate(
                date=TruncDay('start_time')
            ).order_by('date')

    def _get_daily_call_counts(self):
        calls = self._get_calls()
        return calls.values(
                'date', 'direction', 'internal_external'
            ).annotate(
                value=Count('pk')
            ).order_by('date', 'direction', 'internal_external')

    def _get_daily_call_time(self):
        calls = self._get_calls()
        return calls.values(
                'date', 'direction', 'internal_external'
            ).annotate(
                value=Avg('talk_time_seconds')
            ).order_by('date', 'direction', 'internal_external')        

    def _get_donut_calls(self):
        self._validate_form()
        
        calls = self._get_calls()
        calls = calls.values('internal_external', 'direction').annotate(
            count=Count('pk')).order_by('internal_external', 'direction')

        results = []

        for result in calls:
            results.append({
                'name': self._get_names(result['direction'], result['internal_external']),
                'y': result['count'],
                'color': self._get_colour(result['direction'], result['internal_external']),
            })

        return results

    def _get_daily_series(self, queryset, query_type=None):
        # categories are each date
        categories = []

        # define two by two matrix for internal/external/inbound/outbound
        # these are defined nicely by the 0/1 values which means can index
        # matrix appropriately.
        data_lists = [[[],[]] for x in range(2)]
        data_results = [[{},{}] for x in range(2)]

        dict_date_format = '%d %b %y'

        # loop through data to get into format for date loop
        # todo: surely there's a more efficient way to
        # to this and avoid the unnecessary double loop.
        for call in queryset:
            call_date = datetime.strftime(call['date'], dict_date_format)
            direction = int(call['direction'])
            internal_external = int(call['internal_external'])

            # if its an average call change to the minutes and round appropriately
            value = call['value']
            if query_type == 'seconds':
                value = round(value / 60, 1)

            data_results[direction][internal_external][call_date] = value

        # loop through each date between the date form to date
        # to, so dates with no records will still show as zero
        date_from, date_to = self.form.cleaned_data['date_range']
        for day in datetimeRange(date_from, date_to):
            day_str = datetime.strftime(day, dict_date_format)
            categories.append(day_str)

            # loop through each of the data types
            for i in range(2):
                for j in range(2):
                    data_lists[i][j].append(data_results[i][j].get(day_str, 0))

        # loop through each of the data types in the matrix 
        # and append to the series
        series = []
        for i in range(2):
            for j in range(2):
                series.append({
                    'name': self._get_names(i,j),
                    'data': data_lists[i][j],
                    'color': self._get_colour(i,j),
                })

        return categories, series


class DailyCountView(BaseAPIView):
    def get(self, request, format=None):
        self._validate_form()

        calls = self._get_daily_call_counts()
        categories, series = self._get_daily_series(calls)

        return Response({
            'categories': categories,
            'series': series,
        })


class DailyCallTimeView(BaseAPIView):
    def get(self, request, format=None):
        self._validate_form()

        calls = self._get_daily_call_time()
        categories, series = self._get_daily_series(queryset=calls, query_type='seconds')

        return Response({
            'categories': categories,
            'series': series,
        })


class DonutView(BaseAPIView):
    def get(self, request, format=None):
        results = self._get_donut_calls()
        return Response(results)


class CountView(BaseAPIView):
    def get(self, request, format=None):
        self._validate_form()

        queryset = self._get_calls()

        direction = request.GET.get('direction')
        internal_external = request.GET.get('internal_external')

        if direction:
            queryset = queryset.filter(direction=direction)

        if internal_external:
            queryset = queryset.filter(internal_external=internal_external)    

        return Response({
            'count': queryset.count(),
            'colour': self._get_colour(direction, internal_external),
        })


class DepartmentView(BaseAPIView):
    def get(self, request, format=None):
        self._validate_form()

        q_objects = self._get_call_q_objects()
        q_objects &= Q(
            Q(user__departmentuser__pk=OuterRef('pk')) &
            Q(start_time__gte=OuterRef('date_joined')) &
            Q(start_time__lt=OuterRef('_date_left'))
        )

        queryset = DepartmentUser.objects.all().values('department__name').annotate(
            ii_count=Sum(Subquery(
                Call.objects.filter(
                        q_objects & 
                        Q(
                            Q(internal_external=0) &
                            Q(direction=0)
                        )
                    ).values(
                        'user__departmentuser__pk'
                    ).annotate(
                        count=Count('pk')
                    ).order_by('user__departmentuser__pk').values('count'),
                output_field=IntegerField()
            )),
            io_count=Sum(Subquery(
                Call.objects.filter(
                        q_objects & 
                        Q(
                            Q(internal_external=0) &
                            Q(direction=1)
                        )
                    ).values(
                        'user__departmentuser__pk'
                    ).annotate(
                        count=Count('pk')
                    ).order_by('user__departmentuser__pk').values('count'),
                output_field=IntegerField()
            )),
            ei_count=Sum(Subquery(
                Call.objects.filter(
                        q_objects & 
                        Q(
                            Q(internal_external=1) &
                            Q(direction=0)
                        )
                    ).values(
                        'user__departmentuser__pk'
                    ).annotate(
                        count=Count('pk')
                    ).order_by('user__departmentuser__pk').values('count'),
                output_field=IntegerField()
            )),
            eo_count=Sum(Subquery(
                Call.objects.filter(
                        q_objects & 
                        Q(
                            Q(internal_external=1) &
                            Q(direction=1)
                        )
                    ).values(
                        'user__departmentuser__pk'
                    ).annotate(
                        count=Count('pk')
                    ).order_by('user__departmentuser__pk').values('count'),
                output_field=IntegerField()
            ))

        ).order_by('department__name')

        # only include departments where there have been some calls made
        q_exclude_objects = Q(
            Q(ii_count__isnull=True) &
            Q(io_count__isnull=True) &
            Q(ei_count__isnull=True) &
            Q(eo_count__isnull=True)
        )
        queryset = queryset.exclude(q_exclude_objects)

        categories = queryset.values_list('department__name', flat=True)
        series = [
            {
                'name': self._get_names(0, 0),
                'color': self._get_colour(0, 0),
                'data': queryset.values_list('ii_count', flat=True)
            },
            {
                'name': self._get_names(0, 1),
                'color': self._get_colour(0, 1),
                'data': queryset.values_list('io_count', flat=True)
            },
            {
                'name': self._get_names(1, 0),
                'color': self._get_colour(1, 0),
                'data': queryset.values_list('ei_count', flat=True)
            },
            {
                'name': self._get_names(1, 1),
                'color': self._get_colour(1, 1),
                'data': queryset.values_list('eo_count', flat=True)
            }
        ]

        return Response({
            'categories': categories,
            'series': series,
        })


class EmployeeView(BaseAPIView):
    def get(self, request, format=None):
        self._validate_form()

        # get limit
        limit = request.GET.get('top', None)
        if limit:
            limit = int(limit)
        else:
            limit = 20

        # get broken down calls by direction internal/external
        queryset = self._get_calls()
        queryset = queryset.values(
                'user__pk',
                'internal_external', 
                'direction'
            ).annotate(
                count=Count('pk'),
            ).order_by('user__pk')

        # get the queryset with the total count as this is needed for ordering
        total_queryset = self._get_calls()
        total_queryset = total_queryset.annotate(
                full_name=Concat('user__first_name', V(' '), 'user__last_name')
            ).values(
                'user__pk',
                'full_name',
            ).annotate(
                count=Count('pk'),
            ).order_by('-count')

        # need to get the pks in a list so can determine position in custom order
        sorted_pks = list(total_queryset.values_list('user__pk', flat=True))
        number_of_people = len(sorted_pks)

        # create a count matrix for the different call types
        call_type_matrix = [[[0] * number_of_people for x in range(2)] for y in range(2)]

        for result in queryset:
            # which call type list
            target_list = call_type_matrix[int(result['direction'])][int(result['internal_external'])]
            # which count to change in the list is based on the total queryset position 
            position = sorted_pks.index(result['user__pk'])
            target_list[position] = result['count']


        # the categories is from the total queryset as is ordered correctly
        categories = total_queryset.values_list('full_name', flat=True)[:limit]
        # the series is calculated from the call type matrix
        series = []
        for i in range(2):
            for j in range(2):
                series.append(
                    {
                        'name': self._get_names(i,j),
                        'color': self._get_colour(i,j),
                        'data': call_type_matrix[i][j][:limit]
                    }
                )

        return Response({
            'categories': categories,
            'series': series,
        })