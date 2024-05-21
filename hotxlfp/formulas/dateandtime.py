# -*- coding: utf-8 -*-
"""
inspired by:
https://github.com/sutoiku/formula.js/blob/master/lib/date-time.js
"""
from . import dispatcher
from . import error
from . import utils
import datetime


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
        return error.VALUE
    unit = unit.lower()
    if start_date < end_date:
        if unit == 'y':
            return YEAR(end_date) - YEAR(start_date) - (1 if (MONTH(end_date) < MONTH(start_date) or (MONTH(end_date) == MONTH(start_date) and DAY(end_date) < DAY(start_date))) else 0)
        if unit == 'm':
            return (YEAR(end_date) - YEAR(start_date)) * 12 + MONTH(end_date) - MONTH(start_date) - (1 if DAY(end_date) < DAY(start_date) else 0)
        if unit == 'd':
            return int(DAYS(end_date, start_date))
    if unit == 'md':
        start_day = DAY(start_date)
        end_day = DAY(end_date)
        if end_day >= start_day:
            return end_day - start_day
        else:
            prev_month = MONTH(end_date) - 1
            prev_month_days = 30 if prev_month in {4, 6, 9, 11} else 31 if prev_month != 2 else 29 
            return prev_month_days - start_day + end_day
    if unit == 'ym':
        start_month = MONTH(start_date)
        end_month = MONTH(end_date)
        year_diff = YEAR(end_date) - YEAR(start_date)
        month_diff = (year_diff * 12 + end_month - start_month)
        if DAY(end_date) < DAY(start_date):
            month_diff -= 1
        return int(month_diff % 12)
    if unit == 'yd':
        start_date_end_year = DATE(YEAR(end_date), MONTH(start_date), DAY(start_date))
        if start_date_end_year > end_date:
            start_date_end_year = DATE(YEAR(end_date) - 1, MONTH(start_date), DAY(start_date))
        return int(DAYS(end_date, start_date_end_year))