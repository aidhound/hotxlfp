# -*- coding: utf-8 -*-
import datetime
import unittest
from hotxlfp import Parser
from hotxlfp.formulas import error


class TestStatistical(unittest.TestCase):

    def test_average(self):
        p = Parser(debug=True)
        ret = p.parse('AVERAGE(1)')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)
        # with an array
        ret = p.parse('AVERAGE({1,2,3})')
        self.assertEqual(ret['result'], 2)
        self.assertEqual(ret['error'], None)

    def test_average_empty_inputs_return_handleable_division_errors(self):
        p = Parser()
        for values in ([], (), [None], [[None], [None]], [None, ''], ['text']):
            p.set_function('DATA', lambda values=values: values)
            for expression, result, code in [
                ('AVERAGE(DATA())', None, '#DIV/0!'),
                ('IFERROR(AVERAGE(DATA()),99)', 99, None),
                ('IFNA(AVERAGE(DATA()),77)', None, '#DIV/0!'),
            ]:
                with self.subTest(values=values, expression=expression):
                    self.assertEqual(p.parse(expression),
                                     {'result': result, 'error': code})

    def test_average_preserves_coercion_and_text_exclusion(self):
        p = Parser()
        for values, expected in [
            ([5, '7'], 6), ([5, 'text'], 5), ([5, ''], 5),
            ([5, None], 5), ([None, '', 7], 7), ([0], 0),
        ]:
            with self.subTest(values=values):
                p.set_function('DATA', lambda values=values: values)
                self.assertEqual(p.parse('AVERAGE(DATA())'),
                                 {'result': expected, 'error': None})

    def test_avedev_propagates_average_errors(self):
        p = Parser()
        for values in ([], [None], [None, ''], [5, error.NOT_AVAILABLE]):
            p.set_function('DATA', lambda values=values: values)
            code = '#N/A' if values == [5, error.NOT_AVAILABLE] else '#DIV/0!'
            with self.subTest(values=values):
                self.assertEqual(p.parse('AVEDEV(DATA())'),
                                 {'result': None, 'error': code})
                self.assertEqual(p.parse('IFERROR(AVEDEV(DATA()),99)'),
                                 {'result': 99, 'error': None})

    def test_avedev(self):
        p = Parser(debug=True)
        ret = p.parse('AVEDEV(1)')
        self.assertEqual(ret['result'], 0)
        self.assertEqual(ret['error'], None)
        # with an array
        ret = p.parse('AVEDEV({1;2;3;4})')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)

    def test_averagea(self):
        p = Parser(debug=True)
        ret = p.parse('AVERAGEA(1;"2")')
        self.assertEqual(ret['result'], 1.5)
        self.assertEqual(ret['error'], None)
        ret = p.parse('AVERAGEA(1;"2";TRUE;TRUE)')
        self.assertEqual(ret['result'], 1.25)
        self.assertEqual(ret['error'], None)

    def test_averagea_empty_inputs_return_handleable_division_errors(self):
        p = Parser()
        for values in ([], (), [None], [[None], [None]]):
            p.set_function('DATA', lambda values=values: values)
            for expression, result, code in [
                ('AVERAGEA(DATA())', None, '#DIV/0!'),
                ('IFERROR(AVERAGEA(DATA()),99)', 99, None),
                ('IFNA(AVERAGEA(DATA()),77)', None, '#DIV/0!'),
            ]:
                with self.subTest(values=values, expression=expression):
                    self.assertEqual(p.parse(expression),
                                     {'result': result, 'error': code})
        self.assertEqual(p.parse('AVERAGEA(NULL)'),
                         {'result': None, 'error': '#DIV/0!'})

    def test_averagea_preserves_numeric_string_and_text_coercion(self):
        p = Parser()
        for values, expected in [
            ([5, '7'], 6), ([5, 'text'], 2.5), ([5, ''], 2.5),
            ([5, True], 3), ([5, False], 2.5), ([5, None], 5),
            ([None, '', 7], 3.5), ([None, ''], 0), ([0], 0),
            ((5, '7'), 6), ([[5, None], ['7']], 6),
        ]:
            with self.subTest(values=values):
                p.set_function('DATA', lambda values=values: values)
                self.assertEqual(p.parse('AVERAGEA(DATA())'),
                                 {'result': expected, 'error': None})
        for expression, expected in [
            ('AVERAGEA("7",3)', 5), ('AVERAGEA("text",3)', 1.5),
            ('AVERAGEA("",3)', 1.5), ('AVERAGEA("")', 0),
        ]:
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression),
                                 {'result': expected, 'error': None})

    def test_averagea_preserves_input_errors_and_explicit_fallbacks(self):
        p = Parser()
        for source_error in (error.DIV_ZERO, error.NOT_AVAILABLE):
            p.set_function('DATA', lambda value=source_error: [5, value])
            cases = [
                ('AVERAGEA(DATA())', None, str(source_error)),
                ('IFERROR(AVERAGEA(DATA()),99)', 99, None),
                ('AVERAGEA(IFERROR(DATA(),0))', 2.5, None),
                ('AVERAGEA(IFERROR(DATA(),""))', 2.5, None),
            ]
            if source_error is error.NOT_AVAILABLE:
                cases.append(('IFNA(AVERAGEA(DATA()),77)', 77, None))
            else:
                cases.append(('IFNA(AVERAGEA(DATA()),77)', None, '#DIV/0!'))
            for expression, result, code in cases:
                with self.subTest(error=str(source_error), expression=expression):
                    self.assertEqual(p.parse(expression),
                                     {'result': result, 'error': code})

    def test_averagif(self):
        p = Parser(debug=True)
        ret = p.parse('AVERAGEIF({1;2;3;4};">2")')
        self.assertEqual(ret['result'], 3.5)
        self.assertEqual(ret['error'], None)
        ret = p.parse('AVERAGEIF({1;2;3;4};">2";{4;3;2;1})')
        self.assertEqual(ret['result'], 1.5)
        self.assertEqual(ret['error'], None)

    def test_count(self):
        p = Parser(debug=True)
        ret = p.parse('COUNT(1;"2")')
        self.assertEqual(ret['result'], 2)
        self.assertEqual(ret['error'], None)
        # with an array
        ret = p.parse('COUNT({1;2;3;4})')
        self.assertEqual(ret['result'], 4)
        self.assertEqual(ret['error'], None)

    def test_count_ignores_non_numeric_array_entries(self):
        p = Parser()
        cases = [
            ([None, 7], 1),
            ([None, '', 'text', '7', True, False, 0, 7, error.DIV_ZERO], 3),
            ([], 0),
            ((True, '7', None, -2.5), 2),
            ([[1, '2'], (False, 0, None), [error.NOT_AVAILABLE, '']], 3),
        ]
        for values, expected in cases:
            with self.subTest(values=values):
                p.set_function('DATA', lambda values=values: values)
                self.assertEqual(p.parse('COUNT(DATA())'),
                                 {'result': expected, 'error': None})
                self.assertEqual(p.parse('COUNT(DATA(),"3",TRUE())'),
                                 {'result': expected + 2, 'error': None})

    def test_count_direct_argument_coercion(self):
        p = Parser()
        p.set_function('ERR', lambda: error.DIV_ZERO)
        cases = [
            ('COUNT(7)', 1),
            ('COUNT("7")', 1),
            ('COUNT(TRUE())', 1),
            ('COUNT(FALSE())', 1),
            ('COUNT("text")', 0),
            ('COUNT(ERR())', 0),
            ('COUNT(NA())', 0),
            ('COUNT(NULL)', 0),
            ('COUNT("")', 0),
            ('COUNT("not-a-date")', 0),
            ('COUNT("2026-02-30")', 0),
            ('COUNT("22-MAY-2011")', 1),
            ('COUNT("2011/02/23")', 1),
            ('COUNT(0,-2,3.5)', 3),
        ]
        for expression, expected in cases:
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression),
                                 {'result': expected, 'error': None})

    def test_count_skips_nonfinite_scalar_values(self):
        p = Parser()
        for value in (
            float('nan'), float('inf'), float('-inf'),
            complex(float('nan'), 0), complex(0, float('inf')),
            'NaN', 'inf', '-Infinity', '1e309',
        ):
            with self.subTest(value=value):
                p.set_function('DATA', lambda value=value: value)
                self.assertEqual(p.parse('COUNT(DATA())'),
                                 {'result': 0, 'error': None})
                self.assertEqual(p.parse('COUNT(DATA(),0,"7",FALSE())'),
                                 {'result': 3, 'error': None})

    def test_count_skips_nonfinite_array_and_range_values(self):
        p = Parser()
        values = [
            float('nan'), float('inf'), float('-inf'), 'NaN', 'inf',
            '-Infinity', '1e309', complex(0, float('inf')),
            True, False, None, '', 'text', error.DIV_ZERO, 0, '7', 5,
        ]
        p.set_function('DATA', lambda: values)
        self.assertEqual(p.parse('COUNT(DATA())'),
                         {'result': 3, 'error': None})
        p.set_function('DATA', lambda: [[float('nan'), 'inf'],
                                       (float('-inf'), '3.5', 0)])
        self.assertEqual(p.parse('COUNT(DATA())'),
                         {'result': 2, 'error': None})
        p.on('callRangeValue', lambda start, end, set_value:
             set_value([[float('nan'), 0], ['Infinity', '7'], [True, False]]))
        self.assertEqual(p.parse('COUNT(A1:B3)'),
                         {'result': 2, 'error': None})

    def test_nonfinite_conversion_errors_reach_aggregate_handlers(self):
        p = Parser()
        for value in (float('nan'), float('inf'), float('-inf'), 'NaN', '1e309'):
            p.set_function('DATA', lambda value=value: [5, value, 7])
            for name in ('SUM', 'AVERAGE', 'AVERAGEA'):
                with self.subTest(value=value, function=name):
                    self.assertEqual(p.parse(name + '(DATA())'),
                                     {'result': None, 'error': '#NUM!'})
                    self.assertEqual(p.parse('IFERROR(' + name + '(DATA()),99)'),
                                     {'result': 99, 'error': None})
            self.assertEqual(p.parse('COUNT(DATA())'),
                             {'result': 2, 'error': None})
            self.assertEqual(p.parse('COUNTA(DATA())'),
                             {'result': 3, 'error': None})

    def test_nonparsing_aggregates_validate_numbers_without_coercing_text(self):
        p = Parser()
        for value in (float('nan'), float('inf')):
            p.set_function('DATA', lambda value=value: [5, value, 7])
            for name in ('MIN', 'MAX', 'VAR', 'PRODUCT'):
                with self.subTest(value=value, function=name):
                    self.assertEqual(p.parse(name + '(DATA())'),
                                     {'result': None, 'error': '#NUM!'})
        p.set_function('DATA', lambda: [5, 'NaN', 7])
        self.assertEqual(p.parse('MIN(DATA())'), {'result': 5, 'error': None})
        self.assertEqual(p.parse('MAX(DATA())'), {'result': 7, 'error': None})

    def test_countif_propagates_invalid_numeric_criteria(self):
        p = Parser()
        for criterion in ('NaN', '>inf', '-Infinity'):
            expression = 'COUNTIF({1;2},"' + criterion + '")'
            with self.subTest(criterion=criterion):
                self.assertEqual(p.parse(expression),
                                 {'result': None, 'error': '#NUM!'})
                self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                 {'result': 99, 'error': None})

    def test_count_preserves_finite_numbers_and_dates(self):
        p = Parser()
        values = [0, -0.0, 1, -2.5, '3.5', 10 ** 400, complex(3, 4),
                  datetime.date(2026, 11, 11), datetime.datetime(2026, 11, 11, 12)]
        p.set_function('DATA', lambda: values)
        self.assertEqual(p.parse('COUNT(DATA())'),
                         {'result': 9, 'error': None})
        for value in values:
            with self.subTest(value=value):
                p.set_function('DATA', lambda value=value: value)
                self.assertEqual(p.parse('COUNT(DATA())'),
                                 {'result': 1, 'error': None})

    def test_count_numeric_strings_match_existing_aggregate_coercion(self):
        p = Parser()
        p.set_function('DATA', lambda: [5, '7'])
        for name, expected in [('COUNT', 2), ('SUM', 12),
                                ('AVERAGE', 6), ('AVERAGEA', 6)]:
            with self.subTest(function=name):
                self.assertEqual(p.parse(name + '(DATA())'),
                                 {'result': expected, 'error': None})
        p.set_function('DATA', lambda: [True, False, 0, '7'])
        self.assertEqual(p.parse('COUNT(DATA())'),
                         {'result': 2, 'error': None})

    def test_count_array_literals_coerce_numeric_and_date_text(self):
        p = Parser()
        self.assertEqual(p.parse('COUNT({1;"2";"2026-11-11";"text";TRUE;NULL;NA()})'),
                         {'result': 3, 'error': None})

    def test_count_parses_date_text_in_arrays_using_direct_argument_rules(self):
        p = Parser()
        for value in ('2026-11-11', '22-MAY-2011', '2011/02/23'):
            p.set_function('DIRECT', lambda: value)
            self.assertEqual(p.parse('COUNT(DIRECT())'), {'result': 1, 'error': None})
            for values in ([value], [[value]], ((value,),)):
                p.set_function('DATA', lambda: values)
                with self.subTest(value=value, values=values):
                    self.assertEqual(p.parse('COUNT(DATA())'), {'result': 1, 'error': None})
        values = ['2026-11-11', 'not-a-date', '2026-02-30', None, '', True,
                  False, error.DIV_ZERO, error.NOT_AVAILABLE, 'NaN', '1e309', '7', 0]
        p.set_function('DATA', lambda: values)
        self.assertEqual(p.parse('COUNT(DATA())'), {'result': 3, 'error': None})
        self.assertEqual(p.parse('COUNT(DATA(),TRUE(),FALSE())'), {'result': 5, 'error': None})

    def test_count_parses_date_text_in_range_callbacks(self):
        p = Parser()
        values = [['2026-11-11', None], ['invalid', datetime.date(2026, 11, 11)], [True, '7']]
        p.on('callRangeValue', lambda start, end, set_value: set_value(values))
        self.assertEqual(p.parse('COUNT(A1:B3)'), {'result': 3, 'error': None})

    def test_count_range_callback_values(self):
        p = Parser()
        p.on('callRangeValue', lambda start, end, set_value:
             set_value([[None, 7], [True, '7'], [error.DIV_ZERO, '']]))
        self.assertEqual(p.parse('COUNT(A1:B3)'),
                         {'result': 2, 'error': None})

    def test_count_dates_and_date_looking_text(self):
        p = Parser()
        day = datetime.date(2026, 11, 11)
        moment = datetime.datetime(2026, 11, 11, 12)
        p.set_function('DATA', lambda: [day, moment, '2026-11-11', '7', True, 0])
        p.set_function('DAYVALUE', lambda: day)
        self.assertEqual(p.parse('COUNT(DATA())'),
                         {'result': 5, 'error': None})
        self.assertEqual(p.parse('COUNT(DAYVALUE(),DATE(2026,11,11))'),
                         {'result': 2, 'error': None})
        self.assertEqual(p.parse('COUNT("2026-11-11")'),
                         {'result': 1, 'error': None})
        self.assertEqual(p.parse('COUNT(DATA(),"2026-11-11")'),
                         {'result': 6, 'error': None})

    def test_counta(self):
        p = Parser(debug=True)
        ret = p.parse('COUNTA(1;"2")')
        self.assertEqual(ret['result'], 2)
        self.assertEqual(ret['error'], None)
        # with an array
        ret = p.parse('COUNTA({1;2;3;""})')
        self.assertEqual(ret['result'], 3)
        self.assertEqual(ret['error'], None)
        ret = p.parse('COUNTA(1;2;3;NULL)')
        self.assertEqual(ret['result'], 3)
        self.assertEqual(ret['error'], None)

    def test_blank_functions_agree_on_scalar_values(self):
        p = Parser()
        for value, blank in [
            (None, True), ('', True), (0, False), (False, False),
            (' ', False), ('Alice', False), (error.DIV_ZERO, False),
        ]:
            p.set_function('DATA', lambda value=value: value)
            for name, expected in [('ISBLANK', blank),
                                    ('COUNTA', int(not blank)),
                                    ('COUNTBLANK', int(blank))]:
                with self.subTest(value=value, function=name):
                    self.assertEqual(p.parse(name + '(DATA())'),
                                     {'result': expected, 'error': None})
        p.set_function('DATA', lambda: [None, '', 7, False, error.DIV_ZERO])
        self.assertEqual(p.parse('COUNTA(DATA())'),
                         {'result': 3, 'error': None})
        self.assertEqual(p.parse('COUNTBLANK(DATA())'),
                         {'result': 2, 'error': None})

    def test_countblank(self):
        p = Parser(debug=True)
        ret = p.parse('COUNTBLANK(1;"2")')
        self.assertEqual(ret['result'], 0)
        self.assertEqual(ret['error'], None)
        ret = p.parse('COUNTBLANK(1;2;3;"")')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)
        ret = p.parse('COUNTBLANK(1;2;3;NULL)')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)
        # with an array
        ret = p.parse('COUNTBLANK({1;2;3;4})')
        self.assertEqual(ret['result'], 0)
        self.assertEqual(ret['error'], None)
        ret = p.parse('COUNTBLANK({1;2;3;""})')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)

    def test_countif(self):
        p = Parser(debug=True)
        ret = p.parse('COUNTIF({1;3};">2")')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)
        ret = p.parse('COUNTIF({"foo";"bar"};"foo")')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)
        ret = p.parse('COUNTIF({"foo bar";"baz"};"foo bar")')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)
        ret = p.parse(u'COUNTIF({"áà ãâä";"baz"}; "áà ãâä")')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)
        ret = p.parse(u'COUNTIF({"áà ã,â,ä";"baz"}; "áà ã,â,ä")')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)
        ret = p.parse(u'COUNTIF({"áà ã(â)ä";"baz"}; "áà ã(â)ä")')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)

    def test_max(self):
        p = Parser(debug=True)
        ret = p.parse('MAX({1;3};4)')
        self.assertEqual(ret['result'], 4)
        self.assertEqual(ret['error'], None)
        ret = p.parse('MAX({1;2;3})')
        self.assertEqual(ret['result'], 3)
        self.assertEqual(ret['error'], None)

    def test_min(self):
        p = Parser(debug=True)
        ret = p.parse('MIN({1;3};0)')
        self.assertEqual(ret['result'], 0)
        self.assertEqual(ret['error'], None)
        ret = p.parse('MIN({1;2;3})')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)

    def test_var(self):
        p = Parser(debug=True)
        ret = p.parse('VAR.S({1345;1301;1368;1322;1310;1370;1318;1350;1303;1299})')
        self.assertTrue(str(ret['result']).startswith('754.2'))
        self.assertEqual(ret['error'], None)
        ret = p.parse('VAR.P({1345;1301;1368;1322;1310;1370;1318;1350;1303;1299})')
        self.assertEqual(ret['result'], 678.84)
        self.assertEqual(ret['error'], None)

    def test_stdev(self):
        p = Parser(debug=True)
        ret = p.parse('STDEV.S({1345;1301;1368;1322;1310;1370;1318;1350;1303;1299})')
        self.assertTrue(str(ret['result']).startswith('27.46'))
        self.assertEqual(ret['error'], None)
        ret = p.parse('STDEV.P({1345;1301;1368;1322;1310;1370;1318;1350;1303;1299})')
        self.assertTrue(str(ret['result']).startswith('26.05'))
        self.assertEqual(ret['error'], None)

    def test_median(self):
        p = Parser(debug=True)
        ret = p.parse('MEDIAN({1;2;3;4;5;6})')
        self.assertEqual(ret['result'], 3.5)
        self.assertEqual(ret['error'], None)
        ret = p.parse('MEDIAN({1;2;3;4;5})')
        self.assertEqual(ret['result'], 3)
        self.assertEqual(ret['error'], None)
        ret = p.parse('MEDIAN({1;2;3;4;5;"lala"})')
        self.assertEqual(ret['result'], 3)
        self.assertEqual(ret['error'], None)

    def test_mode(self):
        p = Parser(debug=True)
        ret = p.parse('MODE({5.6;4;4;3;2;4})')
        self.assertEqual(ret['result'], 4)
        self.assertEqual(ret['error'], None)

    def test_averagifs(self):
        p = Parser(debug=True)
        ret = p.parse('AVERAGEIFS({1;2;3;4};{1;2;3;4};">2")')
        self.assertEqual(ret['result'], 3.5)
        self.assertEqual(ret['error'], None)
        ret = p.parse('AVERAGEIFS({1;2;3;4};{4;3;2;1};">2")')
        self.assertEqual(ret['result'], 1.5)
        self.assertEqual(ret['error'], None)
        ret = p.parse('AVERAGEIFS({1;2;3;4};{4;3;2;1};">2";{1;2;3;4};"<> 3")')
        self.assertEqual(ret['result'], 1.5)
        self.assertEqual(ret['error'], None)

    def test_averageifs_accepts_flat_row_column_and_matrix_ranges(self):
        p = Parser()
        for shape in (lambda values: values,
                      lambda values: [values],
                      lambda values: [[value] for value in values],
                      lambda values: [values[:2], values[2:]],
                      lambda values: (tuple(values[:2]), tuple(values[2:]))):
            averages = shape([10, 20, 30, 40])
            first = shape([1, 2, 3, 4])
            second = shape(['x', 'y', 'x', 'y'])
            p.set_function('DATA', lambda: averages)
            p.set_function('FIRST', lambda: first)
            p.set_function('SECOND', lambda: second)
            for expression in ('AVERAGEIFS(DATA(),FIRST(),">1")',
                               'AVERAGEIFS(DATA(),FIRST(),">2",SECOND(),"x")'):
                with self.subTest(averages=averages, expression=expression):
                    self.assertEqual(p.parse(expression), {'result': 30, 'error': None})

    def test_averageifs_accepts_nested_range_callbacks(self):
        for label, values, expected in (
            ('A1:C1', [[1, 2, 3]], 2.5),
            ('A1:A3', [[1], [2], [3]], 2.5),
            ('A1:B2', [[1, 2], [3, 4]], 3),
        ):
            p = Parser()
            p.on('callRangeValue', lambda start, end, set_value: set_value(values))
            expression = 'AVERAGEIFS(' + label + ',' + label + ',">1")'
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': expected, 'error': None})

    def test_averageifs_treats_flat_vectors_as_columns(self):
        p = Parser()
        for averages, criteria in (([10, 20, 30], [[1], [2], [3]]),
                                   ([[10], [20], [30]], [1, 2, 3])):
            p.set_function('DATA', lambda: averages)
            p.set_function('CRITERIA', lambda: criteria)
            with self.subTest(averages=averages, criteria=criteria):
                self.assertEqual(p.parse('AVERAGEIFS(DATA(),CRITERIA(),">1")'),
                                 {'result': 25, 'error': None})

    def test_averageifs_rejects_mismatched_and_invalid_range_shapes(self):
        p = Parser()
        for averages, criteria in (
            ([[10, 20]], [[1], [2]]),
            ([[10, 20], [30, 40]], [[1, 2, 3, 4]]),
            ([[10], [20, 30]], [[1], [2, 3]]),
            ([10, [20]], [1, [2]]),
            ([[[10]]], [[[1]]]),
            ([10, 20], [1, 2, 3]),
            ([10, 20, 30], [1, 2]),
            ([10, 20], 'text'),
        ):
            p.set_function('DATA', lambda: averages)
            p.set_function('CRITERIA', lambda: criteria)
            expression = 'AVERAGEIFS(DATA(),CRITERIA(),">1")'
            with self.subTest(averages=averages, criteria=criteria):
                self.assertEqual(p.parse(expression), {'result': None, 'error': '#VALUE!'})
                self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                 {'result': 99, 'error': None})

    def test_averageifs_no_matches_and_empty_ranges_return_div_zero(self):
        p = Parser()
        for values in ([1, 2, 3], [[1, 2, 3]], [[1], [2], [3]],
                       [[1, 2], [3, 4]], []):
            p.set_function('DATA', lambda: values)
            expression = 'AVERAGEIFS(DATA(),DATA(),">9")'
            with self.subTest(values=values):
                self.assertEqual(p.parse(expression), {'result': None, 'error': '#DIV/0!'})
                self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                 {'result': 99, 'error': None})
                self.assertEqual(p.parse('IFNA(' + expression + ',77)'),
                                 {'result': None, 'error': '#DIV/0!'})

    def test_maxifs(self):
        p = Parser(debug=True)
        ret = p.parse('MAXIFS({1;2;3;4};{1;2;3;4};">2")')
        self.assertEqual(ret['result'], 4)
        self.assertEqual(ret['error'], None)
        ret = p.parse('MAXIFS({1;2;3;4};{4;3;2;1};">2")')
        self.assertEqual(ret['result'], 2)
        self.assertEqual(ret['error'], None)
        ret = p.parse('MAXIFS({1;2;3;4};{4;3;2;1};">3";{1;2;3;4};"<>3")')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)

    def test_maxifs_accepts_flat_row_column_and_matrix_ranges(self):
        p = Parser()
        for shape in (lambda values: values,
                      lambda values: [values],
                      lambda values: [[value] for value in values],
                      lambda values: [values[:2], values[2:]],
                      lambda values: (tuple(values[:2]), tuple(values[2:]))):
            maxima = shape([10, 20, 30, 40])
            first = shape([1, 2, 3, 4])
            second = shape(['x', 'y', 'x', 'y'])
            p.set_function('DATA', lambda: maxima)
            p.set_function('FIRST', lambda: first)
            p.set_function('SECOND', lambda: second)
            for expression, expected in (
                ('MAXIFS(DATA(),FIRST(),">1")', 40),
                ('MAXIFS(DATA(),FIRST(),"<3",SECOND(),"x")', 10),
            ):
                with self.subTest(maxima=maxima, expression=expression):
                    self.assertEqual(p.parse(expression), {'result': expected, 'error': None})

    def test_maxifs_accepts_nested_range_callbacks(self):
        for label, values, expected in (
            ('A1:C1', [[1, 2, 3]], 3),
            ('A1:A3', [[1], [2], [3]], 3),
            ('A1:B2', [[1, 2], [3, 4]], 4),
        ):
            p = Parser()
            p.on('callRangeValue', lambda start, end, set_value: set_value(values))
            expression = 'MAXIFS(' + label + ',' + label + ',">1")'
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': expected, 'error': None})

    def test_maxifs_treats_flat_vectors_as_columns(self):
        p = Parser()
        for maxima, criteria in (([10, 20, 30], [[1], [2], [3]]),
                                 ([[10], [20], [30]], [1, 2, 3])):
            p.set_function('DATA', lambda: maxima)
            p.set_function('CRITERIA', lambda: criteria)
            with self.subTest(maxima=maxima, criteria=criteria):
                self.assertEqual(p.parse('MAXIFS(DATA(),CRITERIA(),">1")'),
                                 {'result': 30, 'error': None})

    def test_maxifs_rejects_mismatched_and_invalid_range_shapes(self):
        p = Parser()
        for maxima, criteria in (
            ([[10, 20]], [[1], [2]]),
            ([[10, 20], [30, 40]], [[1, 2, 3, 4]]),
            ([[10], [20, 30]], [[1], [2, 3]]),
            ([10, [20]], [1, [2]]),
            ([[[10]]], [[[1]]]),
            ([10, 20], [1, 2, 3]),
            ([10, 20, 30], [1, 2]),
            ([10, 20], 'text'),
        ):
            p.set_function('DATA', lambda: maxima)
            p.set_function('CRITERIA', lambda: criteria)
            expression = 'MAXIFS(DATA(),CRITERIA(),">1")'
            with self.subTest(maxima=maxima, criteria=criteria):
                self.assertEqual(p.parse(expression), {'result': None, 'error': '#VALUE!'})
                self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                 {'result': 99, 'error': None})

    def test_maxifs_preserves_negative_maxima_and_zero_for_no_matches(self):
        p = Parser()
        for vector, expected in (([-5, -2, -9], -2), ([-5], -5),
                                  ([100, -5, -2], -2), ([-5, 0, -9], -5), ([], 0)):
            for values in (vector, [vector], [[value] for value in vector]):
                p.set_function('DATA', lambda: values)
                for criteria, result in (("<0", expected), (">999", 0)):
                    expression = 'MAXIFS(DATA(),DATA(),"' + criteria + '")'
                    with self.subTest(values=values, expression=expression):
                        self.assertEqual(p.parse(expression), {'result': result, 'error': None})
        self.assertEqual(p.parse('MAXIFS({-5,0,-9},{-5,0,-9},"<=0")'),
                         {'result': 0, 'error': None})

    def test_slope(self):
        p = Parser(debug=True)
        ret = p.parse('SLOPE(1;2;3;4;1;2;3;4)')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)
        ret = p.parse('SLOPE(6,2,-2,-4,-6,-2,0,2,3,4)')
        self.assertEqual(ret['result'], -2)
        self.assertEqual(ret['error'], None)
        ret = p.parse('SLOPE(6,1,2,4)')
        self.assertEqual(ret['result'], -2.5)
        self.assertEqual(ret['error'], None)
        ret = p.parse('SLOPE(6,1)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')

    def test_large_accepts_flat_row_column_and_matrix_arrays(self):
        p = Parser()
        for values in ([29, 14, 33, 19], [[29, 14, 33, 19]],
                       [[29], [14], [33], [19]], [[29, 14], [33, 19]],
                       ((29, 14), (33, 19))):
            p.set_function('DATA', lambda: values)
            for rank, expected in ((1, 33), (2, 29), (4, 14)):
                expression = 'LARGE(DATA(),' + str(rank) + ')'
                with self.subTest(values=values, rank=rank):
                    self.assertEqual(p.parse(expression), {'result': expected, 'error': None})

    def test_large_accepts_nested_range_callbacks(self):
        for label, values, rank, expected in (
            ('A1:C1', [[1, 3, 2]], 2, 2),
            ('A1:A3', [[1], [3], [2]], 2, 2),
            ('A1:B2', [[1, 4], [3, 2]], 3, 2),
        ):
            p = Parser()
            p.on('callRangeValue', lambda start, end, set_value: set_value(values))
            expression = 'LARGE(' + label + ',' + str(rank) + ')'
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': expected, 'error': None})

    def test_large_checks_rank_against_collected_numbers(self):
        p = Parser()
        for values, rank, expected, code in (
            ([10, None, 5], 2, 5, None),
            ([10, None, 5], 3, None, '#NUM!'),
            ([None, None], 1, None, '#NUM!'),
            ([], 1, None, '#NUM!'),
            ([[]], 1, None, '#NUM!'),
            ([[1, 2, 3]], 4, None, '#NUM!'),
            ([[1, 2, 3]], 0, None, '#NUM!'),
            ([[1, 2, 3]], -1, None, '#NUM!'),
            ([5, 5, 2], 2, 5, None),
            ([-5, -2, -9], 2, -5, None),
            ([10, '5', 'text', None], 3, 0, None),
        ):
            p.set_function('DATA', lambda: values)
            expression = 'LARGE(DATA(),' + str(rank) + ')'
            with self.subTest(values=values, rank=rank):
                self.assertEqual(p.parse(expression), {'result': expected, 'error': code})
                if code:
                    self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                     {'result': 99, 'error': None})

    def test_large_preserves_errors_while_collecting_nested_values(self):
        p = Parser()
        for source_error in (error.DIV_ZERO, error.NOT_AVAILABLE, error.NUM):
            for values in ([5, source_error], [[5, source_error]], [[5], [source_error]]):
                p.set_function('DATA', lambda: values)
                expression = 'LARGE(DATA(),2)'
                with self.subTest(values=values):
                    self.assertEqual(p.parse(expression),
                                     {'result': None, 'error': str(source_error)})
                    self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                     {'result': 99, 'error': None})
                    expected = ({'result': 77, 'error': None}
                                if source_error is error.NOT_AVAILABLE
                                else {'result': None, 'error': str(source_error)})
                    self.assertEqual(p.parse('IFNA(' + expression + ',77)'), expected)

    def test_large(self):
        p = Parser(debug=True)
        ret = p.parse('LARGE({29,14,33,19,17},1)')
        self.assertEqual(ret['result'], 33)
        self.assertEqual(ret['error'], None)
        ret = p.parse('LARGE({29,14,33,19,17},3)')
        self.assertEqual(ret['result'], 19)
        self.assertEqual(ret['error'], None)
        ret = p.parse('LARGE({29,14,33,19,17},0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#NUM!')
        ret = p.parse('LARGE({29,14,33,19,17},5)')
        self.assertEqual(ret['result'], 14)
        self.assertEqual(ret['error'], None)
        ret = p.parse('LARGE({29,14,33,19,17},6)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#NUM!')
        ret = p.parse('LARGE({29,14,33,19,17},"a")')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#VALUE!')
