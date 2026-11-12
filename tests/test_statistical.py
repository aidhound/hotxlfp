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

    def test_count_array_literals_coerce_only_numeric_text(self):
        p = Parser()
        self.assertEqual(p.parse('COUNT({1;"2";"text";TRUE;NULL;NA()})'),
                         {'result': 2, 'error': None})

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
                         {'result': 4, 'error': None})
        self.assertEqual(p.parse('COUNT(DAYVALUE(),DATE(2026,11,11))'),
                         {'result': 2, 'error': None})
        self.assertEqual(p.parse('COUNT("2026-11-11")'),
                         {'result': 1, 'error': None})
        self.assertEqual(p.parse('COUNT(DATA(),"2026-11-11")'),
                         {'result': 5, 'error': None})

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
