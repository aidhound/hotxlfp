# -*- coding: utf-8 -*-
import re
import fnmatch
import itertools
from .._compat import number_types, string_types
from ..helper.number import to_number
import operator
from . import error
import datetime
import time
from dateutil.parser import parse as to_date

OPERATOR_DICT = {
    '>': operator.gt,
    '<': operator.lt,
    '<>': operator.ne,
    '=': operator.eq,
    '>=': operator.ge,
    '<=': operator.le,
}

REGEX_CRITERIA = re.compile(r'(?P<op>[\<\>\=]*)(?P<val>[\w\d\.\*\?]+)')


def iflatten(iterable):
    if not isinstance(iterable, (list, tuple)):
        yield iterable
        return
    remainder = iter(iterable)
    while True:
        try:
            first = next(remainder)
        except StopIteration:
            return
        if isinstance(first, (list, tuple)):
            remainder = itertools.chain(first, remainder)
        else:
            yield first


def flatten(l):
    return list(iflatten(l))


def inumbers(l, try_parse=False, text_is_zero=False):
    """ only the numbers """
    for el in iflatten(l):
        if try_parse:
            el = to_number(el)
        if isinstance(el, number_types):
            yield el
        elif text_is_zero and isinstance(el, string_types):
            yield 0


def numbers(l, try_parse=False, text_is_zero=False):
    return list(inumbers(l, try_parse=try_parse, text_is_zero=text_is_zero))


def parse_number(string):
    num = to_number(string)
    if isinstance(num, number_types):
        return num
    if isinstance(num, error.XLError):
        return num
    return error.VALUE


def iparse_number_array_aux(arr):
    for el in arr:
        yield parse_number(el)


def iparse_number_array(arr):
    if not arr:
        return error.VALUE
    return iparse_number_array_aux(arr)


def parse_criteria(criteria):
    match = REGEX_CRITERIA.match(criteria)
    op = match.group('op')
    val = match.group('val')
    if op:
        val = to_number(val)
        op = OPERATOR_DICT[op]
        return lambda a: op(a, val)
    else:
        if any(c in val for c in ('?', '*')):
            # Then use fnmatch
            return lambda a: fnmatch.fnmatch(val, a)
        else:
            return lambda a: a == to_number(val)


def any_is_error(iterable):
    return any(isinstance(el, error.XLError) for el in iterable)


date_1900 = datetime.datetime(1900, 1, 1)
epoch = datetime.datetime(1970, 1, 1)


def epoch_seconds(date):
    return (date - epoch).total_seconds()


def parse_date(date):
    if isinstance(date, error.XLError):
        return date
    if isinstance(date, datetime.datetime):
        return date
    date = to_number(date)
    if isinstance(date, number_types):
        d = int(date)
        if d < 0:
            return error.NUM
        if d <= 60:
            return datetime.datetime.fromtimestamp(epoch_seconds(date_1900) + (d - 1) * 86400)
        return datetime.datetime.fromtimestamp(epoch_seconds(date_1900) + (d - 2) * 86400)
    if isinstance(date, string_types):
        try:
            return to_date(date)
        except ValueError:
            pass
    return error.VALUE
