# -*- coding: utf-8 -*-
from datetime import datetime, timedelta 
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import lazy
from django.utils.translation import ugettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey
from uuslug import uuslug

from website.apps.authentication.models import CustomUser

from .choices import (CHART_TYPE_CHOICES, CHART_URL_CHOICES, 
    DIRECTION_CHOICES, INTERNAL_EXTERNAL_CHOICES, NUMBER_OF_CHART_CHOICES)


@python_2_unicode_compatible
class Department(models.Model):
    department_id = models.IntegerField(_('department id'), unique=True)
    name = models.CharField(_('name'), max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name',]
        verbose_name = _('Department')
        verbose_name_plural = _('Departments')

    def get_users(self):
        return self.users.all()


@python_2_unicode_compatible
class Call(models.Model):
    call_id = models.IntegerField(_('call id'), primary_key=True)
    user = models.ForeignKey(CustomUser)
    department = models.ForeignKey(Department)
    direction = models.CharField(_('direction'), max_length=1, choices=DIRECTION_CHOICES)
    internal_external = models.CharField(_('internal external'), max_length=1, choices=INTERNAL_EXTERNAL_CHOICES)
    start_time = models.DateTimeField(_('start time'))
    end_time = models.DateTimeField(_('end time'))
    talk_time_seconds = models.IntegerField(_('talk time seconds'))

    def __str__(self):
        return '%s: %s' % (self.user.get_full_name(), self.start_time.strftime('%d %b, %Y, %H:%M:%S'))

    class Meta:
        ordering = ['start_time', 'user',]
        verbose_name = _('Call')
        verbose_name_plural = _('Calls')


@python_2_unicode_compatible
class Page(models.Model):
    name = models.CharField(_('name'), max_length=100)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Row(models.Model):
    name = models.CharField(_('name'), max_length=100, help_text=_('For admin reference purposes'))
    page = models.ForeignKey(Page, blank=True, null=True)
    number_of_charts = models.CharField(_('number of charts'), max_length=1, choices=NUMBER_OF_CHART_CHOICES)
    position = models.SmallIntegerField(default=0)

    def __str__(self):
        return '%s: %s' %  (self.page, self.name)

    class Meta:
        ordering = ['page', 'position',]

    def get_bootstrap_col_classes(self):
        if self.number_of_charts == '1':
            return 'col-sm-12'
        elif self.number_of_charts == '2':
            return 'col-sm-12 col-lg-6'
        elif self.number_of_charts == '4':
            return 'col-xs-12 col-sm-6 col-lg-3'
        return ''


@python_2_unicode_compatible
class Chart(models.Model):
    name = models.CharField(_('name'), max_length=100, help_text=_('For admin reference purposes'))
    title = models.CharField(_('title'), max_length=100) 
    url = models.CharField(_('url'), max_length=100, choices=CHART_URL_CHOICES)
    query_string = models.CharField(_('query string'), max_length=200, blank=True, null=True)
    chart_type = models.CharField(_('chart type'), max_length=50, choices=CHART_TYPE_CHOICES)
    rows = models.ManyToManyField(Row, through='RowChart', blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Chart')
        verbose_name_plural = _('Charts')

    def get_url(self):
        return reverse('phone:%s' % self.url)


@python_2_unicode_compatible
class RowChart(models.Model):
    row = models.ForeignKey(Row)
    chart = models.ForeignKey(Chart)
    position = models.SmallIntegerField(default=0)

    class Meta:
        ordering = ['position',]
