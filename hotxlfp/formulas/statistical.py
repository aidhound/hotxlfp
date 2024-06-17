# -*- coding: utf-8 -*-
"""
inspired by:
https://github.com/sutoiku/formula.js/blob/master/lib/statistical.js
"""
from __future__ import division
from . import dispatcher
from . import error
from . import utils
from .._compat import number_types, statistics
from ..helper.number import to_number


@dispatcher.register_for('AVERAGE')
def AVERAGE(*args):
    return statistics.mean(utils.inumbers(args, try_parse=True))


@dispatcher.register_for('AVEDEV')
def AVEDEV(*args):
    args = utils.flatten(args)
    average = AVERAGE(*args)
    return sum(abs(arg - average) for arg in utils.iflatten(args)) / len(args)


@dispatcher.register_for('AVERAGEA')
def AVERAGEA(*args):
    return statistics.mean(utils.inumbers(args, try_parse=True, text_is_zero=True))


@dispatcher.register_for('AVERAGEIF')
def AVERAGEIF(args, criteria, average_range=None):
    average_range = average_range or args
    args = utils.flatten(args)
    average_range = utils.iparse_number_array(utils.flatten(average_range))
    if isinstance(average_range, error.XLError):
        return average_range
    average_range = list(average_range)
    average_count = 0
    result = 0
    predicate = utils.parse_criteria(criteria)

    for i, arg_i in enumerate(args):
        if (predicate(args[i])):
            result += average_range[i]
            average_count += 1
    return result / average_count


@dispatcher.register_for('COUNT')
def COUNT(*args):
    return len(utils.flatten(args))


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
    return max(utils.inumbers(args))


@dispatcher.register_for('MAXA')
def MAXA(*args):
    return max(utils.inumbers(args, try_parse=True, text_is_zero=True))


@dispatcher.register_for('MEDIAN')
def MEDIAN(*args):
    return statistics.median(utils.inumbers(args, try_parse=True))


@dispatcher.register_for('MIN')
def MIN(*args):
    return min(utils.inumbers(args))


@dispatcher.register_for('MINA')
def MINA(*args):
    return min(utils.inumbers(args, try_parse=True, text_is_zero=True))


@dispatcher.register_for('MODE', 'MODE.SNGL')
def MODE(*args):
    return statistics.mode(utils.inumbers(args, try_parse=True))


@dispatcher.register_for('VAR', 'VAR.S')
def VAR(*args):
    return statistics.variance(utils.inumbers(args))


@dispatcher.register_for('VAR.P', 'VARP')
def VAR_P(*args):
    return statistics.pvariance(utils.inumbers(args))


@dispatcher.register_for('VARA')
def VARA(*args):
    return statistics.variance(utils.inumbers(args, try_parse=True, text_is_zero=True))


@dispatcher.register_for('STDEV', 'STDEV.S')
def STDEV(*args):
    return statistics.stdev(utils.inumbers(args))


@dispatcher.register_for('STDEV.P', 'STDEVP')
def STDEV_P(*args):
    return statistics.pstdev(utils.inumbers(args))


@dispatcher.register_for('STDEVA')
def STDEVA(*args):
    return statistics.stdev(utils.inumbers(args, try_parse=True, text_is_zero=True))


@dispatcher.register_for('STDEVPA')
def STDEVPA(*args):
    return statistics.pstdev(utils.inumbers(args, try_parse=True, text_is_zero=True))


@dispatcher.register_for('HARMEAN')
def HARMEAN(*args):
    return statistics.harmonic_mean(utils.inumbers(args))


@dispatcher.register_for('GEOMEAN')
def GEOMEAN(*args):
    return statistics.geometric_mean(utils.inumbers(args))


@dispatcher.register_for('AVERAGEIFS')
def AVERAGEIFS(average_range, *criteria):
    if len(criteria) % 2 != 0:
        return error.ERROR
    range_and_preds = list(zip(criteria[::2], (utils.parse_criteria(criterion) for criterion in criteria[1::2])))
    sum_value = 0
    count_value = 0
    for i, a in enumerate(average_range):
        if all(pred(criteria_range[i]) for criteria_range, pred in range_and_preds):
            sum_value += a
            count_value += 1
    if count_value == 0:
        return error.DIV0
    return sum_value / count_value


@dispatcher.register_for('MAXIFS')
def MAXIFS(sum_args, *criteria):
    if len(criteria) % 2 != 0:
        return error.ERROR
    range_and_preds = list(zip(criteria[::2], (utils.parse_criteria(criterion) for criterion in criteria[1::2])))
    b = 0
    for i, a in enumerate(sum_args):
        if all(pred(criteria_range[i]) for criteria_range,pred in range_and_preds):
            if a > b: 
                b = a
    return b


@dispatcher.register_for('SLOPE')
def SLOPE(*yx):
    if len(yx) % 2 != 0:
        return error.DIV_ZERO

    midpoint = len(yx) // 2
    ys = yx[:midpoint]
    xs = yx[midpoint:]

    if len(ys) != len(xs) or len(ys) == 0 or len(xs) == 0:
        return error.DIV_ZERO

    ys = list(ys)
    xs = list(xs)

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