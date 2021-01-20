# -*- coding: utf-8 -*-
"""
inspired by:
https://github.com/sutoiku/formula.js/blob/master/lib/information.js
"""

from . import dispatcher
from . import error
from . import utils
from .._compat import number_types, string_types
import datetime


@dispatcher.register_for('ERROR.TYPE')
def ERROR_TYPE(error_val):
    errdict = {
        error.NULL: 1,
        error.DIV_ZERO: 2,
        error.VALUE: 3,
        error.REF: 4,
        error.NAME: 5,
        error.NUM: 6,
        error.NOT_AVAILABLE: 7,
        error.DATA: 8
    }
    return errdict.get(error_val, error.NOT_AVAILABLE)


@dispatcher.register_for('ISBLANK')
def ISBLANK(value):
    return value is None


@dispatcher.register_for('ISERR')
def ISERR(value):
    return isinstance(value, error.XLError) and value != error.NOT_AVAILABLE


@dispatcher.register_for('ISERROR')
def ISERROR(value):
    return isinstance(value, error.XLError)


@dispatcher.register_for('ISEVEN')
def ISEVEN(number):
    if not isinstance(number, number_types):
        return error.VALUE
    return (int(number) & 1) == 0


@dispatcher.register_for('ISODD')
def ISODD(number):
    if not isinstance(number, number_types):
        return error.VALUE
    return (int(number) & 1)


@dispatcher.register_for('ISTEXT')
def ISTEXT(value):
    return isinstance(value, string_types)


@dispatcher.register_for('ISNUMBER')
def ISNUMBER(value):
    return (not isinstance(value, bool)) and isinstance(value, number_types)


@dispatcher.register_for('ISLOGICAL')
def ISLOGICAL(value):
    return isinstance(value, bool)


@dispatcher.register_for('ISNA')
def ISNA(value):
    return value == error.NOT_AVAILABLE


@dispatcher.register_for('N')
def N(value):
    if isinstance(value, (error.XLError, number_types)):
        return value
    if isinstance(value, datetime.datetime):
        return utils.serialize_date(value)
    if value is True:
        return 1
    return 0


@dispatcher.register_for('NA')
def NA():
    return error.NOT_AVAILABLE


@dispatcher.register_for('ISNONTEXT')
def ISNONTEXT(value):
    return not isinstance(value, string_types)
