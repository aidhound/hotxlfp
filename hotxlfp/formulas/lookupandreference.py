# -*- coding: utf-8 -*-
import fnmatch
import datetime
from itertools import islice
from . import dispatcher
from . import error
from . import utils
from .utils import DEFAULT
from .._compat import number_types, string_types
from ..helper.number import validate_number


@dispatcher.register_for('TOCOL')
@utils.propagate_errors()
def TOCOL(array, ignore=0, scan_by_column=False):
    return reshape_array(array, ignore, scan_by_column, as_column=True)


@dispatcher.register_for('TOROW')
@utils.propagate_errors()
def TOROW(array, ignore=0, scan_by_column=False):
    return reshape_array(array, ignore, scan_by_column, as_column=False)


@dispatcher.register_for('UNIQUE')
@utils.propagate_errors()
def UNIQUE(array, by_col=False, exactly_once=False):
    by_col = parse_array_flag(by_col)
    exactly_once = parse_array_flag(exactly_once)
    for value in (by_col, exactly_once):
        if isinstance(value, error.XLError):
            return value
    if not isinstance(array, (list, tuple)):
        array = [[array]]
    shape = utils.array_shape(array)
    if isinstance(shape, error.XLError):
        return shape
    if 0 in shape:
        return error.CALC

    def value_key(value):
        """Keep Excel's value categories separate during duplicate comparisons."""
        if isinstance(value, error.XLError):
            return 'error', str(value)
        if value is None or isinstance(value, bool):
            return type(value), value
        if isinstance(value, datetime.date):
            try:
                value = utils.serialize_date(value)
            except (TypeError, ValueError, OverflowError):
                return error.VALUE
        if isinstance(value, number_types):
            return 'number', value
        if isinstance(value, string_types):
            return 'text', value.casefold()
        return error.VALUE

    if any(isinstance(row, (list, tuple)) for row in array):
        rows = array
    else:
        rows = ((value,) for value in array)
    records = zip(*rows) if by_col else rows
    distinct = {}
    for record in records:
        key = tuple(value_key(value) for value in record)
        for value in key:
            if isinstance(value, error.XLError):
                return value
        if key not in distinct:
            distinct[key] = [record, 0]
        distinct[key][1] += 1
    selected = [record for record, count in distinct.values()
                if not exactly_once or count == 1]
    if not selected:
        return error.CALC
    row_count = shape[0] if by_col else len(selected)
    column_count = len(selected) if by_col else shape[1]
    if row_count > 1048576 or column_count > 16384:
        return error.NUM
    result = zip(*selected) if by_col else selected
    # Blank cells display as zero, but remain distinct from numeric zero while comparing.
    return [[0 if value is None else value for value in row] for row in result]


def parse_array_flag(value):
    """Coerce a logical option, accepting TRUE/FALSE text but not numeric text."""
    if value is None:
        return False
    if isinstance(value, error.XLError):
        return value
    if isinstance(value, number_types):
        value = validate_number(value)
        return value if isinstance(value, error.XLError) else bool(value)
    if isinstance(value, string_types) and value.upper() in ('TRUE', 'FALSE'):
        return value.upper() == 'TRUE'
    return error.VALUE


def reshape_array(array, ignore, scan_by_column, *, as_column):
    """Validate an array and its options, then build one row or one column."""
    ignore = utils.parse_number(0 if ignore is None else ignore)
    scan_by_column = parse_array_flag(scan_by_column)
    for value in (ignore, scan_by_column):
        if isinstance(value, error.XLError):
            return value
    ignore = int(ignore)
    if not 0 <= ignore <= 3:
        return error.VALUE
    if not isinstance(array, (list, tuple)):
        array = [[array]]
    shape = utils.array_shape(array)
    if isinstance(shape, error.XLError):
        return shape
    limit = 1048576 if as_column else 16384
    if ignore == 0 and shape[0] * shape[1] > limit:
        return error.NUM
    if not any(isinstance(row, (list, tuple)) for row in array):
        array = ((value,) for value in array)
    # A single column has the same scan order in either direction.
    values = utils.scan_array(array, ignore, scan_by_column and shape[1] > 1)
    if as_column:
        result = [[value] for value in islice(values, limit + 1)]
        count = len(result)
    else:
        row = list(islice(values, limit + 1))
        result = [row]
        count = len(row)
    if count > limit:
        return error.NUM
    return result if count else error.CALC


@dispatcher.register_for('ROWS')
def ROWS(*args):
    if len(args) != 1:
        return error.NOT_AVAILABLE

    array = args[0]
    if isinstance(array, error.XLError):
        return array
    if not isinstance(array, (list, tuple)):
        return error.VALUE

    return len(array)


@dispatcher.register_for('CHOOSE')
def CHOOSE(*args):
    if (len(args) < 2):
        return error.NOT_AVAILABLE

    index = args[0]
    if isinstance(index, error.XLError):
        return index
    if (index < 1 or index > 254):
        return error.VALUE

    if (len(args) < index + 1):
        return error.VALUE

    return args[index]


@dispatcher.register_for('MATCH')
@utils.propagate_errors()
def MATCH(lookup_value, lookup_array, match_type=1):
    if not lookup_value and not lookup_array:
        return error.NOT_AVAILABLE

    if not isinstance(lookup_array, list):
        return error.NOT_AVAILABLE

    if match_type not in (-1, 0, 1):
        return error.NOT_AVAILABLE

    if len(lookup_array) == 1 and isinstance(lookup_array[0], list):
        lookup_array = lookup_array[0]
    elif lookup_array and all(isinstance(row, list) and len(row) == 1
                              for row in lookup_array):
        lookup_array = [row[0] for row in lookup_array]

    if any(isinstance(value, list) for value in lookup_array):
        return error.NOT_AVAILABLE

    index = None
    index_value = None
    for idx in range(len(lookup_array)):
        if isinstance(lookup_array[idx], error.XLError):
            continue
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
@utils.propagate_errors()
def INDEX(arr, row_num=DEFAULT, column_num=DEFAULT, area_num=DEFAULT):
    if row_num is None:
        row_num = DEFAULT
    if column_num is None:
        column_num = DEFAULT

    if arr is None or (row_num is DEFAULT and column_num is DEFAULT):
        return error.VALUE

    if not isinstance(arr, list):
        arr = [[arr]]

    if not arr:
        return error.REF

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
        if row_num is not DEFAULT and row_num < 0:
            return error.REF
        if column_num is not DEFAULT and column_num < 0:
            return error.REF

        # A vector uses a single position when one coordinate is omitted.
        if bidimensional:
            if len(arr) == 1 and (row_num is DEFAULT or column_num is DEFAULT):
                arr = arr[0]
                bidimensional = False
            elif column_num is DEFAULT and all(isinstance(row, list) and len(row) == 1
                                               for row in arr):
                arr = [row[0] for row in arr]
                bidimensional = False

        if not bidimensional and (row_num is DEFAULT or column_num is DEFAULT):
            position = column_num if row_num is DEFAULT else row_num
            return arr if position == 0 else arr[position - 1]

        if row_num is DEFAULT:
            return [row[column_num - 1] for row in arr]
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
