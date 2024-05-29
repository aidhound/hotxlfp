# -*- coding: utf-8 -*-
"""
inspired by:
https://github.com/sutoiku/formula.js/blob/master/lib/date-time.js
"""
from . import dispatcher
from . import error
from . import utils
import datetime
import calendar


@dispatcher.register_for('DATE')
def DATE(year, month, day):
    year = utils.parse_number(year)
    month = utils.parse_number(month)
    day = utils.parse_number(day)
    if utils.any_is_error((year, month, day)):
        return error.VALUE
    if year < 1900:
        year += 1900
    return datetime.datetime(year, month, day)


@dispatcher.register_for('DATEVALUE')
def DATEVALUE(date):
    return utils.serialize_date(date)


@dispatcher.register_for('YEAR')
def YEAR(serial_number):
    serial_number = utils.parse_date(serial_number)
    if isinstance(serial_number, error.XLError):
        return serial_number
    return serial_number.year


@dispatcher.register_for('MONTH')
def MONTH(serial_number):
    serial_number = utils.parse_date(serial_number)
    if isinstance(serial_number, error.XLError):
        return serial_number
    return serial_number.month


@dispatcher.register_for('DAY')
def DAY(serial_number):
    serial_number = utils.parse_date(serial_number)
    if isinstance(serial_number, error.XLError):
        return serial_number
    return serial_number.day


@dispatcher.register_for('HOUR')
def HOUR(serial_number):
    serial_number = utils.parse_date(serial_number)
    if isinstance(serial_number, error.XLError):
        return serial_number
    return serial_number.hour


@dispatcher.register_for('MINUTE')
def MINUTE(serial_number):
    serial_number = utils.parse_date(serial_number)
    if isinstance(serial_number, error.XLError):
        return serial_number
    return serial_number.minute


@dispatcher.register_for('SECOND')
def SECOND(serial_number):
    serial_number = utils.parse_date(serial_number)
    if isinstance(serial_number, error.XLError):
        return serial_number
    return serial_number.second


@dispatcher.register_for('TODAY')
def TODAY():
    today = datetime.date.today()
    return datetime.datetime(today.year, today.month, today.day)


@dispatcher.register_for('DAYS')
def DAYS(end_date, start_date):
    end_date = utils.parse_date(end_date)
    start_date = utils.parse_date(start_date)
    if utils.any_is_error((end_date, start_date)):
        return error.VALUE
    return utils.serialize_date(end_date) - utils.serialize_date(start_date)


@dispatcher.register_for('NOW')
def NOW():
    return datetime.datetime.now()


@dispatcher.register_for('DATEDIF')
def DATEDIF(start_date, end_date, unit):
    start_date = utils.parse_date(start_date)
    end_date = utils.parse_date(end_date)
    if utils.any_is_error((start_date, end_date)):
        return error.NUM
    if type(unit) != str:
        return error.NAME
    unit = unit.lower()
    if start_date == end_date:
        return 0
    if start_date < end_date:
        if unit == 'y':
            return end_date.year - start_date.year - (1 if (end_date.month < start_date.month or (end_date.month == start_date.month and end_date.day < start_date.day)) else 0)
        if unit == 'm':
            return (end_date.year - start_date.year) * 12 + end_date.month - start_date.month - (1 if end_date.day < start_date.day else 0)
        if unit == 'd':
            return int(utils.serialize_date(end_date) - utils.serialize_date(start_date))
        if unit == 'md':
            start_day = start_date.day
            end_day = end_date.day
            if end_day >= start_day:
                return end_day - start_day
            else:
                prev_month = end_date.month - 1
                prev_month_days = 30 if prev_month in {4, 6, 9, 11} else 31 if prev_month != 2 else 29 if calendar.isleap(end_date.year) else 28
                return prev_month_days - start_day + end_day
        if unit == 'ym':
            start_month = start_date.month
            end_month = end_date.month
            year_diff = end_date.year - start_date.year
            month_diff = (year_diff * 12 + end_month - start_month)
            if end_date.day < start_date.day:
                month_diff -= 1
            return int(month_diff % 12)
        if unit == 'yd':
            start_date_end_year = datetime.datetime(end_date.year, start_date.month, start_date.day)
            if start_date_end_year > end_date:
                start_date_end_year = datetime.datetime(end_date.year - 1, start_date.month, start_date.day)
            return int(utils.serialize_date(end_date) - utils.serialize_date(start_date_end_year))
    return error.NUM


@dispatcher.register_for('EDATE')
def EDATE(start_date, month):
    if start_date == None:
        default_date = True
        start_date = datetime.datetime(1900, 1, 1)
    else:
        default_date = False
        start_date = utils.parse_date(start_date)
    if month == None:
        return start_date
    month= int(month)
    year = start_date.year + (month // 12)
    month = start_date.month + (month % 12)
    if month > 12:
        month -= 12
        year += 1
    elif month < 1:
        month += 12
        year -= 1
    if default_date:
        month -= 1
        if month == 2:
            day = 29 if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0) else 28
        elif month in {4, 6, 9, 11}:
            day = 30
        else:
            day = 31
    else:
        day = start_date.day
        day = min(day, [31, 29 if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
    if year > 9999 or year < 1900:
        return error.NUM
    return datetime.datetime(year, month, day)