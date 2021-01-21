# -*- coding: utf-8 -*-
"""
inspired by:
https://github.com/sutoiku/formula.js/blob/master/lib/math-trig.js
"""
from __future__ import division
import math
import random
import re
from functools import reduce
import operator
import collections
from . import dispatcher
from . import error
from . import utils
from .utils import DEFAULT
from ..helper.number import to_number


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
    return math.acos(number)


@dispatcher.register_for('ACOSH')
def ACOSH(number):
    number = utils.parse_number(number)
    if isinstance(number, error.XLError):
        return number
    return math.log(number + math.sqrt(number * number - 1))


@dispatcher.register_for('ACOT')
def ACOT(number):
    number = utils.parse_number(number)
    if isinstance(number, error.XLError):
        return number
    return math.atan(1 / number)


@dispatcher.register_for('ACOTH')
def ACOTH(number):
    number = utils.parse_number(number)
    if isinstance(number, error.XLError):
        return number
    return 0.5 * math.log((number + 1) / (number - 1))


@dispatcher.register_for('SIN')
def SIN(number):
    number = utils.parse_number(number)
    if isinstance(number, error.XLError):
        return number
    return math.sin(number)


@dispatcher.register_for('SINH')
def SINH(number):
    number = utils.parse_number(number)
    if isinstance(number, error.XLError):
        return number
    return math.sinh(number)


@dispatcher.register_for('ASIN')
def ASIN(number):
    number = utils.parse_number(number)
    if isinstance(number, error.XLError):
        return number
    return math.asin(number)


@dispatcher.register_for('ASINH')
def ASINH(number):
    number = utils.parse_number(number)
    if isinstance(number, error.XLError):
        return number
    return math.asinh(number)


@dispatcher.register_for('COS')
def COS(number):
    number = utils.parse_number(number)
    if isinstance(number, error.XLError):
        return number
    return math.cos(number)


@dispatcher.register_for('COSH')
def COSH(number):
    number = utils.parse_number(number)
    if isinstance(number, error.XLError):
        return number
    return math.cosh(number)


@dispatcher.register_for('COT')
def COT(number):
    number = utils.parse_number(number)
    if isinstance(number, error.XLError):
        return number
    return math.cos(number)/math.sin(number)


@dispatcher.register_for('TAN')
def TAN(number):
    number = utils.parse_number(number)
    if isinstance(number, error.XLError):
        return number
    return math.tan(number)


@dispatcher.register_for('TANH')
def TANH(number):
    number = utils.parse_number(number)
    if isinstance(number, error.XLError):
        return number
    return math.tanh(number)


@dispatcher.register_for('ATAN')
def ATAN(number):
    number = utils.parse_number(number)
    if isinstance(number, error.XLError):
        return number
    return math.atan(number)


@dispatcher.register_for('ATAN2')
def ATAN2(x_num, y_num):
    x_num = utils.parse_number(x_num)
    if isinstance(x_num, error.XLError):
        return x_num
    y_num = utils.parse_number(x_num)
    if isinstance(y_num, error.XLError):
        return y_num
    return math.atan2(x_num, y_num)


@dispatcher.register_for('ATANH')
def ATANH(number):
    number = utils.parse_number(number)
    if isinstance(number, error.XLError):
        return number
    return math.atanh(number)


@dispatcher.register_for('SQRT')
def SQRT(number):
    number = utils.parse_number(number)
    if isinstance(number, error.XLError):
        return number
    return math.sqrt(number)


@dispatcher.register_for('EXP')
def EXP(number):
    number = utils.parse_number(number)
    if isinstance(number, error.XLError):
        return number
    return math.e**number


@dispatcher.register_for('LN')
def LN(number):
    number = utils.parse_number(number)
    if isinstance(number, error.XLError):
        return number
    return math.log(number)


@dispatcher.register_for('LOG')
def LOG(number, base=10):
    number = utils.parse_number(number)
    base = utils.parse_number(base)
    if utils.any_is_error((number, base)):
        return error.VALUE
    return math.log(number, base)


@dispatcher.register_for('LOG10')
def LOG10(number):
    return LOG(number, 10)


@dispatcher.register_for('PI')
def PI():
    return math.pi


@dispatcher.register_for('ROUND')
def ROUND(number, digits):
    number = utils.parse_number(number)
    digits = utils.parse_number(digits)
    if utils.any_is_error((number, digits)):
        return error.VALUE
    return round(number, digits)


@dispatcher.register_for('ROUNDUP')
def ROUNDUP(number, digits):
    number = utils.parse_number(number)
    digits = utils.parse_number(digits)
    if utils.any_is_error((number, digits)):
        return error.VALUE
    sign = 1 if number > 0 else -1
    return sign * (math.ceil(abs(number) * 10**digits)) / 10**digits


@dispatcher.register_for('ROUNDDOWN')
def ROUNDDOWN(number, digits):
    number = utils.parse_number(number)
    digits = utils.parse_number(digits)
    if utils.any_is_error((number, digits)):
        return error.VALUE
    sign = 1 if number > 0 else -1
    return sign * (math.floor(abs(number) * 10**digits)) / 10**digits


@dispatcher.register_for('SUM')
def SUM(*args):
    return sum(utils.inumbers(args, try_parse=True))


@dispatcher.register_for('SUMIF')
def SUMIF(args, criteria):
    predicate = utils.parse_criteria(criteria)
    return sum(a for a in utils.iflatten(args) if predicate(a))


@dispatcher.register_for('CEILING', 'CEILING.MATH', 'CEILING.PRECISE')
def CEILING(number, significance=1):
    number = utils.parse_number(number)
    significance = utils.parse_number(significance)

    if utils.any_is_error((number, significance)):
        return error.VALUE
    if significance == 0:
        return 0

    positive_significance = significance > 0
    significance = abs(significance)
    if number >= 0:
        return math.ceil(number / significance) * significance
    else:
        if positive_significance:
            return -1 * math.floor(abs(number) / significance) * significance
        else:
            return -1 * math.ceil(abs(number) / significance) * significance


@dispatcher.register_for('FLOOR', 'FLOOR.MATH', 'FLOOR.PRECISE')
def FLOOR(number, significance=1):
    number = utils.parse_number(number)
    significance = utils.parse_number(significance)

    if utils.any_is_error((number, significance)):
        return error.VALUE
    if significance == 0:
        return 0
    if number > 0 and not significance > 0:
        return error.NUM

    significance = abs(significance)
    if number >= 0:
        return math.floor(number / significance) * significance
    else:
        return -1 * math.floor(abs(number) / significance) * significance


@dispatcher.register_for('POWER')
def POWER(number, power):
    number = utils.parse_number(number)
    power = utils.parse_number(power)
    if utils.any_is_error((number, power)):
        return error.VALUE
    result = number**power
    if math.isnan(result):
        return error.NUM
    return result


@dispatcher.register_for('QUOTIENT')
def QUOTIENT(numerator, denominator):
    numerator = utils.parse_number(numerator)
    denominator = utils.parse_number(denominator)
    if utils.any_is_error((numerator, denominator)):
        return error.VALUE
    if denominator == 0:
        return error.DIV_ZERO
    return int(numerator / denominator)


@dispatcher.register_for('MOD')
def MOD(numerator, denominator):
    numerator = utils.parse_number(numerator)
    denominator = utils.parse_number(denominator)
    if isinstance(numerator, error.XLError):
        return numerator
    if isinstance(denominator, error.XLError):
        return denominator
    if denominator == 0:
        return error.DIV_ZERO
    modulus = abs(numerator % denominator)
    return modulus if denominator > 0 else -modulus


@dispatcher.register_for('RADIANS')
def RADIANS(number):
    number = utils.parse_number(number)
    if isinstance(number, error.XLError):
        return number
    return number * math.pi / 180


@dispatcher.register_for('DEGREES')
def DEGREES(number):
    number = utils.parse_number(number)
    if isinstance(number, error.XLError):
        return number
    return number * 180 / math.pi


@dispatcher.register_for('PRODUCT')
def PRODUCT(*args):
    return reduce(operator.mul, utils.inumbers(args))


@dispatcher.register_for('ODD')
def ODD(number):
    number = utils.parse_number(number)
    if isinstance(number, error.XLError):
        return number
    tmp = math.ceil(abs(number))
    tmp = tmp if (tmp % 2) == 1 else tmp + 1
    return tmp if number > 0 else -tmp


@dispatcher.register_for('EVEN')
def EVEN(number):
    number = utils.parse_number(number)
    if isinstance(number, error.XLError):
        return number
    tmp = math.ceil(abs(number))
    tmp = tmp if (tmp % 2) == 0 else tmp + 1
    return tmp if number > 0 else -tmp


@dispatcher.register_for('DECIMAL')
def DECIMAL(text, base):
    text = str(text)
    base = utils.parse_number(base)
    if isinstance(base, error.XLError):
        return base
    try:
        dec = int(text, base)
        return (dec - 1099511627776) if (dec >= 549755813888) else dec
    except ValueError:
        return error.VALUE


@dispatcher.register_for('BASE')
def BASE(value, base, places=DEFAULT):
    value = utils.parse_number(value)
    if isinstance(value, error.XLError):
        return value
    base = utils.parse_number(base)
    if isinstance(base, error.XLError):
        return base
    if places is not DEFAULT:
        places = utils.parse_number(places)
        if isinstance(places, error.XLError):
            return places
        if places < 0:
            return error.NUM
    if value == 0:
        return '0'
    digits = []
    while value:
        digits.append(int(value % base))
        value //= base
    result = ''.join(str(n) for n in digits[::-1])
    if places is not DEFAULT:
        if len(result) > places:
            return error.NUM
        result = result.rjust(places, '0')
    return result


@dispatcher.register_for('FACT')
def FACT(number):
    number = utils.parse_number(number)
    if isinstance(number, error.XLError):
        return number
    if number < 0:
        return error.NUM
    return math.factorial(int(number))


@dispatcher.register_for('FACTDOUBLE')
def FACTDOUBLE(number):
    number = utils.parse_number(number)
    if isinstance(number, error.XLError):
        return number
    if number < 0:
        return error.NUM
    number = int(number)
    if number in (0, 1):
        return 1
    return reduce(operator.mul, range(number, 1, -2))


@dispatcher.register_for('ROMAN')
def ROMAN(number, form=0):
    number = utils.parse_number(number)
    form = utils.parse_number(form)
    if form is True:
        form = 0
    elif form is False:
        form = 4
    
    if utils.any_is_error((number, form)):
        return error.VALUE

    if not (0 < number < 4000 and 0 <= form <= 4):
        return error.VALUE # number must be between 1 and 3999

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
def ARABIC(text):
    text = str(text).upper()
    roman_numeral_regex = '^M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$'

    if re.search(roman_numeral_regex, text) is None:
        return error.VALUE

    numeral_map = {
        'M': 1000,
        'CM': 900,
        'D': 500,
        'CD': 400,
        'C': 100,
        'XC': 90,
        'L': 50,
        'XL': 40,
        'X': 10,
        'IX': 9,
        'V': 5,
        'IV': 4,
        'I': 1
    }
    result = 0
    return sum(numeral_map[match.group()] for match in re.finditer('[MDLV]|C[MD]?|X[CL]?|I[XV]?', text))


@dispatcher.register_for('RAND')
def RAND():
    return random.random()


@dispatcher.register_for('RANDBETWEEN')
def RANDBETWEEN(bottom, top):
    bottom = utils.parse_number(bottom)
    top = utils.parse_number(top)
    
    if utils.any_is_error((bottom, top)):
        return error.VALUE

    return random.randint(int(bottom), int(top))
