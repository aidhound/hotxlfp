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

    def test_choose_preserves_selector_and_selected_errors(self):
        p = Parser()
        for source_error in (error.DIV_ZERO, error.NOT_AVAILABLE, error.NUM):
            p.set_function('ERR', lambda value=source_error: value)
            for source in (str(source_error), 'ERR()'):
                for args in (source + ',10,20', '1,' + source + ',20',
                             '2,10,' + source):
                    expression = 'CHOOSE(' + args + ')'
                    with self.subTest(expression=expression, error=str(source_error)):
                        self.assertEqual(p.parse(expression),
                                         {'result': None, 'error': str(source_error)})
                        self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                         {'result': 99, 'error': None})
                        expected = ({'result': 77, 'error': None}
                                    if source_error is error.NOT_AVAILABLE
                                    else {'result': None, 'error': str(source_error)})
                        self.assertEqual(p.parse('IFNA(' + expression + ',77)'), expected)

    def test_choose_ignores_unselected_errors_and_preserves_validation(self):
        p = Parser()
        for expression, result, code in (
            ('CHOOSE(1,10,#DIV/0!)', 10, None),
            ('CHOOSE(2,#N/A,20)', 20, None),
            ('CHOOSE(#NUM!,#N/A,20)', None, '#NUM!'),
            ('CHOOSE(1,0,#N/A)', 0, None),
            ('CHOOSE(1,FALSE(),#N/A)', False, None),
            ('CHOOSE(1,"#N/A",#DIV/0!)', '#N/A', None),
            ('CHOOSE(0,10,20)', None, '#VALUE!'),
            ('CHOOSE(3,10,20)', None, '#VALUE!'),
            ('CHOOSE()', None, '#N/A'),
            ('CHOOSE(1)', None, '#N/A'),
        ):
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': result, 'error': code})

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

    def test_match_preserves_direct_error_arguments(self):
        p = Parser()
        for source_error in (error.DIV_ZERO, error.NOT_AVAILABLE, error.NUM):
            p.set_function('ERR', lambda value=source_error: value)
            for source in (str(source_error), 'ERR()'):
                for args in (source + ',{1,2}', '1,' + source,
                             source + ',{1,2},0', '1,' + source + ',0',
                             '1,{1,2},' + source):
                    expression = 'MATCH(' + args + ')'
                    with self.subTest(expression=expression, error=str(source_error)):
                        self.assertEqual(p.parse(expression),
                                         {'result': None, 'error': str(source_error)})
                        self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                         {'result': 99, 'error': None})
                        expected = ({'result': 77, 'error': None}
                                    if source_error is error.NOT_AVAILABLE
                                    else {'result': None, 'error': str(source_error)})
                        self.assertEqual(p.parse('IFNA(' + expression + ',77)'), expected)

    def test_match_preserves_error_order_without_rejecting_whole_vectors(self):
        p = Parser()
        for expression, result, code in (
            ('MATCH(#DIV/0!,#N/A,0)', None, '#DIV/0!'),
            ('MATCH(1,#NUM!,#DIV/0!)', None, '#NUM!'),
            ('MATCH(#N/A,{1,2},#DIV/0!)', None, '#N/A'),
            ('MATCH("#N/A",{"text","#N/A"},0)', 2, None),
            ('MATCH(3,{1,2},0)', None, '#N/A'),
            ('IFNA(MATCH(3,{1,2},0),77)', 77, None),
        ):
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': result, 'error': code})
        for values in ([1, error.DIV_ZERO], [[1, error.DIV_ZERO]],
                       [[1], [error.DIV_ZERO]]):
            p.set_function('DATA', lambda values=values: values)
            for match_type in (-1, 0, 1):
                expression = 'MATCH(1,DATA(),' + str(match_type) + ')'
                with self.subTest(values=values, expression=expression):
                    self.assertEqual(p.parse(expression), {'result': 1, 'error': None})

    def test_match_skips_error_cells_in_exact_searches(self):
        p = Parser()
        for source_error in (error.NOT_AVAILABLE, error.DIV_ZERO, error.NUM):
            for vector, target, expected in (
                ([source_error, 'Beta'], '"b*"', 2),
                (['a', source_error, 'b'], '"b"', 3),
                ([source_error, 2], '2', 2),
                ([1, source_error, 3], '3', 3),
            ):
                for values in (vector, [vector], [[item] for item in vector]):
                    p.set_function('DATA', lambda values=values: values)
                    expression = 'MATCH(' + target + ',DATA(),0)'
                    with self.subTest(values=values, expression=expression):
                        for formula in (expression, 'IFERROR(' + expression + ',99)',
                                        'IFNA(' + expression + ',77)'):
                            self.assertEqual(p.parse(formula), {'result': expected, 'error': None})

    def test_match_skips_error_cells_in_approximate_searches(self):
        p = Parser()
        for source_error in (error.NOT_AVAILABLE, error.DIV_ZERO, error.NUM):
            for vector, target, match_type, expected in (
                ([source_error, 10, 30], '20', ',1', 2),
                ([10, source_error, 30], '20', ',1', 1),
                ([30, source_error, 10], '20', ',-1', 1),
                ([source_error, 30, 10], '20', ',-1', 2),
                (['a', source_error, 'c'], '"b"', ',1', 1),
                (['c', source_error, 'a'], '"b"', ',-1', 1),
                ([source_error, 20], '20', ',1', 2),
                ([source_error, 10, 30], '20', '', 2),
            ):
                for values in (vector, [vector], [[item] for item in vector]):
                    p.set_function('DATA', lambda values=values: values)
                    expression = 'MATCH(' + target + ',DATA()' + match_type + ')'
                    with self.subTest(values=values, expression=expression):
                        self.assertEqual(p.parse(expression), {'result': expected, 'error': None})

    def test_match_returns_na_when_skipping_errors_leaves_no_match(self):
        p = Parser()
        for vector, target, match_type in (
            ([error.NOT_AVAILABLE, error.DIV_ZERO, error.NUM], '2', -1),
            ([error.NOT_AVAILABLE, error.DIV_ZERO, error.NUM], '2', 0),
            ([error.NOT_AVAILABLE, error.DIV_ZERO, error.NUM], '2', 1),
            (['a', error.DIV_ZERO], '"b"', 0),
            ([error.NUM, 10], '5', 1),
            ([30, error.NUM], '40', -1),
        ):
            for values in (vector, [vector], [[item] for item in vector]):
                p.set_function('DATA', lambda values=values: values)
                expression = 'MATCH(' + target + ',DATA(),' + str(match_type) + ')'
                with self.subTest(values=values, expression=expression):
                    self.assertEqual(p.parse(expression), {'result': None, 'error': '#N/A'})
                    self.assertEqual(p.parse('IFNA(' + expression + ',77)'),
                                     {'result': 77, 'error': None})
                    self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                     {'result': 99, 'error': None})

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

    def test_index_preserves_direct_error_arguments(self):
        p = Parser()
        valid_args = ['{10,20}', '1', '1', '1']
        for source_error in (error.DIV_ZERO, error.NOT_AVAILABLE, error.NUM):
            p.set_function('ERR', lambda value=source_error: value)
            for position in range(len(valid_args)):
                for source in (str(source_error), 'ERR()'):
                    args = valid_args.copy()
                    args[position] = source
                    expression = 'INDEX(' + ','.join(args) + ')'
                    with self.subTest(expression=expression, error=str(source_error)):
                        self.assertEqual(p.parse(expression),
                                         {'result': None, 'error': str(source_error)})
                        self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                         {'result': 99, 'error': None})
                        expected = ({'result': 77, 'error': None}
                                    if source_error is error.NOT_AVAILABLE
                                    else {'result': None, 'error': str(source_error)})
                        self.assertEqual(p.parse('IFNA(' + expression + ',77)'), expected)

    def test_index_preserves_errors_before_array_validation_and_wrapping(self):
        p = Parser()
        p.set_function('EMPTY', lambda: [])
        for source_error in (error.DIV_ZERO, error.NOT_AVAILABLE, error.NUM):
            for args in (str(source_error) + ',2', str(source_error) + ',,2',
                         str(source_error) + ',0,0', str(source_error) + ',#VALUE!',
                         'NULL,' + str(source_error), 'EMPTY(),' + str(source_error)):
                expression = 'INDEX(' + args + ')'
                with self.subTest(expression=expression):
                    self.assertEqual(p.parse(expression),
                                     {'result': None, 'error': str(source_error)})
                    self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                     {'result': 99, 'error': None})

    def test_index_keeps_selected_array_errors_and_conversion_checks(self):
        p = Parser()
        p.set_function('DATA', lambda: [[error.DIV_ZERO, 20], [30, error.NOT_AVAILABLE]])
        for expression, result, code in (
            ('INDEX(DATA(),1,2)', 20, None),
            ('INDEX(DATA(),2,1)', 30, None),
            ('INDEX(DATA(),1,1)', None, '#DIV/0!'),
            ('INDEX(DATA(),2,2)', None, '#N/A'),
            ('IFERROR(INDEX(DATA(),0,2),99)', [20, 99], None),
            ('IFERROR(INDEX(DATA(),1,0),99)', [99, 20], None),
            ('INDEX({10,20},"2")', 20, None),
            ('INDEX({10,20},"bad")', None, '#VALUE!'),
            ('INDEX({10,20},1,"bad")', None, '#VALUE!'),
        ):
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': result, 'error': code})

    def test_index_accepts_flat_row_and_column_vectors(self):
        p = Parser()
        for values in ([10, 20, 30], [[10, 20, 30]], [[10], [20], [30]]):
            p.set_function('DATA', lambda values=values: values)
            for expression, expected in [('INDEX(DATA(),2)', 20),
                                          ('INDEX(DATA(),2,)', 20),
                                          ('INDEX(DATA(),0)', [10, 20, 30])]:
                with self.subTest(values=values, expression=expression):
                    self.assertEqual(p.parse(expression),
                                     {'result': expected, 'error': None})

    def test_index_preserves_row_and_column_coordinates(self):
        p = Parser()
        for values, cases in [
            ([[10, 20, 30]], [('INDEX(DATA(),,2)', 20),
                              ('INDEX(DATA(),1,2)', 20),
                              ('INDEX(DATA(),0,2)', [20]),
                              ('INDEX(DATA(),1,0)', [10, 20, 30]),
                              ('IFERROR(INDEX(DATA(),2,1),99)', 99)]),
            ([[10], [20], [30]], [('INDEX(DATA(),2,1)', 20),
                                  ('INDEX(DATA(),,1)', [10, 20, 30]),
                                  ('INDEX(DATA(),0,1)', [10, 20, 30]),
                                  ('INDEX(DATA(),2,0)', [20]),
                                  ('IFERROR(INDEX(DATA(),1,2),99)', 99)]),
            ([[10, 20], [30, 40]], [('INDEX(DATA(),2)', [30, 40]),
                                   ('INDEX(DATA(),,2)', [20, 40]),
                                   ('INDEX(DATA(),2,2)', 40)]),
            ([[20]], [('INDEX(DATA(),1)', 20), ('INDEX(DATA(),,1)', 20)]),
        ]:
            p.set_function('DATA', lambda values=values: values)
            cases.append(('INDEX(DATA(),0,0)', values))
            for expression, expected in cases:
                with self.subTest(values=values, expression=expression):
                    self.assertEqual(p.parse(expression),
                                     {'result': expected, 'error': None})

    def test_index_vector_positions_outside_bounds_return_ref(self):
        p = Parser()
        for values in ([10, 20, 30], [[10, 20, 30]], [[10], [20], [30]], []):
            p.set_function('DATA', lambda values=values: values)
            for indices in ('-1', '4', '-1,1', '1,-1'):
                expression = 'INDEX(DATA(),' + indices + ')'
                with self.subTest(values=values, indices=indices):
                    self.assertEqual(p.parse(expression),
                                     {'result': None, 'error': '#REF!'})
                    self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                     {'result': 99, 'error': None})

    def test_index_accepts_single_row_and_column_ranges(self):
        for label, values in [('A1:C1', [[10, 20, 30]]),
                              ('A1:A3', [[10], [20], [30]])]:
            with self.subTest(label=label):
                p = Parser()
                p.on('callRangeValue',
                     lambda start, end, set_value: set_value(values))
                self.assertEqual(p.parse('INDEX(' + label + ',2)'),
                                 {'result': 20, 'error': None})

    def test_index_vector_selection_preserves_selected_errors(self):
        p = Parser()
        for values in ([error.DIV_ZERO, 20], [[error.DIV_ZERO, 20]],
                       [[error.DIV_ZERO], [20]]):
            with self.subTest(values=values):
                p.set_function('DATA', lambda values=values: values)
                self.assertEqual(p.parse('INDEX(DATA(),2)'),
                                 {'result': 20, 'error': None})
                self.assertEqual(p.parse('INDEX(DATA(),1)'),
                                 {'result': None, 'error': '#DIV/0!'})
                self.assertEqual(p.parse('IFERROR(INDEX(DATA(),1),99)'),
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
