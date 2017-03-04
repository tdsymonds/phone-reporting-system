"""
The purpose of this script is to create random call data 
and populate the database. 

There are some subtleties that I have ignored, such as
in reality a user cannot receive two calls at the same
time, which is possible with the below. The calls are
also unifomly distributed throughout the open hours,
whereas in reality, this is unlikely to be the case.
Also the number of calls that are received could be 
modelled more realistically.

However this being said, for the purpose of my project,
these subtleties should not raise too many problems.
"""
from datetime import timedelta, date, datetime, time
from settings_secret import PHONE_DATABASE_SETTINGS

import csv
import numpy as np
import psycopg2
import random

# department names and their
# size in percentage
DEPARTMENTS = [
    {
        'name': 'Reception',
        'size': 0.01
    },
    {
        'name': 'Directors',
        'size': 0.01
    },
    {
        'name': 'Lettings',
        'size': 0.3
    },
    {
        'name': 'Sales',
        'size': 0.23
    },
    {
        'name': 'Business Development',
        'size': 0.05
    },
    {
        'name': 'Team Leo',
        'size': 0.04
    },
    {
        'name': 'Team Lyra',
        'size': 0.04
    },
    {
        'name': 'Team Orion',
        'size': 0.04
    },
    {
        'name': 'Team Pegasus',
        'size': 0.04
    },
    {
        'name': 'Team Phoenix',
        'size': 0.04
    },
    {
        'name': 'Team Polaris',
        'size': 0.04
    },
    {
        'name': 'Team Neptune',
        'size': 0.08
    },
    {
        'name': 'Team Jupiter',
        'size': 0.08
    },
]

# will be used for generating email addresses
DOMAIN = 'example.co.uk'
NUMBER_OF_STAFF = 200
OPEN_HOUR = 9
CLOSE_HOUR = 18
MIN_CALLS_PER_DAY = 500
MAX_CALLS_PER_DAY = 5000
AVERAGE_CALL_LENGTH_MINS = 5

def main():
    # initial_setup()
    log_calls(date(2017,1,1), date(2017,5,1))

def log_calls(date_from, date_to):
    # setup db connection
    conn, curs = setup_connection()

    # loop through each date in the parameters skipping weekends
    WEEKEND = set([5, 6])
    for dte in daterange(date_from, date_to):
        if dte.weekday() not in WEEKEND:

            # loop through a random number of calls in the range
            for i in range(random.randint(MIN_CALLS_PER_DAY, MAX_CALLS_PER_DAY)):

                # get a random start time for the call
                random_hour = random.randint(OPEN_HOUR, CLOSE_HOUR)
                random_minute = random.randint(0, 59)
                random_second = random.randint(0, 59)
                start_time_dt = datetime(dte.year, dte.month, dte.day, random_hour, random_minute, random_second)

                # then get a random talk time and calculate the end time
                # of the call
                # I believe the gamma distribution models call length
                # reasonable, so using this distribution to generate a 
                # random number, transform to what is approx the average
                # call length, then multiplying by 60 to convert to seconds
                talk_time = int(np.random.gamma(2, 0.5, 1)[0] * AVERAGE_CALL_LENGTH_MINS * 60)
                end_time_dt = start_time_dt + timedelta(seconds=talk_time)
                
                # convert both dates to strings            
                start_time = start_time_dt.strftime('%Y-%m-%d %H:%m:%S')
                end_time = end_time_dt.strftime('%Y-%m-%d %H:%m:%S')

                # get other required parts
                internal_external = random.randint(0, 1)
                direction = random.randint(0, 1)
                # this technically isn't correct, as they'd be calling
                # an extension for inbound, and from on outbound, but 
                # the purpose of this is just to create some noise,
                # so this is sufficient for now.
                caller =  _get_random_caller()
                called =  _get_random_caller()

                # get a random user
                user_id = random.randint(0, NUMBER_OF_STAFF-1)

                query = """ INSERT INTO tblcallhistory (
                                ch_user_id,
                                ch_calling_number,
                                ch_called_number,
                                ch_direction,
                                ch_internal_external,
                                ch_start_time,
                                ch_end_time,
                                ch_talk_time_seconds
                            ) VALUES (
                                %s, '%s', '%s', %s, %s, '%s', '%s', %s
                            ); """ % (
                                user_id, 
                                caller, 
                                called,
                                direction,
                                internal_external,
                                start_time,
                                end_time,
                                talk_time
                            )

                curs.execute(query)


    # close db connection
    close_connection(conn, curs)

def _get_random_caller():
    return '0%s' %  (7000000000 + random.randint(0, 1000000000-1))

def initial_setup():
    insert_departments()
    insert_names()

def insert_names():
    # first get names
    names = get_common_names()

    # create list of spaces available in each department
    # so that users can be populated to expected size.
    departments_available = []
    for index, department in enumerate(DEPARTMENTS):
        departments_available += [index for i in range((int(department['size'] * NUMBER_OF_STAFF)))]

    # setup db connection
    conn, curs = setup_connection()

    # loop through all the names and create users in the db
    for index, name_list in enumerate(names):
        # get the department for the user
        if len(departments_available) > 0:
            i = random.randint(0, len(departments_available)-1)
            department_id = departments_available.pop(i)
        else:
            # if a rounding error means we have no more
            # departments for a particular user, allocate
            # randomly to any department
            department_id = random.randint(0, len(DEPARTMENTS))


        query = """ INSERT INTO tblusers (
                        user_id,
                        user_firstname,
                        user_surname,
                        user_active,
                        user_email,
                        user_extension,
                        user_department_id
                    ) VALUES (
                        %s, '%s', '%s', %s, '%s', '%s', %s
                    );""" % (
                        index, 
                        name_list[0],
                        name_list[1],
                        _is_user_active(index),
                        _set_user_email(name_list[0], name_list[1]),
                        _set_user_extension(department_id, index),
                        department_id
                    )

        curs.execute(query)

def _is_user_active(index):
    # return 1 in 10 as not active, just to throw a
    # spanner in the works
    if index % 10 == 0:
        return 0
    return 1

def _set_user_email(firstname, surname):
    return '%s.%s@%s' % (firstname, surname, DOMAIN)

def _set_user_extension(department_id, index):
    return (department_id * 100) + index

def get_common_names():
    # Common names obtained from here on 2nd Feb 2017:
    # http://www.quietaffiliate.com/free-first-name-and-last-name-databases-csv-and-sql/
    path = 'data/'

    firstname_list = _get_common_names(path + 'common-firstnames.csv')
    surname_list = _get_common_names(path + 'common-surnames.csv')

    number_of_firstnames = len(firstname_list)
    number_of_surnames = len(surname_list)
    names = []

    for i in range(NUMBER_OF_STAFF):
        random_firstname = firstname_list[random.randint(0,number_of_firstnames-1)][0]
        random_surname = surname_list[random.randint(0,number_of_surnames-1)][0]

        names.append([random_firstname, random_surname])  

    return names
    
def _get_common_names(filepath):
    with open(filepath, 'r') as f:
        reader = csv.reader(f)
        # skip the header row
        next(reader, None)
        return list(reader)        

def insert_departments():
    conn, curs = setup_connection()

    for index, department in enumerate(DEPARTMENTS):
        query = """ INSERT INTO tbldepartments (
                        department_id, 
                        department_name
                    ) VALUES (
                        %s, 
                        '%s'
                    );""" % (index, department['name'])

        curs.execute(query)

    close_connection(conn, curs)

def setup_connection():
    # TODO: add these variables to project settings
    connstring = "port=%s dbname=%s user=%s host='%s' password='%s'" % (
            PHONE_DATABASE_SETTINGS['port'],
            PHONE_DATABASE_SETTINGS['name'],
            PHONE_DATABASE_SETTINGS['user'],
            PHONE_DATABASE_SETTINGS['host'],
            PHONE_DATABASE_SETTINGS['password']
        )

    conn = psycopg2.connect(connstring)
    conn.autocommit = True
    curs = conn.cursor()
    return (conn, curs)

def close_connection(conn, curs):
    curs.close()
    conn.close()

def daterange(start_date, end_date):
    for n in range(int((end_date-start_date).days)):
        yield start_date + timedelta(n)


if __name__ == '__main__':
    main()
