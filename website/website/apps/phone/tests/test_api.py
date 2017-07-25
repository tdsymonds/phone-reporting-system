# -*- coding: utf-8 -*- 
from datetime import datetime, timedelta
from django.db.models import Avg
from django.urls import reverse
from rest_framework.test import APITestCase
from website.apps.authentication.models import CustomUser

import radar
import random
import string

from ..choices import DIRECTION_CHOICES, INTERNAL_EXTERNAL_CHOICES
from ..models import Call, Department


class APITestCase(APITestCase):
    min_number_of_calls = 100
    max_number_of_calls = 400
    min_call_length = 10
    max_call_length = 1000
    number_of_days = 14
    number_of_departments = 5
    number_of_users = 5

    def setUp(self):
        self.superuser = CustomUser.objects.create_superuser(email='test@test.com', password='testpass')
        self.client.login(username='test@test.com', password='testpass')

        # create a few departments
        for i in range(self.number_of_departments):
            Department.objects.create(department_id=i, name='department: %s' % i)

        # create a few users
        for i in range(self.number_of_users):
            CustomUser.objects.create(
                email = '%s@test.com' % i, 
                department = Department.objects.get(department_id=random.randint(0, self.number_of_departments - 1)),
                first_name = '%s%s' % (i, self._get_random_name()),
                last_name = '%s%s' % (i, self._get_random_name())
            )
    
        # create some calls
        min_number_of_calls = self.min_number_of_calls // 2
        max_number_of_calls = self.max_number_of_calls // 2
        self._create_calls(
            min_number_of_calls = min_number_of_calls, 
            max_number_of_calls = max_number_of_calls
        )

        # change each users department
        for user in self._get_users():
            # get a new random department that's different to the existing one
            new_department = Department.objects.all().exclude(
                pk=user.department.pk).order_by('?').first()
            
            user.department = new_department
            user.save()

        # create some more calls
        self._create_calls(
            min_number_of_calls = min_number_of_calls,
            max_number_of_calls = max_number_of_calls, 
            change_id_by = max_number_of_calls+1
        )

    def _get_users(self):
        return CustomUser.objects.all().exclude(pk=self.superuser.pk)

    def _get_date_from(self, number_of_days):
        return datetime.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            ) - timedelta(days=number_of_days)

    def _get_random_datetime(self):
        return radar.random_datetime(
            start = self._get_date_from(self.number_of_days),
            stop = datetime.now()
        )

    def _get_random_name(self):
        return ''.join(random.choice(string.ascii_uppercase) for _ in range(random.randint(5, 10)))

    def _create_calls(self, min_number_of_calls, max_number_of_calls, change_id_by=0):
        for i in range(random.randint(min_number_of_calls, max_number_of_calls)):
            call_length = random.randint(self.min_call_length, self.max_call_length)
            start_time = self._get_random_datetime()
            user = self._get_users()[random.randint(0, self.number_of_users - 1)]

            Call.objects.create(
                call_id = i + change_id_by,
                user = user,
                department = user.department,
                direction = random.choice(range(2)),
                internal_external = random.choice(range(2)),
                start_time = start_time,
                talk_time_seconds = call_length,
                end_time = start_time + timedelta(seconds=call_length),
            )

    def _get_response(self, url, query_string):
        return self.client.get(reverse(url), query_string)

    def _get_date_range(self, date_from, date_to):
        date_format = '%d/%m/%Y'
        date_from_str = date_from.strftime(date_format)
        date_to_str = date_to.strftime(date_format)
        return '%s - %s' % (date_from_str, date_to_str)

    def _parse_names(self, names):
        direction = None
        internal_external = None
        names_list = names.split('/')

        for choice in DIRECTION_CHOICES:
            if choice[1] == names_list[0]:
                direction = choice[0]
                break

        for choice in INTERNAL_EXTERNAL_CHOICES:
            if choice[1] == names_list[1]:
                internal_external = choice[0]
                break
        
        return direction, internal_external

    def test_api_count(self):
        url = 'phone:count'
        
        # first test for each of the four options with no
        # additional filters.
        for i in range(2):
            for j in range(2):
                response = self._get_response(url, {
                    'direction': i,
                    'internal_external': j
                })

                self.assertEqual(response.status_code, 200)
                db_count = Call.objects.filter(direction=i, internal_external=j).count()
                self.assertEqual(db_count, response.data['count'])

        # try with a random user
        u = self._get_users().order_by('?').first()
        for i in range(2):
            for j in range(2):
                response = self._get_response(url, {
                    'direction': i,
                    'internal_external': j,
                    'filters': [
                        'u%s' % u.pk
                    ]
                })

                self.assertEqual(response.status_code, 200)
                db_count = Call.objects.filter(direction=i, internal_external=j, user=u).count()
                self.assertEqual(db_count, response.data['count'])

        # try with a random department
        d = Department.objects.all().order_by('?').first()
        for i in range(2):
            for j in range(2):
                response = self._get_response(url, {
                    'direction': i,
                    'internal_external': j,
                    'filters': [
                        'd%s' % d.pk
                    ]
                })

                self.assertEqual(response.status_code, 200)
                db_count = Call.objects.filter(direction=i, internal_external=j, department=d).count()
                self.assertEqual(db_count, response.data['count'])

        # try with multiple filters
        d = Department.objects.all().order_by('?').first()
        u = self._get_users().order_by('?').first()
        for i in range(2):
            for j in range(2):
                response = self._get_response(url, {
                    'direction': i,
                    'internal_external': j,
                    'filters': [
                        'd%s' % d.pk,
                        'u%s' % u.pk   
                    ]
                })

                self.assertEqual(response.status_code, 200)
                db_count = Call.objects.filter(direction=i, internal_external=j, department=d, user=u).count()
                self.assertEqual(db_count, response.data['count'])

    def test_api_daily_count(self):
        url = 'phone:daily_count'

        date_range = self._get_date_range(date_from=self._get_date_from(self.number_of_days), date_to=datetime.now())
        
        # first test with all data
        response = self._get_response(url, {
            'date_range': date_range
        })

        self.assertEqual(response.status_code, 200)

        # for each date in the daterange check the totals match up
        for i in range(self.number_of_days):
            date_from = self._get_date_from(number_of_days=i)

            for series in response.data['series']:
                direction, internal_external = self._parse_names(series['name'])

                db_count = Call.objects.filter(
                    start_time__gte=date_from,
                    start_time__lt=date_from + timedelta(days=1),
                    direction=direction, 
                    internal_external=internal_external
                ).count()

                self.assertEqual(db_count, series['data'][-(i+1)])


        # try with a random user
        u = self._get_users().order_by('?').first()
        response = self._get_response(url, {
            'date_range': date_range,
            'filters': [
                'u%s' % u.pk
            ]
        })

        self.assertEqual(response.status_code, 200)

        # for each date in the daterange check the totals match up
        for i in range(self.number_of_days):
            date_from = self._get_date_from(number_of_days=i)

            for series in response.data['series']:
                direction, internal_external = self._parse_names(series['name'])

                db_count = Call.objects.filter(
                    start_time__gte=date_from,
                    start_time__lt=date_from + timedelta(days=1),
                    direction=direction, 
                    internal_external=internal_external,
                    user=u
                ).count()

                self.assertEqual(db_count, series['data'][-(i+1)])


        # try with a random department
        d = Department.objects.all().order_by('?').first()
        response = self._get_response(url, {
            'date_range': date_range,
            'filters': [
                'd%s' % d.pk
            ]
        })

        self.assertEqual(response.status_code, 200)

        # for each date in the daterange check the totals match up
        for i in range(self.number_of_days):
            date_from = self._get_date_from(number_of_days=i)

            for series in response.data['series']:
                direction, internal_external = self._parse_names(series['name'])

                db_count = Call.objects.filter(
                    start_time__gte=date_from,
                    start_time__lt=date_from + timedelta(days=1),
                    direction=direction, 
                    internal_external=internal_external,
                    department=d
                ).count()

                self.assertEqual(db_count, series['data'][-(i+1)]) 


        # try with multiple filters
        d = Department.objects.all().order_by('?').first()
        u = self._get_users().order_by('?').first()
        response = self._get_response(url, {
            'date_range': date_range,
            'filters': [
                'd%s' % d.pk,
                'u%s' % u.pk
            ]
        })

        self.assertEqual(response.status_code, 200)

        # for each date in the daterange check the totals match up
        for i in range(self.number_of_days):
            date_from = self._get_date_from(number_of_days=i)

            for series in response.data['series']:
                direction, internal_external = self._parse_names(series['name'])

                db_count = Call.objects.filter(
                    start_time__gte=date_from,
                    start_time__lt=date_from + timedelta(days=1),
                    direction=direction, 
                    internal_external=internal_external,
                    department=d,
                    user=u
                ).count()

                self.assertEqual(db_count, series['data'][-(i+1)])                

    def test_api_daily_call_time(self):
        url = 'phone:daily_call_time'

        date_range = self._get_date_range(date_from=self._get_date_from(self.number_of_days), date_to=datetime.now())
        
        # first test with all data
        response = self._get_response(url, {
            'date_range': date_range
        })

        self.assertEqual(response.status_code, 200)

        # for each date in the daterange check the totals match up
        for i in range(self.number_of_days):
            date_from = self._get_date_from(number_of_days=i)

            for series in response.data['series']:
                direction, internal_external = self._parse_names(series['name'])

                db_avg = Call.objects.filter(
                    start_time__gte=date_from,
                    start_time__lt=date_from + timedelta(days=1),
                    direction=direction, 
                    internal_external=internal_external
                ).aggregate(avg=Avg('talk_time_seconds'))['avg']

                if not db_avg:
                    db_avg = 0
                        
                self.assertEqual(round(db_avg / 60, 1), series['data'][-(i+1)])


        # try with a random user
        u = self._get_users().order_by('?').first()
        response = self._get_response(url, {
            'date_range': date_range,
            'filters': [
                'u%s' % u.pk
            ]
        })

        self.assertEqual(response.status_code, 200)

        # for each date in the daterange check the totals match up
        for i in range(self.number_of_days):
            date_from = self._get_date_from(number_of_days=i)

            for series in response.data['series']:
                direction, internal_external = self._parse_names(series['name'])

                db_avg = Call.objects.filter(
                    start_time__gte=date_from,
                    start_time__lt=date_from + timedelta(days=1),
                    direction=direction, 
                    internal_external=internal_external,
                    user=u
                ).aggregate(avg=Avg('talk_time_seconds'))['avg']

                if not db_avg:
                    db_avg = 0
                        
                self.assertEqual(round(db_avg / 60, 1), series['data'][-(i+1)])


        # try with a random department
        d = Department.objects.all().order_by('?').first()
        response = self._get_response(url, {
            'date_range': date_range,
            'filters': [
                'd%s' % d.pk
            ]
        })

        self.assertEqual(response.status_code, 200)

        # for each date in the daterange check the totals match up
        for i in range(self.number_of_days):
            date_from = self._get_date_from(number_of_days=i)

            for series in response.data['series']:
                direction, internal_external = self._parse_names(series['name'])

                db_avg = Call.objects.filter(
                    start_time__gte=date_from,
                    start_time__lt=date_from + timedelta(days=1),
                    direction=direction, 
                    internal_external=internal_external,
                    department=d
                ).aggregate(avg=Avg('talk_time_seconds'))['avg']

                if not db_avg:
                    db_avg = 0
                        
                self.assertEqual(round(db_avg / 60, 1), series['data'][-(i+1)]) 


        # try with multiple filters
        d = Department.objects.all().order_by('?').first()
        u = self._get_users().order_by('?').first()
        response = self._get_response(url, {
            'date_range': date_range,
            'filters': [
                'd%s' % d.pk,
                'u%s' % u.pk
            ]
        })

        self.assertEqual(response.status_code, 200)

        # for each date in the daterange check the totals match up
        for i in range(self.number_of_days):
            date_from = self._get_date_from(number_of_days=i)

            for series in response.data['series']:
                direction, internal_external = self._parse_names(series['name'])

                db_avg = Call.objects.filter(
                    start_time__gte=date_from,
                    start_time__lt=date_from + timedelta(days=1),
                    direction=direction, 
                    internal_external=internal_external,
                    department=d,
                    user=u
                ).aggregate(avg=Avg('talk_time_seconds'))['avg']

                if not db_avg:
                    db_avg = 0
                        
                self.assertEqual(round(db_avg / 60, 1), series['data'][-(i+1)])

    def test_api_department(self):
        url = 'phone:department'

        # first test with all data
        response = self._get_response(url, {})
        self.assertEqual(response.status_code, 200)

        for i, department in enumerate(response.data['categories']):
            for series in response.data['series']:
                direction, internal_external = self._parse_names(series['name'])

                db_count = Call.objects.filter(
                    direction=direction, 
                    internal_external=internal_external,
                    department__name=department
                ).count()

                self.assertEqual(db_count, series['data'][i])


        # try with a random user
        u = self._get_users().order_by('?').first()
        response = self._get_response(url, {
            'filters': [
                'u%s' % u.pk
            ]
        })
        self.assertEqual(response.status_code, 200)

        for i, department in enumerate(response.data['categories']):
            for series in response.data['series']:
                direction, internal_external = self._parse_names(series['name'])

                db_count = Call.objects.filter(
                    direction=direction, 
                    internal_external=internal_external,
                    department__name=department,
                    user=u
                ).count()

                self.assertEqual(db_count, series['data'][i])


        # try with a random department
        d = Department.objects.all().order_by('?').first()
        response = self._get_response(url, {
            'filters': [
                'd%s' % d.pk
            ]
        })
        self.assertEqual(response.status_code, 200)

        departments = response.data['categories']
        self.assertEqual(len(departments), 1)

        for series in response.data['series']:
            direction, internal_external = self._parse_names(series['name'])

            db_count = Call.objects.filter(
                direction=direction, 
                internal_external=internal_external,
                department=d
            ).count()

            self.assertEqual(db_count, series['data'][0])
      
    def test_api_donut(self):
        url = 'phone:donut'
        
        # first test with no filters.
        response = self._get_response(url, {})
        self.assertEqual(response.status_code, 200)

        for series in response.data:
            direction, internal_external = self._parse_names(series['name'])

            db_count = Call.objects.filter(
                direction=direction, 
                internal_external=internal_external
            ).count()

            self.assertEqual(db_count, series['y'])

        # try with a random user
        u = self._get_users().order_by('?').first()
        response = self._get_response(url, {
            'filters': [
                'u%s' % u.pk
            ]
        })
        self.assertEqual(response.status_code, 200)

        for series in response.data:
            direction, internal_external = self._parse_names(series['name'])

            db_count = Call.objects.filter(
                direction=direction, 
                internal_external=internal_external,
                user=u
            ).count()

            self.assertEqual(db_count, series['y'])


        # try with a random department
        d = Department.objects.all().order_by('?').first()
        response = self._get_response(url, {
            'filters': [
                'd%s' % d.pk
            ]
        })
        self.assertEqual(response.status_code, 200)

        for series in response.data:
            direction, internal_external = self._parse_names(series['name'])

            db_count = Call.objects.filter(
                direction=direction, 
                internal_external=internal_external,
                department=d
            ).count()

            self.assertEqual(db_count, series['y'])


        # try with multiple filters
        d = Department.objects.all().order_by('?').first()
        u = self._get_users().order_by('?').first()
        response = self._get_response(url, {
            'filters': [
                'd%s' % d.pk,
                'u%s' % u.pk
            ]
        })
        self.assertEqual(response.status_code, 200)

        for series in response.data:
            direction, internal_external = self._parse_names(series['name'])

            db_count = Call.objects.filter(
                direction=direction, 
                internal_external=internal_external,
                department=d,
                user=u
            ).count()

            self.assertEqual(db_count, series['y'])
   
    def test_api_employee(self):
        url = 'phone:employee'

        # first test with all data
        response = self._get_response(url, {})
        self.assertEqual(response.status_code, 200)

        for i, user_fullname in enumerate(response.data['categories']):
            for series in response.data['series']:
                direction, internal_external = self._parse_names(series['name'])
                first_name, last_name = user_fullname.split(' ')

                db_count = Call.objects.filter(
                    direction=direction, 
                    internal_external=internal_external,
                    user__first_name=first_name,
                    user__last_name=last_name
                ).count()

                self.assertEqual(db_count, series['data'][i])

        # try with a random user
        u = self._get_users().order_by('?').first()
        response = self._get_response(url, {
            'filters': [
                'u%s' % u.pk
            ]
        })
        self.assertEqual(response.status_code, 200)

        employee_names = response.data['categories']
        self.assertEqual(len(employee_names), 1)
        self.assertEqual(employee_names[0], u.get_full_name())

        for series in response.data['series']:
            direction, internal_external = self._parse_names(series['name'])
    
            db_count = Call.objects.filter(
                direction=direction, 
                internal_external=internal_external,
                user__first_name=u.first_name,
                user__last_name=u.last_name
            ).count()

            self.assertEqual(db_count, series['data'][0])


        # try with a random department
        d = Department.objects.all().order_by('?').first()
        response = self._get_response(url, {
            'filters': [
                'd%s' % d.pk
            ]
        })
        self.assertEqual(response.status_code, 200)

        for i, user_fullname in enumerate(response.data['categories']):
            for series in response.data['series']:
                direction, internal_external = self._parse_names(series['name'])
                first_name, last_name = user_fullname.split(' ')

                db_count = Call.objects.filter(
                    direction=direction, 
                    internal_external=internal_external,
                    user__first_name=first_name,
                    user__last_name=last_name,
                    department=d
                ).count()

                self.assertEqual(db_count, series['data'][i])
