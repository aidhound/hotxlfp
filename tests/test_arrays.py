import unittest

from hotxlfp import Parser
from hotxlfp.formulas import error


class TestArrays(unittest.TestCase):

    def test_literals_preserve_rows_columns_and_matrices(self):
        parser = Parser()
        for expression, expected in (
            ('{1}', [[1]]),
            ('{1,2,3}', [[1, 2, 3]]),
            (r'{1\2\3}', [[1, 2, 3]]),
            ('{1;2;3}', [[1], [2], [3]]),
            ('{1,2;3,4;5,6}', [[1, 2], [3, 4], [5, 6]]),
            (r'{1\2;3\4;5\6}', [[1, 2], [3, 4], [5, 6]]),
            (r'{1,2\3;4\5,6}', [[1, 2, 3], [4, 5, 6]]),
            ('{ 1, 2 ;\n 3, 4 }', [[1, 2], [3, 4]]),
        ):
            with self.subTest(expression=expression):
                self.assertEqual(parser.parse(expression), {'result': expected, 'error': None})

    def test_blank_entries_preserve_positions(self):
        parser = Parser()
        for expression, expected in (
            ('{1,,3}', [[1, None, 3]]),
            (r'{1\\3}', [[1, None, 3]]),
            ('{,1,}', [[None, 1, None]]),
            (r'{\1\}', [[None, 1, None]]),
            ('{,}', [[None, None]]),
            ('{,,}', [[None, None, None]]),
            ('{1;;3}', [[1], [None], [3]]),
            ('{;1;}', [[None], [1], [None]]),
            ('{;}', [[None], [None]]),
            ('{;;}', [[None], [None], [None]]),
            ('{1,2;,}', [[1, 2], [None, None]]),
            (r'{1\2;\}', [[1, 2], [None, None]]),
            ('{NULL}', [[None]]),
        ):
            with self.subTest(expression=expression):
                self.assertEqual(parser.parse(expression), {'result': expected, 'error': None})

    def test_invalid_array_layouts_abort_parsing(self):
        parser = Parser()
        for expression in ('{}', '{ \n }', r'{1\2;3}', '{1,2;3}',
                           '{1;2,3}', '{1,2;}', '{{1,2}}', 'IFERROR({1,2;3},99)'):
            with self.subTest(expression=expression):
                self.assertEqual(parser.parse(expression), {'result': None, 'error': '#ERROR!'})

    def test_array_elements_keep_expression_and_quoted_separator_support(self):
        parser = Parser()
        self.assertEqual(parser.parse('{SUM(1,2),SUM(3;4);ABS(-5),6/2}'),
                         {'result': [[3, 7], [5, 3]], 'error': None})
        self.assertEqual(parser.parse(r'{"a,b","c;d","e\f"}'),
                         {'result': [['a,b', 'c;d', r'e\f']], 'error': None})

    def test_error_cells_keep_their_positions_and_codes(self):
        parser = Parser()
        expression = '{1,#N/A;#DIV/0!,4}'
        self.assertEqual(parser.parse(expression),
                         {'result': [[1, error.NOT_AVAILABLE], [error.DIV_ZERO, 4]], 'error': None})
        self.assertEqual(parser.parse('IFERROR(' + expression + ',0)'),
                         {'result': [[1, 0], [0, 4]], 'error': None})
        self.assertEqual(parser.parse('IFNA(' + expression + ',7)'),
                         {'result': [[1, 7], [error.DIV_ZERO, 4]], 'error': None})

    def test_function_argument_separators_and_blanks_are_preserved(self):
        parser = Parser()
        parser.set_function('CAPTURE', lambda *args: list(args))
        for arguments in ('1,2,3', '1;2;3', r'1\2\3'):
            with self.subTest(arguments=arguments):
                self.assertEqual(parser.parse('CAPTURE(' + arguments + ')'),
                                 {'result': [1, 2, 3], 'error': None})
        for arguments in ('1,,3', '1;;3', r'1\\3'):
            with self.subTest(arguments=arguments):
                self.assertEqual(parser.parse('CAPTURE(' + arguments + ')'),
                                 {'result': [1, None, 3], 'error': None})
        self.assertEqual(parser.parse('SUM({1,2};{3;4})'), {'result': 10, 'error': None})

    def test_array_orientation_reaches_arithmetic_and_consumers(self):
        parser = Parser()
        for expression, expected in (
            ('ROWS({1,2,3})', 1),
            (r'ROWS({1\2\3})', 1),
            ('ROWS({1;2;3})', 3),
            ('{1,2}+{10;20}', [[11, 12], [21, 22]]),
            (r'{1\2}+{10;20}', [[11, 12], [21, 22]]),
            ('SUMIFS({10,20,30},{1,2,3},">1")', 50),
            ('AVERAGEIFS({10,20,30},{1,2,3},">1")', 25),
            ('MAXIFS({10,20,30},{1,2,3},">1")', 30),
            ('LARGE({10,20,30},2)', 20),
            ('MATCH(20,{10,20,30},0)', 2),
            ('MATCH(20,{10;20;30},0)', 2),
            ('INDEX({1,2;3,4;5,6},3,2)', 6),
            ('IFERROR(SUMIFS({10,20},{1;2},">1"),99)', 99),
        ):
            with self.subTest(expression=expression):
                self.assertEqual(parser.parse(expression), {'result': expected, 'error': None})

    def test_callback_arrays_keep_their_original_shapes(self):
        parser = Parser()
        parser.set_function('DATA', lambda: [1, 2, 3])
        parser.set_function('CAPTURE', lambda *args: list(args))
        self.assertEqual(parser.parse('DATA()'), {'result': [1, 2, 3], 'error': None})
        self.assertEqual(parser.parse('CAPTURE(DATA(),{1,2})'),
                         {'result': [[1, 2, 3], [[1, 2]]], 'error': None})
