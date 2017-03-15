# -*- coding: utf-8 -*- 
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey
from uuslug import uuslug

from website.apps.authentication.models import CustomUser

from .choices import DIRECTION_CHOICES, INTERNAL_EXTERNAL_CHOICES


@python_2_unicode_compatible
class Department(MPTTModel):
    # mptt admin does not like when pk is 0, so stopping department_id from
    # being pk
    department_id = models.IntegerField(_('department id'), unique=True)
    name = models.CharField(_('name'), max_length=50)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)
    users = models.ManyToManyField(CustomUser, through='DepartmentUser')
    slug = models.SlugField(_('slug'), max_length=255, blank=True, allow_unicode=True)
    added_manually = models.BooleanField(_('added manually'), default=False, 
        help_text=_('Should be marked true if the department is created manually in the admin'))

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name',]
        verbose_name = _('Department')
        verbose_name_plural = _('Departments')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuslug(self.name, instance=self, start_no=2)
        super(Department, self).save(*args, **kwargs)


@python_2_unicode_compatible
class DepartmentUser(models.Model):
    user = models.ForeignKey(CustomUser)
    department = models.ForeignKey(Department)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    date_left = models.DateTimeField(_('date left'), blank=True, null=True)
    view_full_department = models.BooleanField(_('view full department'), default=False)
    view_child_departments = models.BooleanField(_('view child departments'), default=False)

    def __str__(self):
        return '%s: %s' % (self.user.get_full_name(), self.department.name) 

    class Meta:
        verbose_name = _('Department User')
        verbose_name_plural = _('Department Users')


@python_2_unicode_compatible
class Call(models.Model):
    user = models.ForeignKey(CustomUser)
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
