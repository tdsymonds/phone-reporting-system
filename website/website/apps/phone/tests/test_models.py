# -*- coding: utf-8 -*- 
from datetime import datetime
from django.test import TestCase
from website.apps.authentication.models import CustomUser

from ..models import Department, DepartmentUser


class DepartmentTestCase(TestCase):
    def setUp(self):
        # create sample data
        for i in range(10):
            Department.objects.create(department_id=i, name=str(i))

    def test_department_hierarchy(self):
        # get three departments        
        d0 = Department.objects.get(department_id='0')
        d1 = Department.objects.get(department_id='1')
        d2 = Department.objects.get(department_id='2')

        # create hierarchy d0 -> d1 -> d2
        d1.parent = d0
        d1.save()
        d2.parent = d1
        d2.save()

        # are d1 and d2 both descendants of d0?
        self.assertTrue(d1 in d0.get_descendants())
        self.assertTrue(d2 in d0.get_descendants())

        # d1 is a child, d2 is not (it's a grandchild)
        self.assertTrue(d1 in d0.get_children())
        self.assertFalse(d2 in d0.get_children())

        # is d2 a descendent of d1
        self.assertTrue(d2 in d1.get_descendants())

        # it's also a child
        self.assertTrue(d2 in d1.get_children())

        # is d2 a leaf node - i.e. has no children
        self.assertTrue(d2.is_leaf_node())


class DepartmentUserTestCase(TestCase):
    def setUp(self):
        # create two departments
        for i in range(2):
            Department.objects.create(department_id=i, name=str(i))

        # create one user
        u = CustomUser.objects.create(email='test@test.com')

        # create user department with user and first department
        DepartmentUser.objects.create(department=Department.objects.get(department_id='0'), user=u)

    def test_changing_depatment(self):
        # get user and departments
        d0 = Department.objects.get(department_id='0')
        d1 = Department.objects.get(department_id='1')        
        u = CustomUser.objects.get(email='test@test.com')

        # only will be one active department user per user, so can get first
        du = DepartmentUser.objects.filter(date_left__isnull=True, user=u).first()

        # is the new department different to the current?
        if d1 != du.department:
            # set the existing department user as left
            du.date_left = datetime.now()
            du.save()
            # add the new department
            du2 = DepartmentUser.objects.create(department=d1, user=u)
            du2.save()

        # the user has now changed department
        active_du = DepartmentUser.objects.filter(date_left__isnull=True, user=u).first()
        d1_du = DepartmentUser.objects.filter(department=d1, user=u).first()

        # the active department and d1's du are equal
        self.assertEqual(active_du, d1_du)

        # the user now has two department users
        u_dus = DepartmentUser.objects.filter(user=u)
        self.assertTrue(u_dus.count() == 2)
