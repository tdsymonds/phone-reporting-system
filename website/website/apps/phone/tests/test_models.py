# -*- coding: utf-8 -*- 
from datetime import datetime
from django.test import TestCase
from website.apps.authentication.models import CustomUser

from ..models import Department


class DepartmentTestCase(TestCase):
    def setUp(self):
        pass
        # create sample data
        # for i in range(10):
        #     Department.objects.create(department_id=i, name=str(i))

    # TODO: