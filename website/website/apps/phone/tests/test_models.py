# -*- coding: utf-8 -*- 
from django.test import TestCase

from ..models import Department


class DepartmentTestCase(TestCase):
    def setUp(self):
        for i in range(10):
            Department.objects.create(department_id=i, name=str(i))

    def test_department_hierarchy(self):
        # get two departments        
        d0 = Department.objects.get(department_id='0')
        d1 = Department.objects.get(department_id='1')
        d2 = Department.objects.get(department_id='2')

        # create heirachy d0 -> d1 -> d2
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
