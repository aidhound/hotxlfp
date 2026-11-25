# -*- coding: utf-8 -*-
import datetime
from . import error
from ..helper.number import to_number, validate_number
from ..helper.text import to_string
from .utils import (
    OPERATOR_DICT, serialize_date, parse_date, date_1900, array_shape, array_value
)
from .._compat import number_types, string_types


NoneType = type(None)


class ExcelComparator(object):

    def __init__(self, value):
        self.value = value
        if isinstance(value, datetime.date):
            # datetime.datetime is a subclass of datetime.date; serialize_date
            # (via parse_date) already normalizes plain dates correctly.
            self.value = serialize_date(value)

    def convert_other(self, other):
        if other is None:
            if isinstance(self.value, bool):
                other = False
            elif isinstance(self.value, number_types):
                other = type(self.value)(0)  # so it's the same number type
            elif isinstance(self.value, string_types):
                other = ''
        elif isinstance(other, datetime.date):
            other = serialize_date(other)
        return other

    def __lt__(self, other):
        if self.value is None:
            if other is None:
                return False
            else:
                return ExcelComparator(other).__gt__(self.value)
        if type(self.value) != type(other):
            other = self.convert_other(other)
        if type(self.value) != type(other) and not (isinstance(self.value, number_types) and isinstance(other, number_types)):
            # if the type is still different
            if isinstance(self.value, bool):
                return False  # bool is the biggest in XL
            if isinstance(self.value, string_types):
                if isinstance(other, bool):
                    return True
                if isinstance(other, number_types):
                    return False
            if isinstance(self.value, number_types):
                return True
        return self.value < other

    def __gt__(self, other):
        if self.value is None:
            if other is None:
                return False
            return ExcelComparator(other).__lt__(self.value)
        if type(self.value) != type(other):
            other = self.convert_other(other)
        if type(self.value) != type(other) and not (isinstance(self.value, number_types) and isinstance(other, number_types)):
            if isinstance(self.value, bool):
                return True  # bool is the biggest in XL
            if isinstance(self.value, string_types):
                if isinstance(other, bool):
                    return False
                if isinstance(other, number_types):
                    return True
            if isinstance(self.value, number_types):
                return False
        return self.value > other

    def __eq__(self, other):
        if self.value is None:
            if other is None:
                return True
            return ExcelComparator(other).__eq__(self.value)
        if type(self.value) != type(other):
            other = self.convert_other(other)
        return self.value == other

    def __ge__(self, other):
        return self.__gt__(other) or self.__eq__(other)

    def __le__(self, other):
        return self.__lt__(other) or self.__eq__(other)


def value_and_type(value):
    if isinstance(value, number_types):
        value = to_number(value)
        if isinstance(value, error.XLError):
            return (value, error.XLError)
        return (value, number_types)
    if isinstance(value, datetime.datetime):
        return (value, datetime.datetime)
    if isinstance(value, datetime.date):
        # Normalize a plain date to a real datetime so every downstream
        # conversion in IMPLICIT_DATA_TYPE_CONVERSIONS (keyed by
        # datetime.datetime) applies to it unchanged.
        return (datetime.datetime(value.year, value.month, value.day), datetime.datetime)
    if isinstance(value, string_types):
        value = to_number(value)
        if isinstance(value, error.XLError):
            return (value, error.XLError)
        if isinstance(value, number_types):
            return value_and_type(value)
        try_date = parse_date(value)
        if isinstance(try_date, error.XLError):
            return (value, string_types)
        return value_and_type(try_date)
    if isinstance(value, NoneType):
        return (value, NoneType)
    if isinstance(value, error.XLError):
        return (value, error.XLError)
    return (error.VALUE, error.XLError)


# see https://support.office.com/en-ie/article/data-types-in-data-models-e2388f62-6122-4e2b-bcad-053e3da9ba90#__toc319430523
IMPLICIT_DATA_TYPE_CONVERSIONS = {
    '+': {
        # left operand
        number_types: {
            # right operand
            datetime.datetime: {
                # conversion
                'left': None,
                'right': serialize_date,
                'result': parse_date
            },
            number_types: {
                'left': None,
                'right': None
            },
            NoneType: {
                'left': None,
                'right': lambda x: 0
            }
        },
        datetime.datetime: {
            datetime.datetime: {
                'left': serialize_date,
                'right': serialize_date
            },
            number_types: {
                'left': serialize_date,
                'right': None,
                'result': parse_date
            },
            NoneType: {
                'left': serialize_date,
                'right': lambda x: 0,
                'result': parse_date
            }
        },
        NoneType: {
            datetime.datetime: {
                'left': lambda x: 0,
                'right': serialize_date,
                'result': parse_date
            },
            number_types: {
                'left': lambda x: 0,
                'right': None
            },
            NoneType: {
                'left': lambda x: 0,
                'right': lambda x: 0
            }
        },
    },
    '-': {
        number_types: {
            datetime.datetime: {
                'left': None,
                'right': serialize_date
            },
            number_types: {
                'left': None,
                'right': None
            },
            NoneType: {
                'left': None,
                'right': lambda x: 0
            }
        },
        datetime.datetime: {
            datetime.datetime: {
                'left': serialize_date,
                'right': serialize_date
            },
            number_types: {
                'left': serialize_date,
                'right': None,
                'result': parse_date
            },
            NoneType: {
                'left': serialize_date,
                'right': lambda x: 0,
                'result': parse_date
            }
        },
        NoneType: {
            datetime.datetime: {
                'left': lambda x: 0,
                'right': serialize_date
            },
            number_types: {
                'left': lambda x: 0,
                'right': None
            },
            NoneType: {
                'left': lambda x: 0,
                'right': lambda x: 0
            }
        }
    },
    '*': {
        number_types: {
            datetime.datetime: {
                'left': None,
                'right': serialize_date,
                'result': parse_date
            },
            number_types: {
                'left': None,
                'right': None
            },
            NoneType: {
                'left': None,
                'right': lambda x: 0
            }
        },
        datetime.datetime: {
            datetime.datetime: {
                'left': serialize_date,
                'right': serialize_date
            },
            number_types: {
                'left': serialize_date,
                'right': None,
                'result': parse_date
            },
            NoneType: {
                'left': serialize_date,
                'right': lambda x: 0,
                'result': parse_date
            }
        },
        NoneType: {
            datetime.datetime: {
                'left': lambda x: 0,
                'right': serialize_date,
                'result': parse_date
            },
            number_types: {
                'left': lambda x: 0,
                'right': None
            },
            NoneType: {
                'left': lambda x: 0,
                'right': lambda x: 0
            }
        }
    },
    '/': {
        number_types: {
            datetime.datetime: {
                'left': None,
                'right': serialize_date,
                'result': parse_date
            },
            number_types: {
                'left': None,
                'right': None
            },
            NoneType: {
                'left': None,
                'right': lambda x: 0
            }

        },
        datetime.datetime: {
            datetime.datetime: {
                'left': serialize_date,
                'right': serialize_date
            },
            number_types: {
                'left': serialize_date,
                'right': None,
                'result': parse_date
            },
            NoneType: {
                'left': serialize_date,
                'right': lambda x: 0
            }
        },
        NoneType: {
            datetime.datetime: {
                'left': lambda x: 0,
                'right': serialize_date
            },
            number_types: {
                'left': lambda x: 0,
                'right': None
            },
            NoneType: {
                'left': lambda x: 0,
                'right': lambda x: 0
            }
        }
    }
}


def evaluate_arithmetic(op, lval, rval):
    if isinstance(lval, error.XLError):
        return lval
    if isinstance(rval, error.XLError):
        return rval
    if isinstance(lval, (list, tuple)) or isinstance(rval, (list, tuple)):
        return evaluate_array_arithmetic(op, lval, rval)
    if op == '&':
        return to_string(lval) + to_string(rval)

    lval, ltype = value_and_type(lval)
    if isinstance(lval, error.XLError):
        return lval
    rval, rtype = value_and_type(rval)
    if isinstance(rval, error.XLError):
        return rval
    conversions = IMPLICIT_DATA_TYPE_CONVERSIONS[op]

    if ltype not in conversions:
        return error.VALUE
    if rtype not in conversions[ltype]:
        return error.VALUE

    lconv = conversions[ltype][rtype]['left']
    if lconv is not None:
        lval = lconv(lval)
    rconv = conversions[ltype][rtype]['right']
    if rconv is not None:
        rval = rconv(rval)

    try:
        result = validate_number(OPERATOR_DICT[op](lval, rval))
        if isinstance(result, error.XLError):
            return result
        if 'result' in conversions[ltype][rtype]:
            result = conversions[ltype][rtype]['result'](result)
        return result
    except ZeroDivisionError:
        return error.DIV_ZERO
    except OverflowError:
        return error.NUM


def evaluate_logic(op, lval, rval):
    if isinstance(lval, error.XLError):
        return lval
    if isinstance(rval, error.XLError):
        return rval
    return OPERATOR_DICT[op](ExcelComparator(lval), rval)


def evaluate_array_arithmetic(op, lval, rval):
    """Broadcast singleton dimensions and keep unmatched cells as #N/A.

    Flat vectors are columns and retain flat results when neither input is a
    nested array. Scalar cells use the normal arithmetic conversion rules.
    """
    left_shape = array_shape(lval) if isinstance(lval, (list, tuple)) else (1, 1)
    if isinstance(left_shape, error.XLError):
        return left_shape
    right_shape = array_shape(rval) if isinstance(rval, (list, tuple)) else (1, 1)
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

    nested_result = any(
        isinstance(item, (list, tuple))
        for value in (lval, rval) if isinstance(value, (list, tuple))
        for item in value
    )
    result = []
    # Map result positions to each operand, repeating singleton rows/columns.
    # Unmatched positions in non-singleton dimensions supply #N/A.
    for row in range(shape[0]):
        values = [
            evaluate_arithmetic(op, array_value(lval, left_shape, row, column),
                                array_value(rval, right_shape, row, column))
            for column in range(shape[1])
        ]
        result.append(values if nested_result else values[0])
    return result
