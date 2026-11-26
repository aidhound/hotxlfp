# -*- coding: utf-8 -*-
"""
Shared Excel error values, also usable as exceptions to abort internal work.

During formula evaluation these instances travel as values. A function or its
helpers may raise them to stop a calculation; Parser.call_function converts
those exceptions back into values so enclosing formula functions can consume
them. Syntax failures abort parsing. Parser.parse reports an unhandled final
error through its error field.
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
SPILL = XLError('#SPILL!')
FIELD = XLError('#FIELD!')
CALC = XLError('#CALC!')
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
        '#SPILL!': SPILL,
        '#FIELD!': FIELD,
        '#CALC!': CALC,
        '#GETTING_DATA': DATA
    }
    return errdict.get(str(message), ERROR)
