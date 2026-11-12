# -*- coding: utf-8 -*-

import unittest
from hotxlfp.helper import cell, number
from hotxlfp.formulas import error


class TestHelper(unittest.TestCase):

    def test_to_number_returns_num_for_nonfinite_values(self):
        for value in (
            float('nan'), float('inf'), float('-inf'),
            complex(float('nan'), 0), complex(0, float('inf')),
            'NaN', 'inf', '-Infinity', '1e309',
        ):
            with self.subTest(value=value):
                self.assertIs(number.to_number(value), error.NUM)
                self.assertIs(number.invert_number(value), error.NUM)

    def test_to_number_preserves_valid_values_and_unparseable_text(self):
        for value, expected in [
            (0, 0), (False, False), (True, True), (10 ** 400, 10 ** 400),
            (complex(3, 4), complex(3, 4)), ('7', 7), ('3.5', 3.5),
            ('text', 'text'), ('', ''), (None, None),
            (error.DIV_ZERO, error.DIV_ZERO),
        ]:
            with self.subTest(value=value):
                actual = number.to_number(value)
                self.assertEqual(actual, expected)
                self.assertIs(type(actual), type(expected))

    def test_row_index_to_label(self):
        res = cell.row_index_to_label(0)
        self.assertEqual(res, '1')
        res = cell.row_index_to_label(26)
        self.assertEqual(res, '27')
        res = cell.row_index_to_label(51)
        self.assertEqual(res, '52')

    def test_row_label_to_index(self):
        res = cell.row_label_to_index('0')
        self.assertEqual(res, -1)
        res = cell.row_label_to_index('A')
        self.assertEqual(res, -1)
        res = cell.row_label_to_index('1')
        self.assertEqual(res, 0)
        res = cell.row_label_to_index('27')
        self.assertEqual(res, 26)
        res = cell.row_label_to_index('50')
        self.assertEqual(res, 49)

    def test_column_index_to_label(self):
        res = cell.column_index_to_label(0)
        self.assertEqual(res, 'A')
        res = cell.column_index_to_label(26)
        self.assertEqual(res, 'AA')
        res = cell.column_index_to_label(51)
        self.assertEqual(res, 'AZ')

    def test_column_label_to_index(self):
        res = cell.column_label_to_index('')
        self.assertEqual(res, -1)
        res = cell.column_label_to_index('A')
        self.assertEqual(res, 0)
        res = cell.column_label_to_index('AA')
        self.assertEqual(res, 26)
        res = cell.column_label_to_index('AZ')
        self.assertEqual(res, 51)

    def test_extract_label(self):
        res = cell.extract_label('A1')
        self.assertEqual(res[0].index, 0)
        self.assertEqual(res[0].label, '1')
        self.assertEqual(res[0].is_absolute, False)
        self.assertEqual(res[1].index, 0)
        self.assertEqual(res[1].label, 'A')
        self.assertEqual(res[1].is_absolute, False)
        res = cell.extract_label('$N$98')
        self.assertEqual(res[0].index, 97)
        self.assertEqual(res[0].label, '98')
        self.assertEqual(res[0].is_absolute, True)
        self.assertEqual(res[1].index, 13)
        self.assertEqual(res[1].label, 'N')
        self.assertEqual(res[1].is_absolute, True)

    def test_to_label(self):
        res = cell.to_label(cell.ParsedLabel(index=0, label='1', is_absolute=False),
                            cell.ParsedLabel(index=0, label='A', is_absolute=False))
        self.assertEqual(res, 'A1')
        res = cell.to_label(cell.ParsedLabel(index=97, label='98', is_absolute=True),
                            cell.ParsedLabel(index=13, label='N', is_absolute=True))
        self.assertEqual(res, '$N$98')
