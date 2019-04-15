# -*- coding: utf-8 -*-
from __future__ import division
from . import dispatcher
from . import error
from . import utils


@dispatcher.register_for('PV')
def PV(rate, periods, payment, future=None, type=None):
    if future is None:
        future = 0
    if type is None:
        type = 0
    rate = utils.parse_number(rate)
    periods = utils.parse_number(periods)
    payment = utils.parse_number(payment)
    future = utils.parse_number(future)
    type = utils.parse_number(type)
    if utils.any_is_error((rate, periods, payment, future, type)):
        return error.VALUE
    # Return present value
    if rate == 0:
        return -payment * periods - future
    else:
        rate_exp_periods = (1 + rate)**periods
        return (((1 - rate_exp_periods) / rate) * payment * (1 + rate * type) - future) / rate_exp_periods
