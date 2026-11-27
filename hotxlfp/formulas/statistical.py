# -*- coding: utf-8 -*-
"""
inspired by:
https://github.com/sutoiku/formula.js/blob/master/lib/statistical.js
"""
from collections import Counter
import datetime
import math
import statistics
from . import dispatcher
from . import error
from . import utils
from .._compat import number_types, string_types
from ..helper.number import to_number


@dispatcher.register_for('AVERAGE')
def AVERAGE(*args):
    try:
        return statistics.mean(utils.inumbers(args, try_parse=True))
    except statistics.StatisticsError:
        return error.DIV_ZERO


@dispatcher.register_for('AVEDEV')
def AVEDEV(*args):
    args = utils.numbers(args, try_parse=True)
    average = AVERAGE(*args)
    if isinstance(average, error.XLError):
        return average
    return sum(abs(arg - average) for arg in args) / len(args)


@dispatcher.register_for('AVERAGEA')
def AVERAGEA(*args):
    try:
        return statistics.mean(
            utils.inumbers(args, try_parse=True, text_is_zero=True)
        )
    except statistics.StatisticsError:
        return error.DIV_ZERO


@dispatcher.register_for('AVERAGEIF')
def AVERAGEIF(args, criteria, average_range=None):
    if average_range is None:
        average_range = args
    elif isinstance(args, (list, tuple)) and isinstance(average_range, (list, tuple)):
        criteria_shape = utils.array_shape(args)
        if isinstance(criteria_shape, error.XLError):
            return criteria_shape
        average_shape = utils.array_shape(average_range)
        if isinstance(average_shape, error.XLError):
            return average_shape
        if criteria_shape != average_shape:
            return error.VALUE
    args = utils.flatten(args)
    average_range = utils.flatten(average_range)
    if len(average_range) < len(args):
        return error.VALUE
    predicate = utils.parse_criteria(criteria)
    values = [average_range[i] for i, value in enumerate(args) if predicate(value)]
    return AVERAGE(values)


@dispatcher.register_for('COUNT')
def COUNT(*args):
    count = 0
    for arg in args:
        if isinstance(arg, (list, tuple)):
            values = (
                value
                for value in utils.iflatten(arg)
                if not isinstance(value, bool)
            )
        else:
            values = (arg,)

        for value in values:
            value = to_number(value)
            if isinstance(value, string_types):
                value = utils.parse_date(value)
            if isinstance(value, number_types) or isinstance(value, datetime.date):
                count += 1
    return count


@dispatcher.register_for('COUNTA')
def COUNTA(*args):
    return sum(1 for a in utils.iflatten(args) if (a is not None and a != ''))


@dispatcher.register_for('COUNTBLANK')
def COUNTBLANK(*args):
    return sum(1 for a in utils.iflatten(args) if (a is None or a == ''))


@dispatcher.register_for('COUNTIF')
def COUNTIF(args, criteria):
    predicate = utils.parse_criteria(criteria)
    return sum(1 for a in utils.iflatten(args) if predicate(a))


@dispatcher.register_for('MAX')
def MAX(*args):
    return max(utils.inumbers(args, try_parse=True), default=0)


@dispatcher.register_for('MAXA')
def MAXA(*args):
    return max(utils.inumbers(args, try_parse=True, text_is_zero=True), default=0)


@dispatcher.register_for('MEDIAN')
def MEDIAN(*args):
    try:
        return statistics.median(utils.inumbers(args, try_parse=True))
    except statistics.StatisticsError:
        return error.NUM


@dispatcher.register_for('MIN')
def MIN(*args):
    return min(utils.inumbers(args, try_parse=True), default=0)


@dispatcher.register_for('MINA')
def MINA(*args):
    return min(utils.inumbers(args, try_parse=True, text_is_zero=True), default=0)


@dispatcher.register_for('MODE', 'MODE.SNGL')
def MODE(*args):
    counts = Counter(utils.inumbers(args, try_parse=True))
    if not counts:
        return error.NOT_AVAILABLE
    value, frequency = counts.most_common(1)[0]
    return value if frequency > 1 else error.NOT_AVAILABLE


@dispatcher.register_for('VAR', 'VAR.S')
def VAR(*args):
    try:
        return statistics.variance(utils.inumbers(args, try_parse=True))
    except statistics.StatisticsError:
        return error.DIV_ZERO


@dispatcher.register_for('VAR.P', 'VARP')
def VAR_P(*args):
    try:
        return statistics.pvariance(utils.inumbers(args, try_parse=True))
    except statistics.StatisticsError:
        return error.DIV_ZERO


@dispatcher.register_for('VARA')
def VARA(*args):
    try:
        return statistics.variance(utils.inumbers(args, try_parse=True, text_is_zero=True))
    except statistics.StatisticsError:
        return error.DIV_ZERO


@dispatcher.register_for('STDEV', 'STDEV.S')
def STDEV(*args):
    try:
        return statistics.stdev(utils.inumbers(args, try_parse=True))
    except statistics.StatisticsError:
        return error.DIV_ZERO


@dispatcher.register_for('STDEV.P', 'STDEVP')
def STDEV_P(*args):
    try:
        return statistics.pstdev(utils.inumbers(args, try_parse=True))
    except statistics.StatisticsError:
        return error.DIV_ZERO


@dispatcher.register_for('STDEVA')
def STDEVA(*args):
    try:
        return statistics.stdev(utils.inumbers(args, try_parse=True, text_is_zero=True))
    except statistics.StatisticsError:
        return error.DIV_ZERO


@dispatcher.register_for('STDEVPA')
def STDEVPA(*args):
    try:
        return statistics.pstdev(utils.inumbers(args, try_parse=True, text_is_zero=True))
    except statistics.StatisticsError:
        return error.DIV_ZERO


@dispatcher.register_for('HARMEAN')
def HARMEAN(*args):
    values = utils.numbers(args, try_parse=True)
    if not values:
        return error.NOT_AVAILABLE
    # Python allows zero in harmonic_mean; Excel requires positive values.
    if 0 in values:
        return error.NUM
    try:
        return statistics.harmonic_mean(values)
    except (statistics.StatisticsError, OverflowError):
        return error.NUM


@dispatcher.register_for('GEOMEAN')
def GEOMEAN(*args):
    # Read all input errors before checking the numeric domain.
    values = utils.numbers(args, try_parse=True)
    try:
        return statistics.geometric_mean(values)
    except (statistics.StatisticsError, OverflowError):
        return error.NUM


@dispatcher.register_for('AVERAGEIFS')
def AVERAGEIFS(average_range, *criteria):
    if not criteria or len(criteria) % 2 != 0:
        return error.ERROR

    average_shape = utils.array_shape(average_range)
    if isinstance(average_shape, error.XLError):
        return average_shape

    range_and_preds = []
    for criteria_range, criterion in zip(criteria[::2], criteria[1::2]):
        criteria_shape = utils.array_shape(criteria_range)
        if isinstance(criteria_shape, error.XLError):
            return criteria_shape
        if criteria_shape != average_shape:
            return error.VALUE
        range_and_preds.append((utils.flatten(criteria_range), utils.parse_criteria(criterion)))

    values = [
        value for i, value in enumerate(utils.iflatten(average_range))
        if all(pred(criteria_range[i]) for criteria_range, pred in range_and_preds)
    ]
    return AVERAGE(values)


@dispatcher.register_for('MAXIFS')
def MAXIFS(sum_args, *criteria):
    if not criteria or len(criteria) % 2 != 0:
        return error.ERROR

    max_shape = utils.array_shape(sum_args)
    if isinstance(max_shape, error.XLError):
        return max_shape

    range_and_preds = []
    for criteria_range, criterion in zip(criteria[::2], criteria[1::2]):
        criteria_shape = utils.array_shape(criteria_range)
        if isinstance(criteria_shape, error.XLError):
            return criteria_shape
        if criteria_shape != max_shape:
            return error.VALUE
        range_and_preds.append((utils.flatten(criteria_range), utils.parse_criteria(criterion)))

    values = (
        value for i, value in enumerate(utils.iflatten(sum_args))
        if all(pred(criteria_range[i]) for criteria_range, pred in range_and_preds)
    )
    max_value = utils.DEFAULT
    for value in values:
        value = to_number(value)
        if isinstance(value, error.XLError):
            return value
        if not isinstance(value, number_types):
            continue
        if max_value is utils.DEFAULT or value > max_value:
            max_value = value
    return 0 if max_value is utils.DEFAULT else max_value


@dispatcher.register_for('SLOPE')
@utils.propagate_errors()
def SLOPE(*yx):
    """Accept two datasets or legacy y-values followed by x-values."""
    array_input = False
    if len(yx) == 2:
        array_input = any(isinstance(value, (list, tuple)) for value in yx)
        ys, xs = map(utils.flatten, yx)
        # Excel checks dataset lengths before errors inside the arrays.
        if len(ys) != len(xs):
            return error.NOT_AVAILABLE
    else:
        if len(yx) % 2 != 0:
            return error.DIV_ZERO
        midpoint = len(yx) // 2
        ys = list(yx[:midpoint])
        xs = list(yx[midpoint:])

    # Convert without filtering so x/y positions remain aligned.
    for values in (ys, xs):
        for index, value in enumerate(values):
            value = to_number(value)
            if isinstance(value, error.XLError):
                return value
            values[index] = value

    pairs = []
    for y, x in zip(ys, xs):
        if array_input and (isinstance(y, bool) or isinstance(x, bool)):
            continue
        if isinstance(y, number_types) and isinstance(x, number_types):
            pairs.append((y, x))
    if len(pairs) < 2:
        return error.DIV_ZERO
    ys, xs = zip(*pairs)

    # Translating the coordinates preserves slope and reduces cancellation.
    ys = [y - ys[0] for y in ys]
    xs = [x - xs[0] for x in xs]
    n = len(ys)
    sum_x = sum(xs)
    sum_y = sum(ys)
    sum_x_sq = sum(x ** 2 for x in xs)
    sum_xy = sum(x * y for x, y in zip(xs, ys))

    denominator = (n * sum_x_sq) - (sum_x ** 2)
    if denominator == 0:
        return error.DIV_ZERO

    slope = ((n * sum_xy) - (sum_x * sum_y)) / denominator
    return slope


@dispatcher.register_for('LARGE')
def LARGE(arr, n):
    """ 
    The nth largest value in an array.
    """
    n = utils.parse_number(n)
    if isinstance(n, error.XLError):
        return n
    if n < 1:
        return error.NUM
    values = utils.numbers(arr, try_parse=True)
    if n > len(values):
        return error.NUM
    return sorted(values)[-math.ceil(n)]
