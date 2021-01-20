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
