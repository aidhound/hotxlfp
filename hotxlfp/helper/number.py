# -*- coding: utf-8 -*-
import cmath
from .._compat import number_types, string_types
from ..formulas import error

def to_number(number):
    if isinstance(number, number_types):
        # Integers are always finite; avoid converting large ints to floats.
        if isinstance(number, int) or cmath.isfinite(number):
            return number
        return error.NUM
    if isinstance(number, string_types):
        try:
            return int(number)
        except ValueError:
            try:
                return to_number(float(number))
            except ValueError:
                pass
    if isinstance(number, bool):
        return 1 if number else 0
    return number

def invert_number(number):
    number = to_number(number)
    return number if isinstance(number, error.XLError) else -1 * number
