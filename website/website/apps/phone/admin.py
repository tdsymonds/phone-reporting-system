# -*- coding: utf-8 -*- 
from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin

from .models import Call, Department, DepartmentUser


class DepartmentUserInline(admin.StackedInline):
    model = DepartmentUser
    readonly_fields = ('date_joined', )
    extra = 0


@admin.register(Department)
class DepartmentAdmin(DraggableMPTTAdmin):
    list_display = ('tree_actions', 'indented_title', )
    list_display_links = ('indented_title', )
    inlines = (DepartmentUserInline,)


@admin.register(Call)
class CallAdmin(admin.ModelAdmin):
    pass
