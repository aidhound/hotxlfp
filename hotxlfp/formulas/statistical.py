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
