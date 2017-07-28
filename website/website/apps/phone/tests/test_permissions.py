# -*- coding: utf-8 -*- 
from django.urls import reverse
from rest_framework.test import APITestCase
from website.apps.authentication.models import CustomUser

import random
import string

from ..models import Department


class APITestCase(APITestCase):
    test_user = None
    urls = [
        'phone:count',
        'phone:daily_count',
        'phone:daily_call_time',
        'phone:department',
        'phone:donut',
        'phone:employee',
    ]

    def setUp(self):
        # create a two departments
        d1 = Department.objects.create(department_id=1, name='department: %s' % 1)
        d2 = Department.objects.create(department_id=2, name='department: %s' % 2)
            
        # create test user, assign to the first department and login
        self.test_user = CustomUser.objects.create_superuser(
            email='test@test.com', 
            password='testpass', 
            department=d1
        )
        self.client.login(username='test@test.com', password='testpass')
        # disable being a superuser, as superuser can see all
        self.test_user.is_superuser = False
        self.test_user.save()

        # create a few users assigning half to each department
        for i in range(10):
            CustomUser.objects.create(
                email = '%s@test.com' % i, 
                department = Department.objects.get(department_id=(i % 2)+1)
            )

    def _get_response(self, url, query_string):
        return self.client.get(reverse(url), query_string)

    def test_user_with_no_permisisons(self):
        # user can view all urls with no filters
        for url in self.urls:
            response = self._get_response(url, {})
            self.assertEqual(response.status_code, 200)

        # user cannot filter on any employees
        for url in self.urls:
            user = CustomUser.objects.all().exclude(pk=self.test_user.pk).order_by('?').first()
            response = self._get_response(url, {
                'filters': [
                    'u%s' % user.pk
                ]
            })
            self.assertEqual(response.status_code, 400)

    def test_user_with_permissions(self):
        # let user view department 1 only
        self.test_user.departments_can_view.add(Department.objects.get(department_id=1))
        self.test_user.save()

        # user can view all urls with no filters
        for url in self.urls:
            response = self._get_response(url, {})
            self.assertEqual(response.status_code, 200)

        # user cannot filter on any employees in department 2
        for url in self.urls:
            user = CustomUser.objects.filter(department__department_id=2).order_by('?').first()
            response = self._get_response(url, {
                'filters': [
                    'u%s' % user.pk
                ]
            })
            self.assertEqual(response.status_code, 400)

        # however the user can filter on users in department 1
        for url in self.urls:
            user = CustomUser.objects.filter(department__department_id=1).exclude(pk=self.test_user.pk).order_by('?').first()
            response = self._get_response(url, {
                'filters': [
                    'u%s' % user.pk
                ]
            })
            self.assertEqual(response.status_code, 200)
