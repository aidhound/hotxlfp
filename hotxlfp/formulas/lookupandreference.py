# -*- coding: utf-8 -*-
import fnmatch
from . import dispatcher
from . import error
from . import utils
from .utils import DEFAULT
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


@dispatcher.register_for('INDEX')
def INDEX(arr, row_num=DEFAULT, column_num=DEFAULT, area_num=DEFAULT):
    if row_num is None:
        row_num = DEFAULT
    if column_num is None:
        column_num = DEFAULT

    if arr is None or (row_num is DEFAULT and column_num is DEFAULT):
        return error.VALUE

    if not isinstance(arr, list):
        arr = [[arr]]

    bidimensional = isinstance(arr[0], list)

    if row_num is not DEFAULT:
        row_num = utils.parse_number(row_num)
        if isinstance(row_num, error.XLError):
            return row_num

    if column_num is not DEFAULT:
        column_num = utils.parse_number(column_num)
        if isinstance(column_num, error.XLError):
            return column_num
    try:
        if row_num is DEFAULT:
            if bidimensional:
                return [row[column_num - 1] for row in arr]
            else:
                return arr[column_num - 1]
        if column_num is DEFAULT:
            return arr[row_num - 1]
        if row_num == 0 and column_num == 0:
            return arr
        if row_num == 0:
            return [row[column_num - 1] for row in arr]
        if column_num == 0:
            return arr[row_num - 1]
        if not bidimensional and column_num == 1:
            return arr[row_num -1]
        return arr[row_num - 1][column_num - 1]
    except (IndexError, TypeError):
        return error.REF
