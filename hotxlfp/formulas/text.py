# -*- coding: utf-8 -*-
"""
inspired by:
https://github.com/sutoiku/formula.js/blob/master/lib/math-trig.js
"""
import math
from functools import reduce
import operator
import datetime
import re
from fractions import Fraction
from . import dispatcher
from . import error
from . import utils
from .utils import DEFAULT
from ..helper.text import to_string


@dispatcher.register_for('CHAR')
def CHAR(number):
    number = utils.parse_number(number)
    if isinstance(number, error.XLError):
        return number
    return chr(number)


@dispatcher.register_for('CODE')
@utils.propagate_errors()
def CODE(char):
    char = to_string(char)
    return ord(char[0]) if char else error.VALUE


@dispatcher.register_for('CLEAN')
def CLEAN(text):
    text = to_string(text)
    if isinstance(text, error.XLError):
        return text
    return ''.join(c for c in text if ord(c) > 31)


@dispatcher.register_for('CONCAT', 'CONCATENATE')
@utils.propagate_errors(nested=True)
def CONCATENATE(*args):
    return ''.join(to_string(value) for value in utils.iflatten(args))


@dispatcher.register_for('LEN', 'LENB')
def LEN(text):
    text = to_string(text)
    if isinstance(text, error.XLError):
        return text
    return len(text)


@dispatcher.register_for('LOWER')
def LOWER(text):
    text = to_string(text)
    if isinstance(text, error.XLError):
        return text
    return text.lower()


@dispatcher.register_for('UPPER')
def UPPER(text):
    text = to_string(text)
    if isinstance(text, error.XLError):
        return text
    return text.upper()


@dispatcher.register_for('PROPER')
def PROPER(text):
    text = to_string(text)
    if isinstance(text, error.XLError):
        return text
    return text.title()


@dispatcher.register_for('SUBSTITUTE')
@utils.propagate_errors()
def SUBSTITUTE(text, old_text, new_text, instance_num=DEFAULT):
    if instance_num is not DEFAULT:
        instance_num = utils.parse_number(instance_num)
        if isinstance(instance_num, error.XLError):
            return instance_num
        if instance_num <= 0:
            return error.VALUE
    text = to_string(text)
    old_text = to_string(old_text)
    new_text = to_string(new_text)
    if not text or not old_text:
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
@utils.propagate_errors(nested=True)
def TEXTJOIN(delimiter, ignore_empty, *args):
    delimiter = to_string(delimiter)
    words = (to_string(value) for value in utils.iflatten(args))
    if ignore_empty:
        words = (word for word in words if word != '')
    return delimiter.join(words)


@dispatcher.register_for('LEFT', 'LEFTB')
@utils.propagate_errors()
def LEFT(text, num_chars=1):
    text = to_string(text)
    if num_chars < 0:
        return error.VALUE
    return text[:num_chars]


@dispatcher.register_for('RIGHT', 'RIGHTB')
@utils.propagate_errors()
def RIGHT(text, num_chars=1):
    text = to_string(text)
    if num_chars < 0:
        return error.VALUE
    if num_chars == 0:
        return ''
    return text[-num_chars:]


@dispatcher.register_for('MID', 'MIDB')
@utils.propagate_errors()
def MID(text, start_num, num_chars=1):
    text = to_string(text)
    if start_num < 1 or num_chars < 0:
        return error.VALUE
    return text[start_num - 1:][:num_chars]


@dispatcher.register_for('TEXT')
@utils.propagate_errors()
def TEXT(value, format_text):
    if isinstance(format_text, bool):
        return error.VALUE
    format_text = to_string(format_text)
    if isinstance(value, bool):
        return to_string(value)
    # Digits 1-9 are literal format characters; only 0 is a digit placeholder.
    if not format_text or re.fullmatch(r'[1-9]+', format_text):
        return format_text
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


@dispatcher.register_for('TRIM')
def TRIM(value):
    value = to_string(value)
    if isinstance(value, error.XLError):
        return value
    return re.sub(' {2,}', ' ', value).strip()
