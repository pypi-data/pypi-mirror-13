# -*- coding: utf-8 -*-

import datetime
import pytz


def get_day_after(date):
    return date + datetime.timedelta(days=1)


def get_day_before(date):
    return date + datetime.timedelta(days=-1)


def get_yesterday():
    return get_day_before(datetime.date.today())


def get_tomorrow():
    return get_day_after(datetime.date.today())


def get_two_days_ago():
    return get_day_before(get_yesterday())


def get_first_day_of_month(ts):
    return datetime.datetime(ts.year, ts.month, 1)


def get_date_seven_days_ago():
    return datetime.date.today() - datetime.timedelta(days=7)


def get_date_thirty_days_ago():
    return datetime.date.today() - datetime.timedelta(days=30)


def get_ts_beg_and_ts_end_from_date(date):
    ts_beg = datetime.datetime(*(date.timetuple()[:6]), tzinfo=pytz.utc)
    ts_end = datetime.datetime(*(date.timetuple()[:3]), hour=23, minute=59, second=59, tzinfo=pytz.utc)
    return ts_beg, ts_end


def get_date_range(date_beg, date_end):
    return [date_beg + datetime.timedelta(days=i) for i in range((date_end - date_beg).days + 1)]
