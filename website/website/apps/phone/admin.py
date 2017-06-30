# -*- coding: utf-8 -*- 
from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin

from .models import Call, Chart, Department, DepartmentUser, Page, Row, RowChart


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


class RowInline(admin.StackedInline):
    model = Row
    extra = 0


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    inlines = (RowInline,)


class RowChartInline(admin.StackedInline):
    model = RowChart
    extra = 0


@admin.register(Row)
class Row(admin.ModelAdmin):
    inlines = (RowChartInline,)


@admin.register(RowChart)
class RowChartAdmin(admin.ModelAdmin):
    pass


@admin.register(Chart)
class ChartAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'url',)
