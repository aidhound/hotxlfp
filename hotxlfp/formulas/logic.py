# -*- coding: utf-8 -*-
"""
inspired by:
https://github.com/sutoiku/formula.js/blob/master/lib/logical.js
"""
from . import dispatcher
from . import error
from . import utils


@dispatcher.register_for('AND')
def AND(*args):
    args = utils.iflatten(args)
    return all(args)


@dispatcher.register_for('IF')
def IF(test, then, otherwise):
    return then if test else otherwise


@dispatcher.register_for('IFERROR')
def IFERROR(value, value_if_error):
    return value if not isinstance(value, error.XLError) else value_if_error


@dispatcher.register_for('IFNA')
def IFNA(value, value_if_na):
    return value if value != error.NOT_AVAILABLE else value_if_na


@dispatcher.register_for('NOT')
def NOT(boolean):
    return not boolean


@dispatcher.register_for('XOR')
def XOR(*args):
    args = utils.iflatten(args)
    result = sum(bool(a) for a in args)
    return bool(result & 1)


@dispatcher.register_for('OR')
def OR(*args):
    args = utils.iflatten(args)
    return any(args)


@dispatcher.register_for('SWITCH')
def SWITCH(target_value, *args):
    if len(args) <= 1:
        return error.NOT_AVAILABLE
    argc = len(args)
    default_clause = None if (argc % 2 == 0) else args[-1]
    for i in range(0, argc, 2):
        if target_value == args[i]:
            return args[i + 1]
    if default_clause:
        return default_clause
    return error.NOT_AVAILABLE


@dispatcher.register_for('IFS')
def IFS(*args):
    for pair in zip(args[::2], args[1::2]):
        if pair[0]:
            return pair[1]
    return error.NOT_AVAILABLE


# Compatibility functions

@dispatcher.register_for('TRUE')
def TRUE():
    return True


@dispatcher.register_for('FALSE')
def FALSE():
    return False
