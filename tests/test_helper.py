# -*- coding: utf-8 -*-

import unittest
import datetime
from hotxlfp.helper import cell, number, text
from hotxlfp.formulas import error, utils


class TestHelper(unittest.TestCase):

    def test_date_serialization_preserves_1900_boundaries_and_time_fractions(self):
        for value, expected in (
            (datetime.datetime(1900, 1, 1), 1),
            (datetime.datetime(1900, 1, 1, 12), 1.5),
            (datetime.datetime(1900, 2, 28), 59),
            (datetime.datetime(1900, 2, 28, 12), 59.5),
            (datetime.datetime(1900, 3, 1), 61),
            (datetime.datetime(1900, 3, 1, 12), 61.5),
            (datetime.datetime(2025, 1, 1, 12), 45658.5),
            (datetime.date(1900, 1, 1), 1),
            (datetime.date(1900, 3, 1), 61),
        ):
            with self.subTest(value=value):
                self.assertEqual(utils.serialize_date(value), expected)
                expected_date = (value if isinstance(value, datetime.datetime)
                                 else datetime.datetime.combine(value, datetime.time()))
                self.assertEqual(utils.parse_date(expected), expected_date)
        for value in (error.DIV_ZERO, error.NOT_AVAILABLE, error.NUM):
            self.assertIs(utils.serialize_date(value), value)

    def test_to_string_preserves_text_errors_and_converts_blanks_and_booleans(self):
        for value, expected in ((None, ''), ('', ''), ('True', 'True'),
                                ('None', 'None'), (True, 'TRUE'), (False, 'FALSE'),
                                (0, '0'), (123, '123'), (10 ** 400, str(10 ** 400))):
            with self.subTest(value=value):
                self.assertEqual(text.to_string(value), expected)
        for value in (error.DIV_ZERO, error.NOT_AVAILABLE, error.NUM):
            self.assertIs(text.to_string(value), value)

    def test_to_string_formats_floats_like_measured_excel_values(self):
        for value, expected in (
            (1.0, '1'), (-0.0, '0'), (1.25, '1.25'),
            (1 / 3, '0.333333333333333'), (2 / 3, '0.666666666666667'),
            (1.234567890123456, '1.23456789012346'),
            (1e-10, '0.0000000001'), (1e-18, '0.000000000000000001'),
            (1e-19, '1E-19'), (1.23456789e-10, '0.000000000123456789'),
            (1.23456789012345e-5, '1.23456789012345E-05'),
            (1e19, '10000000000000000000'), (1e20, '1E+20'),
            (-1e19, '-10000000000000000000'), (-1e-18, '-0.000000000000000001'),
        ):
            with self.subTest(value=value):
                self.assertEqual(text.to_string(value), expected)

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
