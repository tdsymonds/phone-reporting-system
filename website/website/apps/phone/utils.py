# -*- coding: utf-8 -*- 
from datetime import timedelta


class Reg(object):
    def __init__(self, cursor, row):
        for (attr, val) in zip((d[0] for d in cursor.description), row):
            setattr(self, attr, val)


# http://www.ianlewis.org/en/python-date-range-iterator
def datetimeRange(from_date, to_date=None):
    while to_date is None or from_date <= to_date:
        yield from_date
        from_date = from_date + timedelta(days=1)
