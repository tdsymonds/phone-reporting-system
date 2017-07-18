# -*- coding: utf-8 -*- 
from datetime import datetime, timedelta
from django.urls import reverse
from rest_framework.test import APITestCase
from website.apps.authentication.models import CustomUser

import radar
import random

from ..models import Call, Department


class APITestCase(APITestCase):
    number_of_departments = 3
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
                department = Department.objects.get(department_id=random.randint(0, self.number_of_departments - 1))
            )
    
        # create some calls
        max_number_of_calls = 200
        self._create_calls(max_number_of_calls)

        # change each users department
        for user in self._get_users():
            # get a new random department that's different to the existing one
            new_department = Department.objects.all().exclude(
                pk=user.department.pk).order_by('?').first()
            
            user.department = new_department
            user.save()

        # create some more calls
        self._create_calls(
            max_number_of_calls=max_number_of_calls, 
            change_id_by=max_number_of_calls+1
        )

    def _get_users(self):
        return CustomUser.objects.all().exclude(pk=self.superuser.pk)

    def _get_random_datetime(self):
        return radar.random_datetime(
            start = datetime.now() - timedelta(days=60),
            stop = datetime.now()
        )

    def _create_calls(self, max_number_of_calls, change_id_by=0):
        for i in range(random.randint(50, max_number_of_calls)):
            call_length = random.randint(10, 1000)
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

    def test_api_count(self):
        url = 'phone:count'
        
        # first test for each of the four options with no
        # additional filters.
        for i in range(2):
            for j in range(2):
                response = self._get_response('phone:count', {
                    'direction': i,
                    'internal_external': j
                })

                db_count = Call.objects.filter(direction=i, internal_external=j).count()
                self.assertEqual(db_count, response.data['count'])

        # try with a random user
        u = self._get_users().order_by('?').first()
        for i in range(2):
            for j in range(2):
                response = self._get_response('phone:count', {
                    'direction': i,
                    'internal_external': j,
                    'filters': [
                        'u%s' % u.pk
                    ]
                })

                db_count = Call.objects.filter(direction=i, internal_external=j, user=u).count()
                self.assertEqual(db_count, response.data['count'])

        # try with a random department
        d = Department.objects.all().order_by('?').first()
        for i in range(2):
            for j in range(2):
                print (d, i, j)

                response = self._get_response('phone:count', {
                    'direction': i,
                    'internal_external': j,
                    'filters': [
                        'd%s' % d.pk
                    ]
                })

                db_count = Call.objects.filter(direction=i, internal_external=j, user=u).count()
                self.assertEqual(db_count, response.data['count'])

