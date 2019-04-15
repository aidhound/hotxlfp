# -*- coding: utf-8 -*-
"""
Defines Excel errors as python exceptions
"""

class XLError(RuntimeError):
    pass

ERROR = XLError('#ERROR!')
DIV_ZERO = XLError('#DIV/0!')
NAME = XLError('#NAME?')
NOT_AVAILABLE = XLError('#N/A')
NULL = XLError('#NULL!')
NUM = XLError('#NUM!')
REF = XLError('#REF!')
VALUE = XLError('#VALUE!')
DATA = XLError('#GETTING_DATA')


def from_message(message):
    errdict = {
        '#ERROR!': ERROR,
        '#DIV/0!': DIV_ZERO,
        '#NAME?': NAME,
        '#N/A': NOT_AVAILABLE,
        '#NULL!': NULL,
        '#NUM!': NUM,
        '#REF!': REF,
        '#VALUE!': VALUE,
        '#GETTING_DATA': DATA
    }
    return errdict.get(str(message), ERROR)
