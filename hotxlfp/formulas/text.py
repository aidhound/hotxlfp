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


@dispatcher.register_for('LEN', 'LENB')
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


@dispatcher.register_for('LEFT', 'LEFTB')
def LEFT(text, num_chars=1):
    if num_chars < 0 or not isinstance(text, string_types):
        return error.VALUE
    return text[:num_chars]


@dispatcher.register_for('RIGHT', 'RIGHTB')
def RIGHT(text, num_chars=1):
    if num_chars < 0 or not isinstance(text, string_types):
        return error.VALUE
    return text[-num_chars:]


@dispatcher.register_for('MID', 'MIDB')
def MID(text, start_num, num_chars=1):
    if start_num < 1 or num_chars < 0 or not isinstance(text, string_types):
        return error.VALUE
    return text[start_num - 1:][:num_chars]

import datetime
import re
from fractions import Fraction
@dispatcher.register_for('TEXT')
def TEXT(value, format_text):
    if not isinstance(format_text, string_types):
        return error.NAME
    if isinstance(value, (datetime.datetime, datetime.date)):
        value = datetime.datetime(year=value.year, month=value.month, day=value.day)

        if 'h' in format_text or 'hh' in format_text:
            format_text = re.sub(r'\bmm\b', '%M', format_text)
            format_text = re.sub(r'\bm\b', str(value.minute), format_text)
        else:
            format_text = re.sub(r'\bmm\b', f"{value.month:02}", format_text)
            format_text = re.sub(r'\bm\b', str(value.month), format_text)
        
        format_mapping = {
            "yyyy": "%Y", "yyy": "%Y", "yy": "%y",
            "mmmmm": value.strftime('%B')[0], "mmmm": "%B", "mmm": "%b",
            "dddd": "%A","ddd": "%a","dd": f"{value.day:02}", "d": str(value.day),
            "hh": "%H", "h": str(value.hour or 12), "ss": "%S", "s": str(value.second or 12),
            "am/pm": "%p", "a/p": value.strftime("%p")[0].lower()
        }

        for k, v in format_mapping.items():
            format_text = re.sub(rf"\b{k}\b", v, format_text)

        return value.strftime(format_text)
    
    if isinstance(value, (int, float)):
        prefix = re.match(r'^[^\d#0,]*', format_text).group()
        suffix = re.search(r'[^\d#0,%]*$', format_text).group()
        
        numeric_format = format_text[len(prefix):-len(suffix) if suffix else None]

        is_percentage = '%' in numeric_format
        if is_percentage:
            value *= 100
            numeric_format = numeric_format.replace('%', '')

        numeric_format = numeric_format.replace(',', '')

        if '.' in numeric_format:
            num_decimal_places = len(numeric_format.split('.')[1].replace('#', '0'))
            formatted_value = f"{value:.{num_decimal_places}f}"
        else:
            if value - int(value) >= 0.5:
                formatted_value = str(math.ceil(value))
            else:
                formatted_value = str(math.floor(value))

        if ',' in format_text:
            parts = formatted_value.split('.')
            parts[0] = '{:,}'.format(int(parts[0]))
            formatted_value = '.'.join(parts)


        if 'E' in numeric_format:
            coefficient_format, exponent_format = numeric_format.split('E')

            if '.' in coefficient_format:
                num_decimal_places = len(coefficient_format.split('.')[1].replace('#', '0'))
                formatted_value = f"{value:.{num_decimal_places}e}"
            else:
                formatted_value = f"{value:.0e}"

            if '+' in exponent_format:
                formatted_value = formatted_value.replace('e+', 'E+')
            else:
                formatted_value = formatted_value.replace('e', 'E')

            return formatted_value

        if '???/???' in format_text and '#' not in format_text:
            frac_value = Fraction(value).limit_denominator()
            return f"{frac_value.numerator}/{frac_value.denominator}"
        elif '# ???/???' in format_text:
            frac_value = (Fraction(value).limit_denominator()) - int(value)
            return f"{int(value)} {frac_value.numerator}/{frac_value.denominator}"
        
        return f"{prefix}{formatted_value}{suffix}" + ('%' if is_percentage else '')
    else:
        return format_text

