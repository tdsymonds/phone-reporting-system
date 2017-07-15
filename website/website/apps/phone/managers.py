# -*- coding: utf-8 -*-
from django.db import models
from mptt.managers import TreeQuerySet


class DepartmentQuerySet(TreeQuerySet):
    def viewable_by(self, user):
        return self.filter(
            departmentuser__view_full_department=True, 
            departmentuser__user=user
        ).filter(
            departmentuser__view_child_departments=True, 
            departmentuser__user=user
        ).get_descendants(include_self=True)


class DepartmentManager(models.Manager):
    def get_queryset(self):
        return DepartmentQuerySet(self.model, using=self._db)

    def viewable_by(self, user):
        return self.get_queryset().viewable_by(user)
