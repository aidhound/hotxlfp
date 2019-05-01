# -*- coding: utf-8 -*-
from __future__ import division
import datetime
from . import error
from ..helper.number import to_number
from .utils import OPERATOR_DICT, serialize_date, parse_date, date_1900
from .._compat import number_types, string_types


NoneType = type(None)


class ExcelComparator(object):

    def __init__(self, value):
        self.value = value
        if isinstance(value, datetime.datetime):
            self.value = serialize_date(value)

    def convert_other(self, other):
        if other is None:
            if isinstance(self.value, bool):
                other = False
            elif isinstance(self.value, number_types):
                other = type(self.value)(0)  # so it's the same number type
            elif isinstance(self.value, string_types):
                other = ''
        elif isinstance(other, datetime.datetime):
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
        if type(self.value) != type(other):
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
        if type(self.value) != type(other):
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


class ExcelArrayOps(object):

    def __init__(self, arr):
        self.arr = arr

    def adapt_value(self, value):
        if isinstance(value, list) and len(value) == 1:
            value = value[0]
        if not isinstance(value, list):
            value = [value for i in range(len(self.arr))]
        return value

    def __add__(self, value):
        value = self.adapt_value(value)
        if len(value) != len(self.arr):
            return error.VALUE
        return [evaluate_arithmetic('+', a, b) for a, b in zip(self.arr, value)]

    __radd__ = __add__

    def __sub__(self, value):
        value = self.adapt_value(value)
        if len(value) != len(self.arr):
            return error.VALUE
        return [evaluate_arithmetic('-', a, b) for a, b in zip(self.arr, value)]

    def __rsub__(self, value):
        value = self.adapt_value(value)
        if len(value) != len(self.arr):
            return error.VALUE
        return [evaluate_arithmetic('-', b, a) for a, b in zip(self.arr, value)]

    def __mul__(self, value):
        value = self.adapt_value(value)
        if len(value) != len(self.arr):
            return error.VALUE
        return [evaluate_arithmetic('*', a, b) for a, b in zip(self.arr, value)]

    __rmul__ = __mul__

    def __truediv__(self, value):
        value = self.adapt_value(value)
        if len(value) != len(self.arr):
            return error.VALUE
        return [evaluate_arithmetic('/', a, b) for a, b in zip(self.arr, value)]

    def __rtruediv__(self, value):
        value = self.adapt_value(value)
        if len(value) != len(self.arr):
            return error.VALUE
        return [evaluate_arithmetic('/', b, a) for a, b in zip(self.arr, value)]


def value_and_type(value):
    if isinstance(value, number_types):
        return (value, number_types)
    if isinstance(value, datetime.datetime):
        return (value, datetime.datetime)
    if isinstance(value, string_types):
        value = to_number(value)
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
    if isinstance(lval, list):
        return OPERATOR_DICT[op](ExcelArrayOps(lval), rval)
    if isinstance(rval, list):
        return OPERATOR_DICT[op](lval, ExcelArrayOps(rval))

    lval, ltype = value_and_type(lval)
    rval, rtype = value_and_type(rval)
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
        result = OPERATOR_DICT[op](lval, rval)
        if 'result' in conversions[ltype][rtype]:
            result = conversions[ltype][rtype]['result'](result)
        return result
    except ZeroDivisionError:
        return error.DIV_ZERO


def evaluate_logic(op, lval, rval):
    return OPERATOR_DICT[op](ExcelComparator(lval), rval)
