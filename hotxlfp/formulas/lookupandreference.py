# -*- coding: utf-8 -*-
import fnmatch
from . import dispatcher
from . import error
from .._compat import string_types


@dispatcher.register_for('CHOOSE')
def CHOOSE(*args):
    if (len(args) < 2):
        return error.NOT_AVAILABLE

    index = args[0]
    if (index < 1 or index > 254):
        return error.VALUE

    if (len(args) < index + 1):
        return error.VALUE

    return args[index]


@dispatcher.register_for('MATCH')
def MATCH(lookup_value, lookup_array, match_type=1):
    if not lookup_value and not lookup_array:
        return error.NOT_AVAILABLE

    if not isinstance(lookup_array, list):
        return error.NOT_AVAILABLE

    if match_type not in (-1, 0, 1):
        return error.NOT_AVAILABLE

    index = None
    index_value = None
    for idx in range(len(lookup_array)):
        if match_type == 1:
            if lookup_array[idx] == lookup_value:
                return idx + 1
            elif lookup_array[idx] < lookup_value:
                if not index_value:
                    index = idx + 1
                    index_value = lookup_array[idx]
                elif lookup_array[idx] > index_value:
                    index = idx + 1
                    index_value = lookup_array[idx]
        elif match_type == 0:
            if isinstance(lookup_value, string_types):
                if fnmatch.fnmatch(lookup_array[idx].lower(), lookup_value.lower()):
                    return idx + 1
            else:
                if lookup_array[idx] == lookup_value:
                    return idx + 1
        elif match_type == -1:
            if lookup_array[idx] == lookup_value:
                return idx + 1
            elif lookup_array[idx] > lookup_value:
                if not index_value:
                    index = idx + 1
                    index_value = lookup_array[idx]
                elif lookup_array[idx] < index_value:
                    index = idx + 1
                    index_value = lookup_array[idx]

    return index if index else error.NOT_AVAILABLE
