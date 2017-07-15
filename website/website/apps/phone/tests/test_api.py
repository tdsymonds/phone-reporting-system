# -*- coding: utf-8 -*- 
from datetime import datetime, timedelta
from django.urls import reverse
from rest_framework.test import APITestCase
from website.apps.authentication.models import CustomUser

import radar
import random

from ..models import Call, Department, DepartmentUser


class APITestCase(APITestCase):
    number_of_departments = 3
    number_of_users = 5

    def setUp(self):
        self.superuser = CustomUser.objects.create_superuser(email='test@test.com', password='testpass')
        self.client.login(username='test@test.com', password='testpass')

        # create a few users
        for i in range(self.number_of_users):
            CustomUser.objects.create(email='%s@test.com' % i)
    
        # create a few departments
        for i in range(self.number_of_departments):
            Department.objects.create(department_id=i, name='department: %s' % i)

        # assign the users to the departments
        for user in CustomUser.objects.all():
            # get a random department
            department = Department.objects.get(department_id=random.randint(0, self.number_of_departments - 1))
            # and add the user to that department
            DepartmentUser.objects.create(department=department, user=user)

        # create some calls
        max_number_of_calls = 200
        self._create_calls(max_number_of_calls)

        # change each users department
        for user in CustomUser.objects.all():
            # only will be one active department user per user, so can get first
            department_user = DepartmentUser.objects.filter(date_left__isnull=True, user=user).first()
            # set the current department user as left
            department_user.date_left = datetime.now()
            department_user.save()
            # get a new random department that's different to the existing one
            new_department = Department.objects.all().exclude(
                pk=department_user.department.pk).order_by('?').first()
            # create a new department user
            DepartmentUser.objects.create(department=new_department, user=user)

        # create some more calls
        self._create_calls(
            max_number_of_calls=max_number_of_calls, 
            change_id_by=max_number_of_calls+1
        )

    def _get_random_datetime(self):
        return radar.random_datetime(
            start = datetime.now() - timedelta(days=60),
            stop = datetime.now()
        )

    def _create_calls(self, max_number_of_calls, change_id_by=0):
        for i in range(random.randint(50, max_number_of_calls)):
            call_length = random.randint(10, 1000)
            start_time = self._get_random_datetime()

            Call.objects.create(
                call_id = i + change_id_by,
                user = CustomUser.objects.all()[random.randint(0, self.number_of_users - 1)],
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
        
        for i in range(2):
            for j in range(2):
                response = self._get_response('phone:count', {
                    'direction': i,
                    'internal_external': j
                })

                db_count = Call.objects.filter(direction=i, internal_external=j).count()

                self.assertEqual(db_count, response.data['count'])