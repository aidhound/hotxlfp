# -*- coding: utf-8 -*-
import unittest
from hotxlfp import Parser, formulas
from hotxlfp.formulas import error


class TestLookupAndReference(unittest.TestCase):

    def test_rows_counts_outer_entries(self):
        p = Parser()
        cases = [
            (['Alice', 'Bob'], 2),
            (['Alice', None, ''], 3),
            ([0, False, error.DIV_ZERO], 3),
            ([], 0),
            ([[1, 2, 3]], 1),
            ([[1], [2], [3]], 3),
            ([[1, 2], [3, 4]], 2),
            ((1, None, 3), 3),
            ((), 0),
            ([[1], [2, 3]], 2),
        ]
        for values, expected in cases:
            p.set_function('DATA', lambda values=values: values)
            for name in ('ROWS', 'rows', 'rOwS'):
                with self.subTest(values=values, function=name):
                    self.assertEqual(p.parse(name + '(DATA())'),
                                     {'result': expected, 'error': None})
        self.assertTrue(callable(formulas.get_for('ROWS')))

    def test_rows_invalid_inputs_and_argument_counts(self):
        p = Parser()
        for value in (None, 7, False, 'text'):
            with self.subTest(value=value):
                p.set_function('DATA', lambda value=value: value)
                self.assertEqual(p.parse('ROWS(DATA())'),
                                 {'result': None, 'error': '#VALUE!'})
        for expression in ('ROWS()', 'ROWS(1,2)'):
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression),
                                 {'result': None, 'error': '#N/A'})
        self.assertEqual(p.parse('IFERROR(ROWS(7),99)'),
                         {'result': 99, 'error': None})

    def test_rows_preserves_direct_errors_for_handlers(self):
        p = Parser()
        p.set_function('ERR', lambda: error.DIV_ZERO)
        for expression, result, code in [
            ('ROWS(ERR())', None, '#DIV/0!'),
            ('IFERROR(ROWS(ERR()),99)', 99, None),
            ('IFNA(ROWS(ERR()),77)', None, '#DIV/0!'),
            ('IFNA(ROWS(NA()),77)', 77, None),
        ]:
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression),
                                 {'result': result, 'error': code})

    def test_rows_counts_range_rows_and_two_dimensional_literals(self):
        p = Parser()
        p.on('callRangeValue', lambda start, end, set_value:
             set_value([[None, 1], [error.DIV_ZERO, False], ['', None]]))
        self.assertEqual(p.parse('ROWS(A1:B3)'),
                         {'result': 3, 'error': None})
        self.assertEqual(p.parse('ROWS({1,2,3;4,5,6})'),
                         {'result': 2, 'error': None})

    def test_choose(self):
        p = Parser(debug=True)
        ret = p.parse('CHOOSE(1,1,3)')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)
        ret = p.parse('CHOOSE(2,1,3)')
        self.assertEqual(ret['result'], 3)
        self.assertEqual(ret['error'], None)
        ret = p.parse('CHOOSE(255,1,3)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#VALUE!')
        ret = p.parse('CHOOSE(3,1,3)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#VALUE!')
        ret = p.parse('CHOOSE(1)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#N/A')

    def test_match(self):
        p = Parser(debug=True)
        ret = p.parse('MATCH(39,{25,38,40,41},1)')
        self.assertEqual(ret['result'], 2)
        self.assertEqual(ret['error'], None)
        ret = p.parse('MATCH("f?o",{"eee","aaa","foa","foo"},0)')
        self.assertEqual(ret['result'], 4)
        self.assertEqual(ret['error'], None)
        ret = p.parse('MATCH(39,{25,38,40,41},-1)')
        self.assertEqual(ret['result'], 3)
        self.assertEqual(ret['error'], None)

    def test_match_accepts_flat_row_and_column_vectors(self):
        p = Parser()
        cases = [
            ([1, 2, 3, 4], 'MATCH(3,DATA(),0)', 3),
            ([10, 20, 30], 'MATCH(20,DATA(),0)', 2),
            ([10, 20, 30], 'MATCH(25,DATA(),1)', 2),
            ([10, 20, 30], 'MATCH(25,DATA())', 2),
            ([30, 20, 10], 'MATCH(15,DATA(),-1)', 2),
            (['Alpha', 'Beta', 'Gamma'], 'MATCH("b*",DATA(),0)', 2),
            ([20, 20, 30], 'MATCH(20,DATA(),0)', 1),
            ([20], 'MATCH(20,DATA(),0)', 1),
        ]
        for vector, expression, expected in cases:
            for values in (vector, [vector], [[value] for value in vector]):
                with self.subTest(values=values, expression=expression):
                    p.set_function('DATA', lambda values=values: values)
                    self.assertEqual(p.parse(expression),
                                     {'result': expected, 'error': None})

    def test_match_accepts_single_row_and_column_ranges(self):
        for label, values in [('A1:C1', [[10, 20, 30]]),
                              ('A1:A3', [[10], [20], [30]])]:
            with self.subTest(label=label):
                p = Parser()
                p.on('callRangeValue',
                     lambda start, end, set_value: set_value(values))
                self.assertEqual(p.parse('MATCH(20,' + label + ',0)'),
                                 {'result': 2, 'error': None})

    def test_match_rejects_nonvector_arrays(self):
        p = Parser()
        for values in ([[1, 2], [3, 4]], [[1], [2, 3]],
                       [1, [2]], [[1], 2], [[[1]]], [], [[]]):
            p.set_function('DATA', lambda values=values: values)
            for match_type in (-1, 0, 1):
                expression = 'MATCH(2,DATA(),' + str(match_type) + ')'
                with self.subTest(values=values, match_type=match_type):
                    self.assertEqual(p.parse(expression),
                                     {'result': None, 'error': '#N/A'})
                    self.assertEqual(p.parse('IFNA(' + expression + ',99)'),
                                     {'result': 99, 'error': None})

    def test_index(self):
        p = Parser(debug=True)
        ret = p.parse('INDEX({25,38,40,41},1)')
        self.assertEqual(ret['result'], 25)
        self.assertEqual(ret['error'], None)
        ret = p.parse('INDEX({1\\2\\3\\4;5\\6\\7\\8};2;1)')
        self.assertEqual(ret['result'], 5)
        self.assertEqual(ret['error'], None)
        ret = p.parse('INDEX({1;2;3;4};2;2)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#REF!')
        ret = p.parse('INDEX({1;2;3;4})')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#VALUE!')
        ret = p.parse('INDEX({1,2,3;4,5,6};;2)')
        self.assertEqual(ret['result'], [2, 5])
        self.assertEqual(ret['error'], None)
        ret = p.parse('INDEX({1,2,3},,2)')
        self.assertEqual(ret['result'], 2)
        self.assertEqual(ret['error'], None)
        ret = p.parse('SUM(INDEX({1,2,3;4,5,6};0;2))')
        self.assertEqual(ret['result'], 7)
        self.assertEqual(ret['error'], None)
        ret = p.parse('INDEX({1;2;3};2;)')
        self.assertEqual(ret['result'], 2)
        self.assertEqual(ret['error'], None)
        ret = p.parse('INDEX({1,2,3},2,)')
        self.assertEqual(ret['result'], 2)
        self.assertEqual(ret['error'], None)
        ret = p.parse('INDEX({1;2;3};;1/0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')
        ret = p.parse('INDEX({1;2;3};1/0;)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')
        ret = p.parse('INDEX(1,1,1)')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)
        ret = p.parse('INDEX(1,1,2)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#REF!')
        ret = p.parse('SUM(INDEX({1,2,3},0,0))')
        self.assertEqual(ret['result'], 6)
        self.assertEqual(ret['error'], None)
        ret = p.parse('INDEX({1}*2,1,1)')
        self.assertEqual(ret['result'], 2)
        self.assertEqual(ret['error'], None)
        ret = p.parse('INDEX({1,2}*2,1,1)')
        self.assertEqual(ret['result'], 2)
        self.assertEqual(ret['error'], None)
