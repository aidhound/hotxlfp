# -*- coding: utf-8 -*-
from .._compat import number_types, string_types

def to_number(number):
    if isinstance(number, number_types):
        return number
    if isinstance(number, string_types):
        try:
            return int(number)
        except ValueError:
            try:
                return float(number)
            except ValueError:
                pass
    if isinstance(number, bool):
        return 1 if number else 0
    return number

def invert_number(number):
    return -1 * to_number(number)
