# -*- coding: utf-8 -*- 
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.http import urlquote
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from uuslug import uuslug

from .managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    A fully featured User model with admin-compliant permissions that uses
    a full-length email field as the username.

    Email and password are required. Other fields are optional.
    """
    email = models.EmailField(_('email address'), max_length=254, unique=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    company_position = models.CharField(_('company position'), max_length=100, blank=True, null=True)
    image = models.ImageField(_('image'), upload_to='images/users/', blank=True, null=True)
    is_staff = models.BooleanField(_('staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin '
                    'site.'))
    is_active = models.BooleanField(_('active'), default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    slug = models.SlugField(_('slug'), max_length=255, blank=True, allow_unicode=True)

    phone_id = models.IntegerField(_('phone id'), blank=True, null=True, unique=True)
    phone_extension = models.CharField(_('phone extension'), max_length=20, blank=True, null=True, unique=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuslug(self.get_full_name(), instance=self, start_no=2)
        super(CustomUser, self).save(*args, **kwargs)

    def clean(self):
        """
        Either all the requirement phone fields should be
        entered or none of the fields (indicating that they're
        not a phone user)
        """
        phone_fields = [self.phone_id, self.phone_extension]
        all_none = phone_fields.count(None) == len(phone_fields)
        all_entered = all(phone_fields)

        if not (all_none or all_entered):
            raise ValidationError(_('Please either enter all of the phone fields or none of them'))


    def get_absolute_url(self):
        return "/users/%s/" % urlquote(self.email)

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email])

    def get_departments(self):
        """
        Returns a list of departments accessible to this user.
        """
        department_list = []
        for department_user in self.departmentuser_set.all():
            # if the user can view full department, append the department
            if department_user.view_full_department:
                department_list.append(department_user.department)

            # if the user can view child departments, merge these with the list
            if department_user.view_child_departments:
                department_list += list(department_user.department.get_descendants())

        return sorted(department_list, key=lambda x:x.name)

    def get_users(self):
        """
        Returns a list of users accessible to this user.
        """
        user_list = []
        departments = self.get_departments()
        for department in departments:
            user_list += list(department.get_users())

        # remove duplicates
        user_list = list(set(user_list))            
        return sorted(user_list, key=lambda x: (x.first_name, x.last_name))
