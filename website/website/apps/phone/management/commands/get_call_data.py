# -*- coding: utf-8 -*- 
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
            added_manually=False).exlcude(department_id__in=department_id_list)



        # need to make sure child nodes aren't deleted when a parent node is!!

              

    def get_users(self):
        query = """ SELECT user_id, user_firstname, user_surname, user_active, 
                        user_email, user_extension, user_department_id
                    FROM tblusers"""
        
        curs = self.get_curs(query)

        for row in curs.fetchall():
            r = Reg(curs, row)
            # print (r.user_firstname, r.user_surname)

    def get_call_data(self):
        self.get_departments()
        # self.get_users()       

    def handle(self, *args, **options):
        self.get_call_data()
