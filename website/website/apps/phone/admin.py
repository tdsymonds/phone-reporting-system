# -*- coding: utf-8 -*- 
from django.contrib import admin

from .models import Call, Chart, Department, Page, Row, RowChart


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    pass


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
