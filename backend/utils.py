import datetime

import dateutil
from asgiref.sync import sync_to_async
from dateutil.relativedelta import relativedelta
from django.contrib import messages

from constants import months_int


@sync_to_async
def get_related_object(obj, related):
    return getattr(obj, related)


def add_messages(request, new_messages):
    msg_storage = messages.get_messages(request)
    msg_list = [m.message for m in msg_storage]
    msg_storage.used = False
    for text in new_messages:
        if text not in msg_list:
            messages.error(request, text)


#     Date functions


def get_years_range():
    years_range = []
    for year in range(
        (datetime.date.today() - relativedelta(years=2)).year,
        (datetime.date.today() + relativedelta(years=5)).year,
    ):
        years_range.append((year, year))
    return years_range


def get_current_year():
    year = datetime.date.today().year
    return (year, year)


def get_current_month():
    month = months_int[datetime.date.today().month - 1]
    return month


def append_data(date, *args, **kwargs):
    return date + datetime.timedelta(*args, **kwargs)


def first_day_of_the_previous_month():
    today = datetime.date.today()
    return today.replace(day=1) + dateutil.relativedelta.relativedelta(
        months=-1
    )


def last_day_of_the_previous_month():
    today = datetime.date.today()
    return today.replace(day=1) - datetime.timedelta(days=1)


def get_last_days_of_the_month(year, month):
    if month == 12:
        end_date = datetime.date(day=1, month=1, year=year + 1)
    else:
        end_date = datetime.date(day=1, month=month + 1, year=year)
    end_date -= datetime.timedelta(days=1)
    return end_date.day
