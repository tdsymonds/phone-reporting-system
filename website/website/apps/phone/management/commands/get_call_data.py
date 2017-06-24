# -*- coding: utf-8 -*- 
from datetime import datetime, timedelta
from django.conf import settings
from django.core.management.base import BaseCommand

import psycopg2

from website.apps.authentication.models import CustomUser

from ...models import Call, Department, DepartmentUser
from ...utils import Reg


class Command(BaseCommand):
    
    def get_curs(self, query):
        connstring = connstring = "dbname='%s' user='%s' password='%s' host='%s' port=%s" % (
            settings.PHONE_DATABASE['NAME'], 
            settings.PHONE_DATABASE['USER'], 
            settings.PHONE_DATABASE['PASSWORD'], 
            settings.PHONE_DATABASE['HOST'], 
            settings.PHONE_DATABASE['PORT'])

        conn = psycopg2.connect(connstring)
        curs = conn.cursor()
        curs.execute(query)
        return curs

    def get_departments(self):
        department_id_list = []

        # first get all departments from the phone database
        query = """ SELECT department_id, department_name
                    FROM tbldepartments"""
        
        curs = self.get_curs(query)

        # loop through each of the results
        for row in curs.fetchall():
            r = Reg(curs, row)

            # append the id to the departments list
            department_id_list += [r.department_id]

            # does the department already exist?
            department_exists = existing_department = Department.objects.filter(
                department_id=r.department_id).first()

            if department_exists:
                # the department exists, so just need to update
                # the existing information
                existing_department.name = r.department_name
                existing_department.save()
            else:
                # need to create the department
                new_department = Department(
                    department_id=r.department_id, 
                    name=r.department_name
                )
                new_department.save()
                print ('-Added: %s' % (new_department))


        # delete old departments
        # note: don't want to remove departments that have been 
        # added manually
        departments_to_delete = Department.objects.filter(
            added_manually=False).exclude(department_id__in=department_id_list)

        # todo: need to make sure child nodes aren't deleted when a parent node is!!
        # todo: delete these departments             

    def get_users(self):
        user_id_list = []

        # get all the users
        query = """ SELECT user_id, user_firstname, user_surname, 
                        user_email, user_extension, user_department_id,
                        user_active
                    FROM tblusers """
        
        curs = self.get_curs(query)

        # loop through each of the results
        for row in curs.fetchall():
            r = Reg(curs, row)

            # append the user id to the list
            user_id_list += [r.user_id]

            # does the user alreay exist?
            user_exists = existing_user = CustomUser.objects.filter(
                phone_id=r.user_id).first()

            if user_exists:
                # update the info
                existing_user.email = r.user_email
                existing_user.first_name = r.user_firstname
                existing_user.last_name = r.user_surname
                existing_user.is_active = r.user_active
                existing_user.phone_extension=r.user_extension
                existing_user.save()

                # has the department changed?
                new_department = Department.objects.filter(department_id=r.user_department_id).first()

                # only will be one active department user per user, so can get first
                department_user = DepartmentUser.objects.filter(date_left__isnull=True, user=existing_user).first()

                # do the departments match?
                if new_department != department_user.department:
                    # set the current department user as left
                    department_user.date_left = datetime.now()
                    # add the new department
                    department_user = DepartmentUser(department=new_department, user=existing_user)
                    department_user.save()

            else:
                # need to add a new user
                new_user = CustomUser(
                    email=r.user_email,
                    first_name=r.user_firstname,
                    last_name=r.user_surname,
                    is_active=r.user_active,
                    phone_id=r.user_id,
                    phone_extension=r.user_extension,
                )
                new_user.save()
                print ('-Added new user: %s' % (new_user))

                # need to add them to the correct department.
                department = Department.objects.filter(department_id=r.user_department_id).first()
                department_user = DepartmentUser(department=department, user=new_user)
                department_user.save()

                print ('--Added to department: %s' % (department))

        # note to self:
        # do i need to delete old users because whether they are 
        # active or not is already being handled by the phone system

    def get_calls(self):
        # calls are created after the phone call has complete,
        # so once logged they do not change, so only need to add
        # new calls and can skip existing.

        datetime_format = '%Y-%m-%d'
        today = datetime.now().strftime(datetime_format)

        # due to the large amount of data, need to import calls on a daily basis,
        # otherwise there is too much data to loop through and consider
        query = """ SELECT ch_call_id, ch_user_id, ch_calling_number, ch_called_number, 
                           ch_direction, ch_internal_external, ch_start_time, 
                           ch_end_time, ch_talk_time_seconds
                    FROM tblcallhistory
                    WHERE ch_start_time BETWEEN '%s 00:00' AND '%s 23:59:59' 
                """ % (today, today)

        curs = self.get_curs(query)

        # loop through each of the calls
        for row in curs.fetchall():
            r = Reg(curs, row)

            # does the call exist in my db?
            call_exists = Call.objects.filter(call_id=r.ch_call_id)

            if not call_exists:
                # need to add the call
                # first get the user
                user = CustomUser.objects.filter(phone_id=r.ch_user_id).first()

                new_call = Call(
                    call_id=r.ch_call_id,
                    user=user,
                    direction=r.ch_direction,
                    internal_external=r.ch_internal_external,
                    start_time=r.ch_start_time,
                    end_time=r.ch_end_time,
                    talk_time_seconds=r.ch_talk_time_seconds,
                )
                new_call.save()

        # calls aren't deleted from the system, so i don't need to handle this

    def quality_check(self):
        datetime_format = '%Y-%m-%d'
        today = datetime.now().strftime(datetime_format)
        two_weeks_ago = (datetime.now() - timedelta(weeks=2)).strftime(datetime_format)

        query = """ SELECT date_trunc('day', ch_start_time), COUNT(*)
                    FROM tblcallhistory
                    WHERE ch_start_time BETWEEN '%s 00:00' AND '%s 23:59:59' 
                    GROUP BY 1
                    ORDER BY 1
                """ % (two_weeks_ago, today)

        curs = self.get_curs(query)


        for row in curs.fetchall():
            # get the application call count for the day
            count = Call.objects.filter(start_time__gte=row[0], start_time__lt=(row[0] + timedelta(days=1))).count()

            # does the application call count match the phone db call count
            if row[1] != count:
                # no match, so there's an error!
                print ('- ERROR on %s: %s does not equal %s' % (row[0], count, row[1]))

    def get_call_data(self):
        self.get_departments()
        self.get_users()       
        self.get_calls()
        self.quality_check()

    def handle(self, *args, **options):
        self.get_call_data()
