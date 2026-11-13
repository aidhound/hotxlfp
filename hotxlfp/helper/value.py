# -*- coding: utf-8 -*-
from .._compat import number_types
from .number import validate_number


def validate_value(value):
    """Validate scalar and nested array values without text conversion."""
    if isinstance(value, number_types):
        return validate_number(value)
    value_type = type(value)
    if value_type in (list, tuple):
        return value_type(validate_value(item) for item in value)
    return value
