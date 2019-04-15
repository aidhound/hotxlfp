# -*- coding: utf-8 -*-
import re
import math
from collections import namedtuple
from .._compat import integer_types, string_types


def row_label_to_index(label):
    try:
        result = int(label)
    except ValueError:
        result = label
    if isinstance(result, integer_types):
        return max(result - 1, -1)
    else:
        return -1


def row_index_to_label(row):
    if row >= 0:
        return str(row + 1)
    return ''

COLUMN_LABEL_BASE = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
COLUMN_LABEL_BASE_LENGTH = len(COLUMN_LABEL_BASE)


def column_label_to_index(label):
    result = 0
    if isinstance(label, string_types):
        label = label.upper()
        for i, j in zip(range(len(label)), range(len(label) - 1, -1, -1)):
            result += (COLUMN_LABEL_BASE_LENGTH**j) * (COLUMN_LABEL_BASE.find(label[i]) + 1)
    return result - 1


def column_index_to_label(column):
    result = ''
    while column >= 0:
        column = int(column)
        result = chr((column % COLUMN_LABEL_BASE_LENGTH) + 97) + result
        column = math.floor(column // COLUMN_LABEL_BASE_LENGTH) - 1

    return result.upper()


LABEL_EXTRACT_REGEXP = re.compile(r'^([$])?([A-Za-z]+)([$])?([0-9]+)$')

ParsedLabel = namedtuple('ParsedLabel', ['index', 'label', 'is_absolute'])


class Cell(object):
    __slots__ = ('label', 'row', 'col')

    def __init__(self, label=None, row=None, col=None):
        self.label = label
        self.row = row
        self.col = col

    def __getitem__(self, idx):
        # Allowing you to do stuff like row, coll = mycell
        if idx == 0:
            return self.row
        if idx == 1:
            return self.col
        raise IndexError

    def __repr__(self):
        return 'Cell(label=%(label)s, row=%(row)s, col=%(col)s)' % {'label': self.label,'row': self.row, 'col': self.col}


def extract_label(label):
    """ 
    Extract cell coordinates.

    @param label cell coordinates (e.g. 'A1', '$B6', '$N$98').
    @returns Returns an list of objects.
    """
    match = LABEL_EXTRACT_REGEXP.match(label)
    if (not isinstance(label, string_types)) or (match is None):
        return []
    label = label.upper()
    column_abs, column, row_abs, row = match.groups()

    return [
        ParsedLabel(
            index=row_label_to_index(row),
            label=row,
            is_absolute=row_abs == '$'
        ),
        ParsedLabel(
            index=column_label_to_index(column),
            label=column,
            is_absolute=column_abs == '$',
        )
    ]


def to_label(row, column):
    row_label = ('$' if row.is_absolute else '') + row_index_to_label(row.index)
    column_label = ('$' if column.is_absolute else '') + column_index_to_label(column.index)
    return column_label + row_label
