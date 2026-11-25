# -*- coding: utf-8 -*-
import math
from decimal import Decimal
from ..formulas import error


def to_string(value):
    """Coerce a text argument, keeping calculation errors as values.

    Finite floats use 15 significant digits and fixed notation when it fits
    in 20 characters (excluding the sign), as measured in Excel concatenation.
    Native integers retain their full precision.
    """
    if value is None:
        return ''
    if isinstance(value, (str, error.XLError)):
        return value
    if isinstance(value, bool):
        return 'TRUE' if value else 'FALSE'
    if isinstance(value, float) and math.isfinite(value):
        if value == 0:
            return '0'
        significant = format(value, '.15g')
        fixed = format(Decimal(significant), 'f')
        if '.' in fixed:
            fixed = fixed.rstrip('0').rstrip('.')
        return fixed if len(fixed.lstrip('-')) <= 20 else significant.upper()
    return str(value)
