# -*- coding: utf-8 -*-
from __future__ import division
from . import dispatcher
from . import error
from . import utils
from .utils import DEFAULT


@dispatcher.register_for('HEX2DEC')
def HEX2DEC(hex):
    try:
        dec = int(hex, 16)
        return (dec - 1099511627776) if (dec >= 549755813888) else dec
    except ValueError:
        return error.VALUE


@dispatcher.register_for('DEC2HEX')
def DEC2HEX(dec, places=DEFAULT):
    dec = utils.parse_number(dec)
    if isinstance(dec, error.XLError):
        return dec
    if places is not DEFAULT:
        places = utils.parse_number(places)
        if isinstance(places, error.XLError):
            return places
        if places < 0:
            return error.NUM
    if dec < 0:
        places = DEFAULT
        dec = dec + 1099511627776
    try:
        result = (hex(dec)[2:])
        if result[-1] == 'L':
            result = result[:-1]
        if places is not DEFAULT:
            if len(result) > places:
                return error.NUM
            result = result.rjust(places, '0')
        return result.upper()
    except ValueError:
        return error.VALUE


@dispatcher.register_for('COMPLEX')
def COMPLEX(real, imaginary):
    real = utils.parse_number(real)
    imaginary = utils.parse_number(imaginary)
    if utils.any_is_error((real, imaginary)):
        return error.VALUE
    return complex(real, imaginary)


@dispatcher.register_for('DELTA')
def DELTA(number1, number2):
    number1 = utils.parse_number(number1)
    number2 = utils.parse_number(number2)
    if utils.any_is_error((number1, number2)):
        return error.VALUE
    return 1 if number1 == number2 else 0
