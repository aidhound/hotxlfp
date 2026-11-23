# -*- coding: utf-8 -*-
import re
import fnmatch
import itertools
from functools import wraps
from .._compat import number_types, string_types
from ..helper.number import to_number
import operator
from . import error
import datetime
import time
from dateutil.parser import parse as to_date

DEFAULT = lambda: 0

OPERATOR_DICT = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.truediv,
    '>': operator.gt,
    '<': operator.lt,
    '<>': operator.ne,
    '=': operator.eq,
    '>=': operator.ge,
    '<=': operator.le,
}

REGEX_CRITERIA = re.compile(r'(?P<op><>|<=|>=|<|>|=)?(?P<val>.*)', re.UNICODE)

# Excel orders these error codes when they are used in criteria comparisons.
CRITERIA_ERROR_ORDER = {
    str(code): position for position, code in enumerate((
        error.NULL, error.DIV_ZERO, error.VALUE, error.REF,
        error.NAME, error.NUM, error.NOT_AVAILABLE,
    ))
}


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


def array_shape(array):
    """Return a two-dimensional shape, or an Excel error for an invalid array.

    Flat lists/tuples are columns. Nested arrays must be rectangular and have
    no more than two dimensions.
    """
    if isinstance(array, error.XLError):
        return array
    if not isinstance(array, (list, tuple)):
        return error.VALUE
    if not any(isinstance(item, (list, tuple)) for item in array):
        return len(array), 1
    if not all(isinstance(row, (list, tuple)) for row in array):
        return error.VALUE

    columns = len(array[0])
    for row in array:
        if len(row) != columns or any(isinstance(item, (list, tuple)) for item in row):
            return error.VALUE
    return len(array), columns


def inumbers(l, try_parse=False, text_is_zero=False):
    """Yield numeric values, raising XLError to abort on an Excel error.

    Raising prevents consumers such as sum from accepting a partial result.
    Parser.call_function catches this internal abort and returns the error as
    a value for enclosing formula functions to handle.
    """
    for el in iflatten(l):
        if try_parse or isinstance(el, number_types):
            el = to_number(el)
        if isinstance(el, error.XLError):
            raise el
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

def parse_complex(string):
    if string is None:
        return 0
    if isinstance(string, complex):
        return string
    if isinstance(string, error.XLError):
        return string
    try:
        return complex(string.replace('i', 'j').replace(' ', ''))
    except ValueError:
        return error.NUM

def iparse_number_array_aux(arr):
    for el in arr:
        yield parse_number(el)


def iparse_number_array(arr):
    if not arr:
        return error.VALUE
    return iparse_number_array_aux(arr)


def parse_criteria(criteria):
    """Compile a predicate, treating error criteria as values to match.

    Error cells do not match numeric ordering, but can match error codes or
    inequality criteria. Selected aggregate errors are handled by the caller.
    Invalid numeric conversions still raise XLError at the function boundary.
    """
    op = '='
    val = criteria
    if isinstance(criteria, string_types):
        match = REGEX_CRITERIA.match(criteria)
        op = match.group('op') or '='
        val = match.group('val')
        criterion_error = error.from_message(val.upper()) if val.startswith('#') else None
        if criterion_error is not None and str(criterion_error) == val.upper():
            val = criterion_error
        else:
            val = to_number(val)
            if isinstance(val, error.XLError):
                raise val

    compare = OPERATOR_DICT[op]
    if isinstance(val, error.XLError):
        criterion_code = str(val)
        criterion_order = CRITERIA_ERROR_ORDER.get(criterion_code)

        def match_error(value):
            if not isinstance(value, error.XLError):
                return op == '<>'
            if op in ('=', '<>'):
                return compare(str(value), criterion_code)
            value_order = CRITERIA_ERROR_ORDER.get(str(value))
            return (value_order is not None and criterion_order is not None
                    and compare(value_order, criterion_order))
        return match_error

    if isinstance(val, string_types) and op in ('=', '<>'):
        if any(c in val for c in ('?', '*')):
            # Excel criteria ignore case; keep path separators literal.
            pattern = re.compile(fnmatch.translate(val), re.IGNORECASE)

            def match_text(value):
                matched = (isinstance(value, string_types)
                           and pattern.match(value) is not None)
                return not matched if op == '<>' else matched
            return match_text
        if val == '':
            return lambda value: (value is None or value == '') == (op == '=')

    if isinstance(val, string_types):
        val = val.lower()

        def match_text(value):
            if not isinstance(value, string_types):
                return op == '<>'
            return compare(value.lower(), val)
        return match_text

    if op in ('=', '<>'):
        return lambda value: compare(value, val)

    # Choose the ordering category once, rather than checking the criterion per cell.
    value_types = number_types if isinstance(val, number_types) else string_types
    return lambda value: isinstance(value, value_types) and compare(value, val)


def any_is_error(iterable):
    return any(isinstance(el, error.XLError) for el in iterable)


def propagate_errors(*, nested=False):
    """Return the first typed error before calling the decorated function.

    By default only direct arguments are checked. With nested=True, list/tuple
    elements are checked too. The scan completes before a short-circuiting
    consumer runs; the original arguments remain available to the function.
    """
    def decorate(function):
        @wraps(function)
        def wrapped(*args, **kwargs):
            values = itertools.chain(args, kwargs.values())
            if nested:
                values = itertools.chain.from_iterable(
                    iflatten(value) for value in values
                )
            for value in values:
                if isinstance(value, error.XLError):
                    return value
            return function(*args, **kwargs)
        return wrapped
    return decorate


date_1900 = datetime.datetime(1900, 1, 1)
epoch = datetime.datetime(1970, 1, 1)


def epoch_seconds(date):
    return (date - epoch).total_seconds()


def parse_date(date):
    if isinstance(date, error.XLError):
        return date
    if isinstance(date, datetime.datetime):
        return date
    if isinstance(date, datetime.date):
        return datetime.datetime(date.year, date.month, date.day)
    date = to_number(date)
    if isinstance(date, error.XLError):
        return date
    if isinstance(date, number_types):
        if date < 0:
            return error.NUM
        if date < 1:
            return date_1900
        if date <= 60:
            return epoch + datetime.timedelta(seconds=(epoch_seconds(date_1900) + (date - 1) * 86400))
        return epoch + datetime.timedelta(seconds=(epoch_seconds(date_1900) + (date - 2) * 86400))
    if isinstance(date, string_types):
        try:
            return to_date(date)
        except ValueError:
            pass
    return error.VALUE


def serialize_date(date):
    date = parse_date(date)
    if isinstance(date, error.XLError):
        return date
    if not isinstance(date, datetime.datetime):
        return error.VALUE
    if date == date_1900:
        return 0
    date = epoch_seconds(date) * 1000
    d1900 = epoch_seconds(date_1900) * 1000
    if date <= -2203891200000:
        return (date - d1900) / 86400000 + 1
    return (date - d1900) / 86400000 + 2
