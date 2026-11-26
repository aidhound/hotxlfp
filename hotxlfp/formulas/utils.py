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


def scan_array(array, ignore=0, scan_by_column=False):
    """Return a lazy iterator over a validated rectangular sequence of rows.

    ignore controls which cells are skipped:
        0: Keep all cells.
        1: Skip blanks (None).
        2: Skip XLError cells.
        3: Skip both blanks and errors.
    Retained blanks become 0; empty text stays unchanged.

    scan_by_column controls traversal order:
        False (default): Read each row left to right, then move down.
        True: Read each column top to bottom, then move right.
    For [[1, 2], [3, 4]], these produce 1, 2, 3, 4 and 1, 3, 2, 4.

    The caller validates the array shape and normalizes these options.
    """
    rows = zip(*array) if scan_by_column else array
    return (0 if value is None else value for row in rows for value in row
            if not (ignore & 1 and value is None)
            and not (ignore & 2 and isinstance(value, error.XLError)))


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


def array_value(value, shape, row, column):
    """Read a broadcast cell, using #N/A outside non-singleton dimensions."""
    if not isinstance(value, (list, tuple)):
        return value
    row = 0 if shape[0] == 1 else row
    column = 0 if shape[1] == 1 else column
    if row >= shape[0] or column >= shape[1]:
        return error.NOT_AVAILABLE
    values = value[row]
    return values[column] if isinstance(values, (list, tuple)) else values


def map_arrays(function, left, right):
    """Map a function over corresponding cells of two broadcast arrays.

    Flat vectors are columns. Singleton dimensions repeat; unmatched cells
    supply #N/A to the function, which decides how to handle error values.
    """
    left_shape = array_shape(left)
    if isinstance(left_shape, error.XLError):
        return left_shape
    right_shape = array_shape(right)
    if isinstance(right_shape, error.XLError):
        return right_shape

    shape = []
    for left_size, right_size in zip(left_shape, right_shape):
        if left_size == 0 or right_size == 0:
            if max(left_size, right_size) > 1:
                return error.VALUE
            shape.append(0)
        else:
            shape.append(max(left_size, right_size))

    # Retain the left array's containers; a right-hand matrix supplies row
    # containers when broadcasting a flat left vector into a matrix.
    row_templates = None
    for array in (left, right):
        if array and isinstance(array[0], (list, tuple)):
            row_templates = array
            break

    result = []
    for row in range(shape[0]):
        values = [
            function(array_value(left, left_shape, row, column),
                     array_value(right, right_shape, row, column))
            for column in range(shape[1])
        ]
        if row_templates is not None:
            row_type = type(row_templates[min(row, len(row_templates) - 1)])
            result.append(row_type(values))
        else:
            result.append(values[0])
    return type(left)(result)


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


def parse_integer(value, minimum=0):
    """Parse an integer argument, checking its minimum before truncation."""
    value = parse_number(0 if value is None else value)
    if isinstance(value, error.XLError):
        return value
    if isinstance(value, complex) or value < minimum:
        return error.VALUE
    return int(value)


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


def compile_criteria_pattern(value):
    """Compile an Excel wildcard pattern with literal brackets and ~ escapes.

    The caller selects wildcard mode only for criteria containing * or ?;
    otherwise Excel treats tildes as ordinary text.
    """
    parts = []
    characters = iter(value)
    for character in characters:
        if character == '~':
            character = next(characters, '')
            if character in ('*', '?', '[', ']'):
                character = '[' + character + ']'
        elif character in ('[', ']'):
            character = '[' + character + ']'
        parts.append(character)
    return re.compile(fnmatch.translate(''.join(parts)), re.IGNORECASE)


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
        criterion_text = val.upper()
        criterion_error = error.from_message(criterion_text) if val.startswith('#') else None
        if criterion_error is not None and str(criterion_error) == criterion_text:
            val = criterion_error
        elif criterion_text in ('TRUE', 'FALSE'):
            val = criterion_text == 'TRUE'
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

    if isinstance(val, bool):
        if op == '<>':
            return lambda value: not isinstance(value, bool) or compare(value, val)
        return lambda value: isinstance(value, bool) and compare(value, val)

    if isinstance(val, string_types) and op in ('=', '<>'):
        if any(c in val for c in ('?', '*')):
            # Excel criteria ignore case; keep path separators literal.
            pattern = compile_criteria_pattern(val)

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

    if isinstance(val, number_types) and not isinstance(val, bool):
        if op == '=':
            def match_number(value):
                if isinstance(value, string_types):
                    value = to_number(value)
                return not isinstance(value, bool) and compare(value, val)
            return match_number
        if op == '<>':
            return lambda value: isinstance(value, bool) or compare(value, val)

    if op in ('=', '<>'):
        return lambda value: compare(value, val)

    # Choose the ordering category once, rather than checking the criterion per cell.
    value_types = number_types if isinstance(val, number_types) else string_types
    return lambda value: (isinstance(value, value_types)
                          and not isinstance(value, bool) and compare(value, val))


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


# Serial-zero baseline for Excel's 1900 date system.
date_1900 = datetime.datetime(1899, 12, 31)
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
            # Represent Excel's January 0 using the preceding real calendar day.
            return date_1900 + datetime.timedelta(days=date)
        if date <= 60:
            return epoch + datetime.timedelta(seconds=(epoch_seconds(date_1900) + date * 86400))
        return epoch + datetime.timedelta(seconds=(epoch_seconds(date_1900) + (date - 1) * 86400))
    if isinstance(date, string_types):
        try:
            return to_date(date)
        except ValueError:
            pass
    return error.VALUE


def serialize_date(date):
    """Return a 1900-system serial, reserving 60 for Excel's fictitious date."""
    date = parse_date(date)
    if isinstance(date, error.XLError):
        return date
    if not isinstance(date, datetime.datetime):
        return error.VALUE
    days = (date - date_1900).total_seconds() / 86400
    # For Lotus 1-2-3 compatibility, Excel treats 1900 as a leap year.
    # Reserve serial 60 for the fictitious February 29, which datetime cannot represent.
    return days + (0 if date < datetime.datetime(1900, 3, 1) else 1)
