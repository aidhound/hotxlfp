# -*- coding: utf-8 -*-
"""
inspired by:
https://github.com/sutoiku/formula.js/blob/master/lib/math-trig.js
"""
from __future__ import division
import math
from functools import reduce
import operator
from . import dispatcher
from . import error
from . import utils
from ..helper.number import to_number
from .._compat import string_types


@dispatcher.register_for('CHAR')
def CHAR(number):
    number = utils.parse_number(number)
    if isinstance(number, error.XLError):
        return number
    return chr(number)


@dispatcher.register_for('CODE')
def CODE(char):
    return ord(char)


@dispatcher.register_for('CLEAN')
def CLEAN(text):
    if not isinstance(text, string_types):
        return error.VALUE    
    return ''.join(c for c in text if ord(c) > 31)


@dispatcher.register_for('CONCAT', 'CONCATENATE')
def CONCATENATE(*args):
    return ''.join(utils.iflatten(args))


@dispatcher.register_for('LOWER')
def LOWER(text):
    if not isinstance(text, string_types):
        return error.VALUE
    return text.lower()


@dispatcher.register_for('UPPER')
def UPPER(text):
    if not isinstance(text, string_types):
        return error.VALUE
    return text.upper()

@dispatcher.register_for('PROPER')
def PROPER(text):
    if not isinstance(text, string_types):
        return error.VALUE
    return text.title()
