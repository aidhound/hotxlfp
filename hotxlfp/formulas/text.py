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
from .utils import DEFAULT
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
    if isinstance(text, error.XLError):
        return text
    if text is None:
        text = ''
    if not isinstance(text, string_types):
        text = str(text)
    return ''.join(c for c in text if ord(c) > 31)


@dispatcher.register_for('CONCAT', 'CONCATENATE')
def CONCATENATE(*args):
    return ''.join(utils.iflatten(args))


@dispatcher.register_for('LEN')
def LEN(text):
    if isinstance(text, error.XLError):
        return text
    if text is None:
        return 0
    if not isinstance(text, string_types):
        text = str(text)
    return len(text)


@dispatcher.register_for('LOWER')
def LOWER(text):
    if isinstance(text, error.XLError):
        return text
    if text is None:
        text = ''
    if not isinstance(text, string_types):
        text = str(text)
    return text.lower()


@dispatcher.register_for('UPPER')
def UPPER(text):
    if isinstance(text, error.XLError):
        return text
    if text is None:
        text = ''
    if not isinstance(text, string_types):
        text = str(text)
    return text.upper()


@dispatcher.register_for('PROPER')
def PROPER(text):
    if isinstance(text, error.XLError):
        return text
    if text is None:
        text = ''
    if not isinstance(text, string_types):
        text = str(text)
    return text.title()


@dispatcher.register_for('SUBSTITUTE')
def SUBSTITUTE(text, old_text, new_text, instance_num=DEFAULT):
    if instance_num is not DEFAULT:
        instance_num = utils.parse_number(instance_num)
        if isinstance(instance_num, error.XLError):
            return instance_num
        if instance_num <= 0:
            return error.VALUE
    if not text or not old_text or not new_text:
        return text
    if instance_num is DEFAULT:
        return text.replace(old_text, new_text)
    else:
        len_old = len(old_text)
        ocurrences = 0
        for i in range(len(text) - len_old + 1):
            if text[i:i + len_old] == old_text:
                ocurrences += 1
                if ocurrences == instance_num:
                    return text[0:i] + new_text + text[i + len_old:]
        return text


@dispatcher.register_for('TEXTJOIN')
def TEXTJOIN(delimiter, ignore_empty, *args):
    if not isinstance(delimiter, string_types):
        return error.VALUE
    if ignore_empty:
        gen = (words for words in utils.iflatten(args) if words is not None)
    else:
        gen = (words if words is not None else '' for words in utils.iflatten(args))
    return delimiter.join(gen)
