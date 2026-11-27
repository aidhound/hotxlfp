# -*- coding: utf-8 -*-
"""
inspired by:
https://github.com/sutoiku/formula.js/blob/master/lib/math-trig.js
"""
import math
import random
import re
from functools import reduce
import operator
import collections
import decimal
from . import dispatcher
from . import error
from . import utils
from .utils import DEFAULT
from ..helper.number import to_number, validate_number
from .._compat import string_types
from ..helper.text import to_string


@dispatcher.register_for('ABS')
def ABS(number):
    number = utils.parse_number(number)
    if isinstance(number, error.XLError):
        return number
    return abs(number)


@dispatcher.register_for('ACOS')
def ACOS(number):
    number = utils.parse_number(number)
    if isinstance(number, error.XLError):
        return number
    if not -1 <= number <= 1:
        return error.NUM
    return math.acos(number)


@dispatcher.register_for('ACOSH')
def ACOSH(number):
    number = utils.parse_number(number)
    if isinstance(number, error.XLError):
        return number
    try:
        return math.acosh(number)
    except (ValueError, OverflowError):
        return error.NUM


@dispatcher.register_for('ACOT')
def ACOT(number):
    number = utils.parse_number(number)
    if isinstance(number, error.XLError):
        return number
    try:
        return math.atan2(1, number)
    except OverflowError:
        return error.NUM


@dispatcher.register_for('ACOTH')
def ACOTH(number):
    number = utils.parse_number(number)
    if isinstance(number, error.XLError):
        return number
    if -1 <= number <= 1:
        return error.NUM
    return math.atanh(1 / number)


@dispatcher.register_for('SIN')
def SIN(number):
    number = utils.parse_number(number)
    if isinstance(number, error.XLError):
        return number
    try:
        return math.sin(number)
    except OverflowError:
        return error.NUM


@dispatcher.register_for('SINH')
def SINH(number):
    number = utils.parse_number(number)
    if isinstance(number, error.XLError):
        return number
    try:
        return math.sinh(number)
    except OverflowError:
        return error.NUM


@dispatcher.register_for('ASIN')
def ASIN(number):
    number = utils.parse_number(number)
    if isinstance(number, error.XLError):
        return number
    if not -1 <= number <= 1:
        return error.NUM
    return math.asin(number)


@dispatcher.register_for('ASINH')
def ASINH(number):
    number = utils.parse_number(number)
    if isinstance(number, error.XLError):
        return number
    try:
        return math.asinh(number)
    except OverflowError:
        return error.NUM


@dispatcher.register_for('COS')
def COS(number):
    number = utils.parse_number(number)
    if isinstance(number, error.XLError):
        return number
    try:
        return math.cos(number)
    except OverflowError:
        return error.NUM


@dispatcher.register_for('COSH')
def COSH(number):
    number = utils.parse_number(number)
    if isinstance(number, error.XLError):
        return number
    try:
        return math.cosh(number)
    except OverflowError:
        return error.NUM


@dispatcher.register_for('COT')
def COT(number):
    number = utils.parse_number(number)
    if isinstance(number, error.XLError):
        return number
    if abs(number) >= 2**27:
        return error.NUM
    if number == 0:
        return error.DIV_ZERO
    return math.cos(number)/math.sin(number)


@dispatcher.register_for('TAN')
def TAN(number):
    number = utils.parse_number(number)
    if isinstance(number, error.XLError):
        return number
    try:
        return math.tan(number)
    except OverflowError:
        return error.NUM


@dispatcher.register_for('TANH')
def TANH(number):
    number = utils.parse_number(number)
    if isinstance(number, error.XLError):
        return number
    try:
        return math.tanh(number)
    except OverflowError:
        return error.NUM


@dispatcher.register_for('ATAN')
def ATAN(number):
    number = utils.parse_number(number)
    if isinstance(number, error.XLError):
        return number
    try:
        return math.atan(number)
    except OverflowError:
        return error.NUM


@dispatcher.register_for('ATAN2')
def ATAN2(x_num, y_num):
    x_num = utils.parse_number(x_num)
    if isinstance(x_num, error.XLError):
        return x_num
    y_num = utils.parse_number(y_num)
    if isinstance(y_num, error.XLError):
        return y_num
    if y_num == 0:
        if x_num == 0:
            return error.DIV_ZERO
        return 0 if x_num > 0 else math.pi
    try:
        return math.atan2(y_num, x_num)
    except OverflowError:
        return error.NUM


@dispatcher.register_for('ATANH')
def ATANH(number):
    number = utils.parse_number(number)
    if isinstance(number, error.XLError):
        return number
    if not -1 < number < 1:
        return error.NUM
    return math.atanh(number)


@dispatcher.register_for('SQRT')
def SQRT(number):
    number = utils.parse_number(number)
    if isinstance(number, error.XLError):
        return number
    try:
        return math.sqrt(number)
    except (ValueError, OverflowError):
        return error.NUM


@dispatcher.register_for('EXP')
def EXP(number):
    number = utils.parse_number(number)
    if isinstance(number, error.XLError):
        return number
    try:
        return math.e**number
    except OverflowError:
        return error.NUM


@dispatcher.register_for('LN')
def LN(number):
    number = utils.parse_number(number)
    if isinstance(number, error.XLError):
        return number
    try:
        return math.log(number)
    except (ValueError, OverflowError):
        return error.NUM


@dispatcher.register_for('LOG')
@utils.propagate_errors()
def LOG(number, base=10):
    number = utils.parse_number(number)
    base = utils.parse_number(base)
    for value in (number, base):
        if isinstance(value, error.XLError):
            return value
    try:
        return math.log(number, base)
    except ZeroDivisionError:
        return error.DIV_ZERO
    except (ValueError, OverflowError):
        return error.NUM


@dispatcher.register_for('LOG10')
def LOG10(number):
    return LOG(number, 10)


@dispatcher.register_for('PI')
def PI():
    return math.pi


@dispatcher.register_for('ROUND')
@utils.propagate_errors()
def ROUND(number, digits):
    return round_number(number, digits, decimal.ROUND_HALF_UP)


@dispatcher.register_for('ROUNDUP')
@utils.propagate_errors()
def ROUNDUP(number, digits):
    return round_number(number, digits, decimal.ROUND_UP)


@dispatcher.register_for('ROUNDDOWN')
@utils.propagate_errors()
def ROUNDDOWN(number, digits):
    return round_number(number, digits, decimal.ROUND_DOWN)


def round_number(number, digits, rounding):
    """Round decimal places without overflowing an intermediate power of ten."""
    number = utils.parse_number(number)
    digits = utils.parse_number(digits)
    for value in (number, digits):
        if isinstance(value, error.XLError):
            return value
    if isinstance(number, bool):
        number = int(number)
    digits = int(digits)
    # Avoid constructing decimal scales beyond the finite float range.
    if number == 0 or digits > 323:
        return number
    if digits < -308:
        return error.NUM if rounding == decimal.ROUND_UP else 0
    try:
        value = decimal.Decimal(number) if isinstance(number, int) else decimal.Decimal(str(number))
        with decimal.localcontext() as context:
            context.prec = max(28, len(value.as_tuple().digits), value.adjusted() + digits + 2)
            result = value.quantize(decimal.Decimal(1).scaleb(-digits), rounding=rounding)
        return validate_number(float(result))
    except (decimal.InvalidOperation, OverflowError, ValueError):
        return error.NUM


@dispatcher.register_for('SUM')
def SUM(*args):
    try:
        return sum(utils.inumbers(args, try_parse=True))
    except OverflowError:
        return error.NUM


@dispatcher.register_for('SUMIF')
def SUMIF(args, criteria):
    predicate = utils.parse_criteria(criteria)
    values = [value for value in utils.iflatten(args) if predicate(value)]
    return SUM(values)


@dispatcher.register_for('CEILING')
@utils.propagate_errors()
def CEILING(number, significance=1):
    number = utils.parse_number(number)
    significance = utils.parse_number(significance)

    for value in (number, significance):
        if isinstance(value, error.XLError):
            return value
    if significance == 0:
        return 0
    if number > 0 and significance < 0:
        return error.NUM

    positive_significance = significance > 0
    significance = abs(significance)
    try:
        if number >= 0:
            return math.ceil(number / significance) * significance
        if positive_significance:
            return -1 * math.floor(abs(number) / significance) * significance
        return -1 * math.ceil(abs(number) / significance) * significance
    except (OverflowError, ValueError):
        return error.NUM


@dispatcher.register_for('FLOOR')
@utils.propagate_errors()
def FLOOR(number, significance=1):
    number = utils.parse_number(number)
    significance = utils.parse_number(significance)

    for value in (number, significance):
        if isinstance(value, error.XLError):
            return value
    if significance == 0:
        return 0 if number == 0 else error.DIV_ZERO
    if number > 0 and not significance > 0:
        return error.NUM

    abs_significance = abs(significance)
    try:
        if number >= 0:
            return math.floor(number / abs_significance) * abs_significance
        func = math.floor
        if significance > 0:
            func = math.ceil
        return -1 * func(abs(number) / abs_significance) * abs_significance
    except (OverflowError, ValueError):
        return error.NUM


@dispatcher.register_for('CEILING.MATH')
@utils.propagate_errors()
def CEILING_MATH(number, significance=1, mode=0):
    number, significance, mode = map(utils.parse_number, (number, significance, mode))
    for value in (number, significance, mode):
        if isinstance(value, error.XLError):
            return value
    significance = abs(significance)
    return CEILING(number, -significance if number < 0 and mode != 0 else significance)


@dispatcher.register_for('CEILING.PRECISE')
@utils.propagate_errors()
def CEILING_PRECISE(number, significance=1):
    return CEILING_MATH(number, significance)


@dispatcher.register_for('FLOOR.MATH')
@utils.propagate_errors()
def FLOOR_MATH(number, significance=1, mode=0):
    number, significance, mode = map(utils.parse_number, (number, significance, mode))
    for value in (number, significance, mode):
        if isinstance(value, error.XLError):
            return value
    significance = abs(significance)
    if significance == 0:
        return 0
    return FLOOR(number, -significance if number < 0 and mode != 0 else significance)


@dispatcher.register_for('FLOOR.PRECISE')
@utils.propagate_errors()
def FLOOR_PRECISE(number, significance=1):
    return FLOOR_MATH(number, significance)


@dispatcher.register_for('POWER')
@utils.propagate_errors()
def POWER(number, power):
    number = utils.parse_number(number)
    power = utils.parse_number(power)
    for value in (number, power):
        if isinstance(value, error.XLError):
            return value
    if number == 0 and power == 0:
        return error.NUM
    negative_root = number < 0 and power % 1 != 0
    if negative_root:
        # Excel accepts negative roots when 1/power is an odd integer.
        if (1 / power) % 2 != 1:
            return error.NUM
        number = -number
    # Even the smallest integer base above one overflows at 2**1024.
    if isinstance(number, int) and isinstance(power, int) and abs(number) > 1 and power >= 1024:
        return error.NUM
    try:
        result = number**power
        if not math.isfinite(result):
            return error.NUM
    except ZeroDivisionError:
        return error.DIV_ZERO
    except (ValueError, OverflowError):
        return error.NUM
    return -result if negative_root else result


@dispatcher.register_for('QUOTIENT')
@utils.propagate_errors()
def QUOTIENT(numerator, denominator):
    numerator = utils.parse_number(numerator)
    denominator = utils.parse_number(denominator)
    for value in (numerator, denominator):
        if isinstance(value, error.XLError):
            return value
    if denominator == 0:
        return error.DIV_ZERO
    try:
        return int(numerator / denominator)
    except (OverflowError, ValueError):
        return error.NUM


@dispatcher.register_for('MOD')
@utils.propagate_errors()
def MOD(numerator, denominator):
    numerator = utils.parse_number(numerator)
    denominator = utils.parse_number(denominator)
    if isinstance(numerator, error.XLError):
        return numerator
    if isinstance(denominator, error.XLError):
        return denominator
    if denominator == 0:
        return error.DIV_ZERO
    try:
        if not math.isfinite(numerator / denominator):
            return error.NUM
        return numerator % denominator
    except OverflowError:
        return error.NUM


@dispatcher.register_for('RADIANS')
def RADIANS(number):
    number = utils.parse_number(number)
    if isinstance(number, error.XLError):
        return number
    try:
        return validate_number(number * (math.pi / 180))
    except OverflowError:
        return error.NUM


@dispatcher.register_for('DEGREES')
def DEGREES(number):
    number = utils.parse_number(number)
    if isinstance(number, error.XLError):
        return number
    try:
        return validate_number(number * (180 / math.pi))
    except OverflowError:
        return error.NUM


@dispatcher.register_for('PRODUCT')
def PRODUCT(*args):
    if not args:
        return error.ERROR
    values = []
    for value in args:
        if isinstance(value, (list, tuple)):
            values.extend(utils.inumbers(value, try_parse=True))
        elif value is not None:
            value = utils.parse_number(value)
            if isinstance(value, error.XLError):
                return value
            values.append(value)
    try:
        return reduce(operator.mul, values) if values else 0
    except OverflowError:
        return error.NUM


@dispatcher.register_for('ODD')
def ODD(number):
    number = utils.parse_number(number)
    if isinstance(number, error.XLError):
        return number
    tmp = math.ceil(abs(number))
    tmp = tmp if (tmp % 2) == 1 else tmp + 1
    return tmp if number >= 0 else -tmp


@dispatcher.register_for('EVEN')
def EVEN(number):
    number = utils.parse_number(number)
    if isinstance(number, error.XLError):
        return number
    tmp = math.ceil(abs(number))
    tmp = tmp if (tmp % 2) == 0 else tmp + 1
    return tmp if number > 0 else -tmp


@dispatcher.register_for('DECIMAL')
@utils.propagate_errors()
def DECIMAL(text, base):
    text = to_string(text).upper()
    base = utils.parse_number(base)
    if isinstance(base, error.XLError):
        return base
    base = int(base)
    if not 2 <= base <= 36 or len(text) > 255 or re.fullmatch('[0-9A-Z]*', text) is None:
        return error.NUM
    if base == 16 and text.startswith('0X'):
        text = text[2:]
    alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'[:base]
    if any(character not in alphabet for character in text):
        return error.NUM
    try:
        result = int(text, base) if text else 0
        return result if math.isfinite(result) else error.NUM
    except (ValueError, OverflowError):
        return error.NUM


@dispatcher.register_for('BASE')
@utils.propagate_errors()
def BASE(value, base, places=DEFAULT):
    value = utils.parse_number(value)
    if isinstance(value, error.XLError):
        return value
    base = utils.parse_number(base)
    if isinstance(base, error.XLError):
        return base
    base = int(base)
    if not 0 <= value < 2**53 or not 2 <= base <= 36:
        return error.NUM
    value = int(value)
    if places is not DEFAULT:
        places = utils.parse_number(places)
        if isinstance(places, error.XLError):
            return places
        if places < 0 or int(places) > 255:
            return error.NUM
        places = int(places)
    digits = []
    while value:
        digits.append('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'[value % base])
        value //= base
    result = ''.join(digits[::-1]) or '0'
    if places is not DEFAULT:
        result = result.rjust(places, '0')
    return result


@dispatcher.register_for('FACT')
def FACT(number):
    number = utils.parse_number(number)
    if isinstance(number, error.XLError):
        return number
    if number < 0 or int(number) > 170:
        return error.NUM
    return math.factorial(int(number))


@dispatcher.register_for('FACTDOUBLE')
def FACTDOUBLE(number):
    number = utils.parse_number(number)
    if isinstance(number, error.XLError):
        return number
    number = int(number)
    if number < 0 or number > 300:
        return error.NUM
    if number in (0, 1):
        return 1
    return reduce(operator.mul, range(number, 1, -2))


@dispatcher.register_for('ROMAN')
@utils.propagate_errors()
def ROMAN(number, form=0):
    number = utils.parse_number(number)
    form = utils.parse_number(form)
    if form is True:
        form = 0
    elif form is False:
        form = 4
    
    for value in (number, form):
        if isinstance(value, error.XLError):
            return value
    number, form = int(number), int(form)

    if not (0 <= number < 4000 and 0 <= form <= 4):
        return error.VALUE

    def numerals(compress):
        numeral_map = ((1000, 'M'), (500, 'D'), (100, 'C'), (50, 'L'), (10, 'X'), (5, 'V'), (1, 'I'))
        for i, (arabic, roman) in enumerate(numeral_map, 1):
            yield arabic, roman
            # Then we make a list where we try to create new mappings
            # subtracting the subsequent fixed roman numeral values from our current one 
            # and prepending their roman numerals to ours, up to compress times.
            # The more mappings we have the more compressed the representation will be.
            inbetweeners = collections.deque()
            for smaller_arabic, smaller_roman in numeral_map[i:]:
                smaller_arabic = arabic - smaller_arabic
                if (smaller_arabic, smaller_roman) not in numeral_map:
                    inbetweeners.appendleft((smaller_arabic, smaller_roman + roman))
                    if len(inbetweeners) == compress:
                        break
            for el in inbetweeners:
                yield el
    
    result = ''
    for arabic_digit, roman_numeral in numerals(form + 1):
        if not number:
            break
        count = int(number / arabic_digit)
        result += roman_numeral * count
        number -= arabic_digit * count
    return result


@dispatcher.register_for('ARABIC')
@utils.propagate_errors()
def ARABIC(text):
    text = to_string(text).upper()
    if len(text) > 255:
        return error.VALUE
    text = text.strip()
    sign = -1 if text.startswith('-') else 1
    if sign < 0:
        text = text[1:]
        if not text.strip():
            return error.NUM
    if re.fullmatch('[MDCLXVI]*', text) is None:
        return error.VALUE
    numeral_map = dict(M=1000, D=500, C=100, L=50, X=10, V=5, I=1)
    result, largest = 0, 0
    for character in reversed(text):
        value = numeral_map[character]
        result += -value if value < largest else value
        largest = max(largest, value)
    return sign * result


@dispatcher.register_for('RAND')
def RAND():
    return random.random()


@dispatcher.register_for('RANDBETWEEN')
@utils.propagate_errors()
def RANDBETWEEN(bottom, top):
    bottom = utils.parse_number(bottom)
    top = utils.parse_number(top)
    
    for value in (bottom, top):
        if isinstance(value, error.XLError):
            return value
    if bottom > top:
        return error.NUM
    bottom = math.ceil(bottom)
    return random.randint(bottom, max(bottom, math.floor(top)))


@dispatcher.register_for('INT')
@utils.propagate_errors()
def INT(number):
    number = utils.parse_number(number)
    if isinstance(number, error.XLError):
        return number
    return math.floor(number)


@dispatcher.register_for('SUMIFS')
def SUMIFS(sum_args, *criteria):
    if not criteria or len(criteria) % 2 != 0:
        return error.ERROR

    sum_shape = utils.array_shape(sum_args)
    if isinstance(sum_shape, error.XLError):
        return sum_shape

    range_and_preds = []
    for criteria_range, criterion in zip(criteria[::2], criteria[1::2]):
        if isinstance(criteria_range, string_types):
            return error.ERROR
        criteria_shape = utils.array_shape(criteria_range)
        if isinstance(criteria_shape, error.XLError):
            return criteria_shape
        if criteria_shape != sum_shape:
            return error.VALUE
        range_and_preds.append((utils.flatten(criteria_range), utils.parse_criteria(criterion)))

    values = [
        value for i, value in enumerate(utils.iflatten(sum_args))
        if all(pred(criteria_range[i]) for criteria_range, pred in range_and_preds)
    ]
    return SUM(values)


@dispatcher.register_for('SIGN')
@utils.propagate_errors()
def SIGN(number):
    number = utils.parse_number(number)
    if isinstance(number, error.XLError):
        return number
    if number == 0:
        return 0
    if number > 0:
        return 1
    return -1
