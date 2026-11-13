# -*- coding: utf-8 -*-
import unittest
import datetime
from hotxlfp import Parser
from hotxlfp.formulas import error


class TestOperators(unittest.TestCase):

    def test_nonfinite_arithmetic_results_return_numeric_errors(self):
        p = Parser()
        p.set_function('BIG', lambda: 1e308)
        p.set_function('SMALL', lambda: 1e-308)
        p.set_function('HUGE', lambda: 10 ** 400)
        p.set_function('COMPLEX', lambda: complex(1e308, 1e308))
        for expression in ('BIG()+BIG()', '-BIG()-BIG()', 'BIG()*BIG()',
                           'BIG()/SMALL()', 'COMPLEX()*COMPLEX()',
                           'HUGE()+1.0', 'HUGE()*1.0', 'HUGE()/1',
                           'DATE(2026,1,1)*BIG()'):
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression),
                                 {'result': None, 'error': '#NUM!'})
                self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                 {'result': 99, 'error': None})
        self.assertEqual(p.parse('IFERROR(BIG()*BIG()=0,99)'),
                         {'result': 99, 'error': None})

    def test_arithmetic_result_validation_preserves_valid_results(self):
        p = Parser()
        p.set_function('HUGE', lambda: 10 ** 400)
        for expression, result, code in [
            ('HUGE()+1', 10 ** 400 + 1, None),
            ('HUGE()/HUGE()', 1.0, None),
            ('2^8', 256, None),
            ('2^1024', 2 ** 1024, None),
            ('50%', 0.5, None),
            ('1/0', None, '#DIV/0!'),
            ('0/0', None, '#DIV/0!'),
        ]:
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression),
                                 {'result': result, 'error': code})

    def test_percentage_overflow_returns_a_handleable_numeric_error(self):
        p = Parser()
        expression = '9' * 400 + '%'
        self.assertEqual(p.parse(expression),
                         {'result': None, 'error': '#NUM!'})
        self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                         {'result': 99, 'error': None})

    def test_array_arithmetic_keeps_numeric_errors_as_elements(self):
        p = Parser()
        for value in (1e308, 10 ** 400):
            p.set_function('DATA', lambda: [[value, 3], [4, value]])
            for expression in ('DATA()*2.0', '2.0*DATA()'):
                with self.subTest(value=value, expression=expression):
                    self.assertEqual(p.parse(expression),
                                     {'result': [[error.NUM, 6], [8, error.NUM]],
                                      'error': None})
                    self.assertEqual(p.parse('IFERROR(' + expression + ',0)'),
                                     {'result': [[0, 6], [8, 0]], 'error': None})

    def test_nonfinite_arithmetic_inputs_preserve_numeric_error(self):
        p = Parser()
        for value in (float('nan'), float('inf'), 'NaN', '1e309'):
            p.set_function('DATA', lambda value=value: value)
            for op in ('+', '-', '*', '/'):
                for expression in ('DATA()' + op + '1', '1' + op + 'DATA()'):
                    with self.subTest(value=value, expression=expression):
                        self.assertEqual(p.parse(expression),
                                         {'result': None, 'error': '#NUM!'})
                        self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                         {'result': 99, 'error': None})

    def test_overflowing_decimal_literals_preserve_numeric_error(self):
        p = Parser()
        literal = '9' * 400 + '.0'
        for expression in (literal, '-' + literal):
            with self.subTest(negative=expression.startswith('-')):
                self.assertEqual(p.parse(expression),
                                 {'result': None, 'error': '#NUM!'})
                self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                 {'result': 99, 'error': None})

    def test_plus(self):
        p = Parser(debug=True)
        ret = p.parse('1 + 1')
        self.assertEqual(ret['result'], 2)
        self.assertEqual(ret['error'], None)
        ret = p.parse('1 + "lele"')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#VALUE!')
        ret = p.parse('1 + "2"')
        self.assertEqual(ret['result'], 3)
        self.assertEqual(ret['error'], None)

    def test_minus(self):
        p = Parser(debug=True)
        ret = p.parse('1 - 1')
        self.assertEqual(ret['result'], 0)
        self.assertEqual(ret['error'], None)
        ret = p.parse('1 - "lele"')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#VALUE!')

    def test_mult(self):
        p = Parser(debug=True)
        ret = p.parse('4*2')
        self.assertEqual(ret['result'], 8)
        self.assertEqual(ret['error'], None)
        ret = p.parse('4*"lele"')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#VALUE!')

    def test_div(self):
        p = Parser(debug=True)
        ret = p.parse('4/2')
        self.assertEqual(ret['result'], 2)
        self.assertEqual(ret['error'], None)
        ret = p.parse('5/2')
        self.assertEqual(ret['result'], 2.5)
        self.assertEqual(ret['error'], None)
        ret = p.parse('4/"lele"')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#VALUE!')
        ret = p.parse('5/0')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')

    def test_time_logic(self):
        p = Parser(debug=True)
        # Numbers
        ret = p.parse('TIME(22,0,0) = TIME(23,0,0)')
        self.assertEqual(ret['result'], False)  # 0
        self.assertEqual(ret['error'], None)
        ret = p.parse('TIME(22,0,0) <> TIME(23,0,0)')
        self.assertEqual(ret['result'], True)
        self.assertEqual(ret['error'], None)
        ret = p.parse('TIME(22,0,0) > TIME(23,0,0)')
        self.assertEqual(ret['result'], False)
        self.assertEqual(ret['error'], None)
        ret = p.parse('TIME(22,0,0) < TIME(23,0,0)')
        self.assertEqual(ret['result'], True)
        self.assertEqual(ret['error'], None)
        ret = p.parse('HOUR(TIME(22,15,30))')
        self.assertEqual(ret['result'], 22)
        self.assertEqual(ret['error'], None)
        ret = p.parse('MINUTE(TIME(22,15,30))')
        self.assertEqual(ret['result'], 15)
        self.assertEqual(ret['error'], None)
        ret = p.parse('SECOND(TIME(22,15,30))')
        self.assertEqual(ret['result'], 30)
        self.assertEqual(ret['error'], None)
        ret = p.parse('TIMEVALUE("12:00")')
        self.assertEqual(ret['result'], 0.5)
        self.assertEqual(ret['error'], None)


    def test_comparisons_preserve_error_codes(self):
        p = Parser()
        for source_error in (error.DIV_ZERO, error.NOT_AVAILABLE):
            p.set_function('ERR', lambda value=source_error: value)
            for op in ('=', '<>', '<', '>', '<=', '>='):
                for left, right in (('ERR()', '0'), ('0', 'ERR()'),
                                    ('ERR()', 'ERR()')):
                    expression = left + op + right
                    with self.subTest(expression=expression, error=str(source_error)):
                        self.assertEqual(p.parse(expression),
                                         {'result': None, 'error': str(source_error)})

    def test_comparison_errors_reach_handlers(self):
        p = Parser()
        p.set_function('ERR', lambda: error.DIV_ZERO)
        for op in ('=', '<>', '<', '>', '<=', '>='):
            for left, right in (('ERR()', '0'), ('0', 'ERR()')):
                expression = 'IFERROR(' + left + op + right + ',99)'
                with self.subTest(expression=expression):
                    self.assertEqual(p.parse(expression),
                                     {'result': 99, 'error': None})
            expression = 'IFNA(NA()' + op + '0,77)'
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression),
                                 {'result': 77, 'error': None})

    def test_comparisons_follow_arithmetic_left_error_policy(self):
        p = Parser()
        p.set_function('ERR', lambda: error.DIV_ZERO)
        for op in ('=', '<>', '<', '>', '<=', '>='):
            for left, right, code in (('ERR()', 'NA()', '#DIV/0!'),
                                      ('NA()', 'ERR()', '#N/A')):
                expression = left + op + right
                with self.subTest(expression=expression):
                    self.assertEqual(p.parse(expression),
                                     {'result': None, 'error': code})

    def test_logic(self):
        p = Parser(debug=True)
        # Numbers
        ret = p.parse('3 = 2')
        self.assertEqual(ret['result'], False)
        self.assertEqual(ret['error'], None)
        ret = p.parse('4 <> 2')
        self.assertEqual(ret['result'], True)
        self.assertEqual(ret['error'], None)
        ret = p.parse('3 > 2')
        self.assertEqual(ret['result'], True)
        self.assertEqual(ret['error'], None)
        ret = p.parse('2 < 3')
        self.assertEqual(ret['result'], True)
        self.assertEqual(ret['error'], None)
        ret = p.parse('3 >= 2')
        self.assertEqual(ret['result'], True)
        self.assertEqual(ret['error'], None)
        ret = p.parse('3 <= 2')
        self.assertEqual(ret['result'], False)
        self.assertEqual(ret['error'], None)
        ret = p.parse('3 < .4')
        self.assertEqual(ret['result'], False)
        self.assertEqual(ret['error'], None)
        ret = p.parse('3 < 0.4')
        self.assertEqual(ret['result'], False)
        self.assertEqual(ret['error'], None)
        ret = p.parse('3 > .4')
        self.assertEqual(ret['result'], True)
        self.assertEqual(ret['error'], None)
        ret = p.parse('3 > 0.4')
        self.assertEqual(ret['result'], True)
        self.assertEqual(ret['error'], None)
        ret = p.parse('3 >= 0.4')
        self.assertEqual(ret['result'], True)
        self.assertEqual(ret['error'], None)
        ret = p.parse('3 <= 0.4')
        self.assertEqual(ret['result'], False)
        self.assertEqual(ret['error'], None)
        # Strings
        ret = p.parse('"3" = "2"')
        self.assertEqual(ret['result'], False)
        self.assertEqual(ret['error'], None)
        ret = p.parse('"4" <> "2"')
        self.assertEqual(ret['result'], True)
        self.assertEqual(ret['error'], None)
        ret = p.parse('"3" > "2"')
        self.assertEqual(ret['result'], True)
        self.assertEqual(ret['error'], None)
        ret = p.parse('"2" < "3"')
        self.assertEqual(ret['result'], True)
        self.assertEqual(ret['error'], None)
        ret = p.parse('"3" >= "2"')
        self.assertEqual(ret['result'], True)
        self.assertEqual(ret['error'], None)
        ret = p.parse('"3" <= "2"')
        self.assertEqual(ret['result'], False)
        self.assertEqual(ret['error'], None)
        ret = p.parse('""=0')
        self.assertEqual(ret['result'], False)
        self.assertEqual(ret['error'], None)
        # booleans are bigger than strings
        ret = p.parse('FALSE>"true"')
        self.assertEqual(ret['result'], True)
        self.assertEqual(ret['error'], None)
        ret = p.parse('TRUE>"true"')
        self.assertEqual(ret['result'], True)
        self.assertEqual(ret['error'], None)
        ret = p.parse('FALSE<"true"')
        self.assertEqual(ret['result'], False)
        self.assertEqual(ret['error'], None)
        ret = p.parse('TRUE<"true"')
        self.assertEqual(ret['result'], False)
        self.assertEqual(ret['error'], None)
        ret = p.parse('"true"<TRUE')
        self.assertEqual(ret['result'], True)
        self.assertEqual(ret['error'], None)
        ret = p.parse('"true"<FALSE')
        self.assertEqual(ret['result'], True)
        self.assertEqual(ret['error'], None)
        ret = p.parse('"true">TRUE')
        self.assertEqual(ret['result'], False)
        self.assertEqual(ret['error'], None)
        ret = p.parse('"true">FALSE')
        self.assertEqual(ret['result'], False)
        self.assertEqual(ret['error'], None)
        # strings are bigger than numbers
        ret = p.parse('"a" > 2')
        self.assertEqual(ret['result'], True)
        self.assertEqual(ret['error'], None)
        ret = p.parse('"a" < 2')
        self.assertEqual(ret['result'], False)
        self.assertEqual(ret['error'], None)
        ret = p.parse('"2">2')
        self.assertEqual(ret['result'], True)
        self.assertEqual(ret['error'], None)
        ret = p.parse('2<"2"')
        self.assertEqual(ret['result'], True)
        self.assertEqual(ret['error'], None)
        ret = p.parse('2>"2"')
        self.assertEqual(ret['result'], False)
        self.assertEqual(ret['error'], None)
        # strings are bigger than dates
        ret = p.parse('"a">DATE(2019,11,20)')
        self.assertEqual(ret['result'], True)
        self.assertEqual(ret['error'], None)
        ret = p.parse('"1"<DATE(2019,11,20)')
        self.assertEqual(ret['result'], False)
        self.assertEqual(ret['error'], None)
        ret = p.parse('"1"<DATE(2019,11,20)')
        self.assertEqual(ret['result'], False)
        self.assertEqual(ret['error'], None)
        # Blanks are considered 0 with numbers
        ret = p.parse('0=B3')
        self.assertEqual(ret['result'], True)
        self.assertEqual(ret['error'], None)
        ret = p.parse('1>B3')
        self.assertEqual(ret['result'], True)
        self.assertEqual(ret['error'], None)
        ret = p.parse('-1<B3')
        self.assertEqual(ret['result'], True)
        self.assertEqual(ret['error'], None)
        # Blanks are considered epoch with dates
        ret = p.parse('DATE(1900, 1, 1)=B3')
        self.assertEqual(ret['result'], True)
        self.assertEqual(ret['error'], None)
        ret = p.parse('DATE(2019,11,27)>B3')
        self.assertEqual(ret['result'], True)
        self.assertEqual(ret['error'], None)
        ret = p.parse('DATE(1800,11,20)<B3')
        self.assertEqual(ret['result'], False)  # Because it will think you're in year 3700
        self.assertEqual(ret['error'], None)
        # Blanks equal Blanks
        ret = p.parse('B4=B3')
        self.assertEqual(ret['result'], True)
        self.assertEqual(ret['error'], None)
        ret = p.parse('B4>B3')
        self.assertEqual(ret['result'], False)
        self.assertEqual(ret['error'], None)
        ret = p.parse('B4<B3')
        self.assertEqual(ret['result'], False)
        self.assertEqual(ret['error'], None)
        ret = p.parse('B3>1')
        self.assertEqual(ret['result'], False)
        self.assertEqual(ret['error'], None)
        ret = p.parse('B3<1')
        self.assertEqual(ret['result'], True)
        self.assertEqual(ret['error'], None)
        ret = p.parse('B3>""')
        self.assertEqual(ret['result'], False)
        self.assertEqual(ret['error'], None)
        ret = p.parse('B3>DATE(2000; 1; 2)')
        self.assertEqual(ret['result'], False)
        self.assertEqual(ret['error'], None)
        ret = p.parse('B3>TRUE')
        self.assertEqual(ret['result'], False)
        self.assertEqual(ret['error'], None)
        ret = p.parse('B3>FALSE')
        self.assertEqual(ret['result'], False)
        self.assertEqual(ret['error'], None)
        ret = p.parse('B3<TRUE')
        self.assertEqual(ret['result'], True)
        self.assertEqual(ret['error'], None)
        ret = p.parse('B3<FALSE')
        self.assertEqual(ret['result'], False)
        self.assertEqual(ret['error'], None)

    def test_implicit_conversions_number(self):
        # Cell references will be blanks in this test
        # since we don't teach the parser how to get cells
        p = Parser(debug=True)
        # Number plus number
        ret = p.parse('2 + 2')
        self.assertEqual(ret['result'], 4)
        self.assertEqual(ret['error'], None)
        # Number plus stupid string
        ret = p.parse('2 + "2"')
        self.assertEqual(ret['result'], 4)
        self.assertEqual(ret['error'], None)
        # Number plus date
        ret = p.parse('2 + DATE(2019,11,20)')
        self.assertEqual(ret['result'], datetime.datetime(2019, 11, 22))
        self.assertEqual(ret['error'], None)
        # Number plus bool
        ret = p.parse('2 + TRUE')
        self.assertEqual(ret['result'], 3)
        self.assertEqual(ret['error'], None)
        ret = p.parse('2 + FALSE')
        self.assertEqual(ret['result'], 2)
        self.assertEqual(ret['error'], None)
        # Number plus blank
        ret = p.parse('2 + B3')
        self.assertEqual(ret['result'], 2)
        self.assertEqual(ret['error'], None)
        # Number minus date
        ret = p.parse('2 - DATE(2019,11,20)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#NUM!')
        # Number minus number
        ret = p.parse('2 - 2')
        self.assertEqual(ret['result'], 0)
        self.assertEqual(ret['error'], None)
        # Number minus bool
        ret = p.parse('2 - TRUE')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)
        ret = p.parse('2 - FALSE')
        self.assertEqual(ret['result'], 2)
        self.assertEqual(ret['error'], None)
        # Number minus blank
        ret = p.parse('2 - B3')
        self.assertEqual(ret['result'], 2)
        self.assertEqual(ret['error'], None)
        # Number times date
        ret = p.parse('2 * DATE(2019,11,20)')
        self.assertEqual(ret['result'], datetime.datetime(2139, 10, 11))
        self.assertEqual(ret['error'], None)
        # Number times number
        ret = p.parse('2 * 3.5')
        self.assertEqual(ret['result'], 7)
        self.assertEqual(ret['error'], None)
        # Number times bool
        ret = p.parse('2 * TRUE')
        self.assertEqual(ret['result'], 2)
        self.assertEqual(ret['error'], None)
        ret = p.parse('2 * FALSE')
        self.assertEqual(ret['result'], 0)
        self.assertEqual(ret['error'], None)
        # Number times blank
        ret = p.parse('2 * B3')
        self.assertEqual(ret['result'], 0)
        self.assertEqual(ret['error'], None)
        # Number divided by date
        ret = p.parse('200000000 / DATE(2019,11,20)')
        self.assertEqual(ret['result'], datetime.datetime(1912, 7, 2, 8, 34, 13, 337596))
        self.assertEqual(ret['error'], None)
        # Number divided by number
        ret = p.parse('2 / 4')
        self.assertEqual(ret['result'], 0.5)
        self.assertEqual(ret['error'], None)
        # Number divided by bool
        ret = p.parse('2 / TRUE')
        self.assertEqual(ret['result'], 2)
        self.assertEqual(ret['error'], None)
        ret = p.parse('2 / FALSE')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')
        # Number divided by blank
        ret = p.parse('2 / B3')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')

    def test_implicit_conversions_date(self):
        # Cell references will be blanks in this test
        # since we don't teach the parser how to get cells
        p = Parser(debug=True)
        # Date plus date
        ret = p.parse('DATE(2019,11,20) + DATE(2019,11,20)')
        self.assertEqual(ret['result'], 87578)
        self.assertEqual(ret['error'], None)
        # Date plus stupid string
        ret = p.parse('DATE(2019,11,20) + "2"')
        self.assertEqual(ret['result'], datetime.datetime(2019, 11, 22))
        self.assertEqual(ret['error'], None)
        ret = p.parse('DATE(1900; 11; 1) + "14/10/1900"')
        # In the resulf of this one you would need to
        # use parse_date on the result to get excels result of 16/08/1901
        # for now we're keeping it coherent with adding dates
        # which gives you the serialized value
        self.assertEqual(ret['result'], 594)
        self.assertEqual(ret['error'], None)
        # Date plus number
        ret = p.parse('DATE(2019,11,20) + 2')
        self.assertEqual(ret['result'], datetime.datetime(2019, 11, 22))
        self.assertEqual(ret['error'], None)
        # Date plus bool
        ret = p.parse('DATE(2019,11,20) + TRUE')
        self.assertEqual(ret['result'], datetime.datetime(2019, 11, 21))
        self.assertEqual(ret['error'], None)
        ret = p.parse('DATE(2019,11,20) + FALSE')
        self.assertEqual(ret['result'], datetime.datetime(2019, 11, 20))
        self.assertEqual(ret['error'], None)
        # Date plus blank
        ret = p.parse('DATE(2019,11,20) + B3')
        self.assertEqual(ret['result'], datetime.datetime(2019, 11, 20))
        self.assertEqual(ret['error'], None)
        # Date minus date
        ret = p.parse('DATE(2019,11,20) - DATE(2019,11,20)')
        self.assertEqual(ret['result'], 0)
        self.assertEqual(ret['error'], None)
        # Date minus number
        ret = p.parse('DATE(2019,11,20) - 2')
        self.assertEqual(ret['result'], datetime.datetime(2019, 11, 18))
        self.assertEqual(ret['error'], None)
        # Date minus bool
        ret = p.parse('DATE(2019,11,20) - TRUE')
        self.assertEqual(ret['result'], datetime.datetime(2019, 11, 19))
        self.assertEqual(ret['error'], None)
        ret = p.parse('DATE(2019,11,20) - FALSE')
        self.assertEqual(ret['result'], datetime.datetime(2019, 11, 20))
        self.assertEqual(ret['error'], None)
        # Date minus blank
        ret = p.parse('DATE(2019,11,20) - B3')
        self.assertEqual(ret['result'], datetime.datetime(2019, 11, 20))
        self.assertEqual(ret['error'], None)
        # Date times date
        ret = p.parse('DATE(2019,11,20) * DATE(2019,11,20)')
        self.assertEqual(ret['result'], 1917476521)
        self.assertEqual(ret['error'], None)
        # Date times number
        ret = p.parse('DATE(2019,11,20) * 2')
        self.assertEqual(ret['result'], datetime.datetime(2139, 10, 11))
        self.assertEqual(ret['error'], None)
        # Date times bool
        ret = p.parse('DATE(2019,11,20) * TRUE')
        self.assertEqual(ret['result'], datetime.datetime(2019, 11, 20))
        self.assertEqual(ret['error'], None)
        ret = p.parse('DATE(2019,11,20) * FALSE')
        self.assertEqual(ret['result'], datetime.datetime(1900, 1, 1))
        self.assertEqual(ret['error'], None)
        # Date times blank
        ret = p.parse('DATE(2019,11,20) * B3')
        self.assertEqual(ret['result'], datetime.datetime(1900, 1, 1))  # excel actualy return 1900/1/0 but that's no good in python
        self.assertEqual(ret['error'], None)
        # Date divided by date
        ret = p.parse('DATE(2019,11,20) / DATE(2019,11,20)')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)
        # Date divided by number
        ret = p.parse('DATE(2019,11,20) / 2')
        self.assertEqual(ret['result'], datetime.datetime(1959, 12, 10, 12, 0))
        self.assertEqual(ret['error'], None)
        # Date divided by bool
        ret = p.parse('DATE(2019,11,20) / TRUE')
        self.assertEqual(ret['result'], datetime.datetime(2019, 11, 20))
        self.assertEqual(ret['error'], None)
        ret = p.parse('DATE(2019,11,20) / FALSE')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')
        # Date divided by blank
        ret = p.parse('DATE(2019,11,20) / B3')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')

    def test_implicit_conversions_raw_date(self):
        # A plain datetime.date (not just datetime.datetime, e.g. what a
        # consumer might store in a variable/cell) must behave exactly like
        # the equivalent DATE(...) result in arithmetic and comparisons.
        p = Parser(debug=True)
        p.set_variable('startdate', datetime.date(2019, 11, 20))
        p.set_variable('enddate', datetime.date(2019, 11, 22))
        self.assertEqual(p.parse('startdate + 2'), p.parse('DATE(2019,11,20) + 2'))
        self.assertEqual(p.parse('enddate - startdate'), p.parse('DATE(2019,11,22) - DATE(2019,11,20)'))
        self.assertEqual(p.parse('startdate * 2'), p.parse('DATE(2019,11,20) * 2'))
        self.assertEqual(p.parse('startdate / 2'), p.parse('DATE(2019,11,20) / 2'))
        # Comparisons between two raw dates
        self.assertEqual(p.parse('startdate < enddate'), {'result': True, 'error': None})
        self.assertEqual(p.parse('startdate = startdate'), {'result': True, 'error': None})
        self.assertEqual(p.parse('startdate > enddate'), {'result': False, 'error': None})
        # Mixed datetime.date / datetime.datetime (DATE(...)) operands
        self.assertEqual(p.parse('startdate + DATE(2019,11,22)'), p.parse('DATE(2019,11,20) + DATE(2019,11,22)'))
        self.assertEqual(p.parse('startdate < DATE(2019,11,22)'), p.parse('DATE(2019,11,20) < DATE(2019,11,22)'))
        # Blank still compares to a raw date the same way it does to DATE(...)
        self.assertEqual(p.parse('startdate > B3'), p.parse('DATE(2019,11,20) > B3'))

    def test_implicit_conversions_bool(self):
        # Cell references will be blanks in this test
        # since we don't teach the parser how to get cells
        p = Parser(debug=True)
        # Bool plus date
        ret = p.parse('TRUE + DATE(2019;11;20)')
        self.assertEqual(ret['result'], datetime.datetime(2019, 11, 21))
        self.assertEqual(ret['error'], None)
        ret = p.parse('FALSE + DATE(2019;11;20)')
        self.assertEqual(ret['result'], datetime.datetime(2019, 11, 20))
        self.assertEqual(ret['error'], None)
        # Bool plus number
        ret = p.parse('TRUE + 1')
        self.assertEqual(ret['result'], 2)
        self.assertEqual(ret['error'], None)
        ret = p.parse('FALSE + 1')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)
        # Bool plus bool
        ret = p.parse('TRUE + TRUE')
        self.assertEqual(ret['result'], 2)
        self.assertEqual(ret['error'], None)
        ret = p.parse('TRUE + FALSE')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)
        ret = p.parse('FALSE + FALSE')
        self.assertEqual(ret['result'], 0)
        self.assertEqual(ret['error'], None)
        # Bool plus Blank
        ret = p.parse('TRUE + B4')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)
        ret = p.parse('FALSE + B4')
        self.assertEqual(ret['result'], 0)
        self.assertEqual(ret['error'], None)
        # Bool minus date
        ret = p.parse('TRUE - DATE(2019;11;20)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#NUM!')
        # Bool minus number
        ret = p.parse('TRUE - 1')
        self.assertEqual(ret['result'], 0)
        self.assertEqual(ret['error'], None)
        ret = p.parse('FALSE - 1')
        self.assertEqual(ret['result'], -1)
        self.assertEqual(ret['error'], None)
        # Bool minus bool
        ret = p.parse('TRUE - TRUE')
        self.assertEqual(ret['result'], 0)
        self.assertEqual(ret['error'], None)
        ret = p.parse('TRUE - FALSE')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)
        ret = p.parse('FALSE - FALSE')
        self.assertEqual(ret['result'], 0)
        self.assertEqual(ret['error'], None)
        ret = p.parse('FALSE - TRUE')
        self.assertEqual(ret['result'], -1)
        self.assertEqual(ret['error'], None)
        # Bool minus Blank
        ret = p.parse('TRUE - B4')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)
        ret = p.parse('FALSE - B4')
        self.assertEqual(ret['result'], 0)
        self.assertEqual(ret['error'], None)
        # Bool times date
        ret = p.parse('TRUE * DATE(2019;11;20)')
        self.assertEqual(ret['result'], datetime.datetime(2019, 11, 20))
        self.assertEqual(ret['error'], None)
        # Bool times number
        ret = p.parse('TRUE * 2')
        self.assertEqual(ret['result'], 2)
        self.assertEqual(ret['error'], None)
        ret = p.parse('FALSE * 2')
        self.assertEqual(ret['result'], 0)
        self.assertEqual(ret['error'], None)
        # Bool times bool
        ret = p.parse('TRUE * TRUE')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)
        ret = p.parse('TRUE * FALSE')
        self.assertEqual(ret['result'], 0)
        self.assertEqual(ret['error'], None)
        ret = p.parse('FALSE * FALSE')
        self.assertEqual(ret['result'], 0)
        self.assertEqual(ret['error'], None)
        ret = p.parse('FALSE * TRUE')
        self.assertEqual(ret['result'], 0)
        self.assertEqual(ret['error'], None)
        # Bool times Blank
        ret = p.parse('TRUE * B4')
        self.assertEqual(ret['result'], 0)
        self.assertEqual(ret['error'], None)
        ret = p.parse('FALSE * B4')
        self.assertEqual(ret['result'], 0)
        self.assertEqual(ret['error'], None)
        # Bool divided by date
        ret = p.parse('TRUE / DATE(2019;11;20)')
        self.assertEqual(ret['result'], datetime.datetime(1900, 1, 1))
        self.assertEqual(ret['error'], None)
        # Bool divided by number
        ret = p.parse('TRUE / 2')
        self.assertEqual(ret['result'], 0.5)
        self.assertEqual(ret['error'], None)
        ret = p.parse('FALSE / 2')
        self.assertEqual(ret['result'], 0)
        self.assertEqual(ret['error'], None)
        # Bool divided by bool
        ret = p.parse('TRUE / TRUE')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)
        ret = p.parse('TRUE / FALSE')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')
        ret = p.parse('FALSE / FALSE')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')
        ret = p.parse('FALSE / TRUE')
        self.assertEqual(ret['result'], 0)
        self.assertEqual(ret['error'], None)
        # Bool divided by Blank
        ret = p.parse('TRUE / B4')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')
        ret = p.parse('FALSE / B4')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')

    def test_implicit_conversions_blank(self):
        # Cell references will be blanks in this test
        # since we don't teach the parser how to get cells
        p = Parser(debug=True)
        # Blank plus date
        ret = p.parse('B3 + DATE(2019;11;20)')
        self.assertEqual(ret['result'], datetime.datetime(2019, 11, 20))
        self.assertEqual(ret['error'], None)
        # Blank plus number
        ret = p.parse('B3 + 1')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)
        # Blank plus bool
        ret = p.parse('B3 + TRUE')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)
        ret = p.parse('B3 + FALSE')
        self.assertEqual(ret['result'], 0)
        self.assertEqual(ret['error'], None)
        # Blank plus Blank
        ret = p.parse('B3 + B4')
        self.assertEqual(ret['result'], 0)
        self.assertEqual(ret['error'], None)
        # Blank minus date
        ret = p.parse('B3 - DATE(2019;11;20)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#NUM!')
        # Blank minus number
        ret = p.parse('B3 - 1')
        self.assertEqual(ret['result'], -1)
        self.assertEqual(ret['error'], None)
        # Blank minus bool
        ret = p.parse('B3 - TRUE')
        self.assertEqual(ret['result'], -1)
        self.assertEqual(ret['error'], None)
        ret = p.parse('B3 - FALSE')
        self.assertEqual(ret['result'], 0)
        self.assertEqual(ret['error'], None)
        # Blank minus Blank
        ret = p.parse('B3 - B4')
        self.assertEqual(ret['result'], 0)
        self.assertEqual(ret['error'], None)
        # Blank times date
        ret = p.parse('B3 * DATE(2019;11;20)')
        self.assertEqual(ret['result'], datetime.datetime(1900, 1, 1))  # excel actualy return 1900/1/0 but that's no good in python
        self.assertEqual(ret['error'], None)
        # Blank times number
        ret = p.parse('B3 * 1')
        self.assertEqual(ret['result'], 0)
        self.assertEqual(ret['error'], None)
        # Blank times bool
        ret = p.parse('B3 * TRUE')
        self.assertEqual(ret['result'], 0)
        self.assertEqual(ret['error'], None)
        ret = p.parse('B3 * FALSE')
        self.assertEqual(ret['result'], 0)
        self.assertEqual(ret['error'], None)
        # Blank times Blank
        ret = p.parse('B3 * B4')
        self.assertEqual(ret['result'], 0)
        self.assertEqual(ret['error'], None)
        # Blank divided by date
        ret = p.parse('B3 / DATE(2019;11;20)')
        self.assertEqual(ret['result'], 0)  # excel actualy return 1900/1/0 but that's no good in python
        self.assertEqual(ret['error'], None)
        # Blank divided by number
        ret = p.parse('B3 / 2')
        self.assertEqual(ret['result'], 0)
        self.assertEqual(ret['error'], None)
        # Blank divided by bool
        ret = p.parse('B3 / TRUE')
        self.assertEqual(ret['result'], 0)
        self.assertEqual(ret['error'], None)
        ret = p.parse('B3 / FALSE')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')
        # Blank divided by Blank
        ret = p.parse('B3 / B4')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')

    def test_arithmetic_combines_single_row_arrays_elementwise(self):
        p = Parser()
        p.set_function('LEFTROW', lambda: [[2, 4, 8]])
        p.set_function('RIGHTROW', lambda: [[1, 2, 4]])
        for op, expected in [('+', [[3, 6, 12]]), ('-', [[1, 2, 4]]),
                             ('*', [[2, 8, 32]]), ('/', [[2, 2, 2]])]:
            with self.subTest(op=op):
                self.assertEqual(p.parse('LEFTROW()' + op + 'RIGHTROW()'),
                                 {'result': expected, 'error': None})
        self.assertEqual(p.parse('SUM(LEFTROW()*RIGHTROW())'),
                         {'result': 42, 'error': None})

    def test_array_adaptation_preserves_existing_shapes_and_broadcasting(self):
        p = Parser()
        for left, right, expected in [
            ([2, 4, 8], [1], [3, 5, 9]),
            ([[2], [4], [8]], [[1], [2], [4]], [[3], [6], [12]]),
            ([[2, 4], [6, 8]], [[1, 2], [3, 4]], [[3, 6], [9, 12]]),
            ([[2]], [[1]], [[3]]),
            ([], [1], []),
        ]:
            with self.subTest(left=left, right=right):
                p.set_function('LEFTARRAY', lambda: left)
                p.set_function('RIGHTARRAY', lambda: right)
                self.assertEqual(p.parse('LEFTARRAY()+RIGHTARRAY()'),
                                 {'result': expected, 'error': None})
        p.set_function('DATA', lambda: [[2, 4, 8]])
        for expression, expected in [
            ('DATA()+1', [[3, 5, 9]]), ('1+DATA()', [[3, 5, 9]]),
            ('DATA()-1', [[1, 3, 7]]), ('1-DATA()', [[-1, -3, -7]]),
            ('DATA()/2', [[1, 2, 4]]), ('16/DATA()', [[8, 4, 2]]),
        ]:
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression),
                                 {'result': expected, 'error': None})

    def test_row_array_arithmetic_keeps_errors_in_their_cells(self):
        p = Parser()
        p.set_function('LEFTROW', lambda: [[2, error.DIV_ZERO, 8]])
        p.set_function('RIGHTROW', lambda: [[1, 2, 0]])
        self.assertEqual(p.parse('LEFTROW()/RIGHTROW()'),
                         {'result': [[2, error.DIV_ZERO, error.DIV_ZERO]],
                          'error': None})
        self.assertEqual(p.parse('IFERROR(LEFTROW()/RIGHTROW(),0)'),
                         {'result': [[2, 0, 0]], 'error': None})

    def test_arrays(self):
        p = Parser(debug=True)
        ret = p.parse('2/{1;2;4}')
        self.assertEqual(ret['result'], [2, 1, 0.5])
        self.assertEqual(ret['error'], None)
        ret = p.parse('{1;2;4}/2')
        self.assertEqual(ret['result'], [0.5, 1, 2])
        self.assertEqual(ret['error'], None)
        ret = p.parse('{1;2;4}*2')
        self.assertEqual(ret['result'], [2, 4, 8])
        self.assertEqual(ret['error'], None)
        ret = p.parse('2*{1;2;4}')
        self.assertEqual(ret['result'], [2, 4, 8])
        self.assertEqual(ret['error'], None)
        ret = p.parse('2+{1;2;4}')
        self.assertEqual(ret['result'], [3, 4, 6])
        self.assertEqual(ret['error'], None)
        ret = p.parse('{1;2;4}+2')
        self.assertEqual(ret['result'], [3, 4, 6])
        self.assertEqual(ret['error'], None)
        ret = p.parse('2-{1;2;4}')
        self.assertEqual(ret['result'], [1, 0, -2])
        self.assertEqual(ret['error'], None)
        ret = p.parse('{1;2;4}-2')
        self.assertEqual(ret['result'], [-1, 0, 2])
        self.assertEqual(ret['error'], None)

    def test_implicit_conversions_errors(self):
        p = Parser(debug=True)
        ret = p.parse('1/0 + 1')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')
        ret = p.parse('1 + 1/0')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')
        ret = p.parse('1 + "lele"')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#VALUE!')
        ret = p.parse('"lele"+1')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#VALUE!')

    def test_errors(self):
        p = Parser(debug=False)
        ret = p.parse('#REF! + #N/A')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#REF!')

    def test_amp(self):
        p = Parser(debug=True)
        for expression, expected in [
            ('1&2', '12'),
            ('"prefix"&7', 'prefix7'),
            ('""&"suffix"', 'suffix'),
            ('"#DIV/0!"&"suffix"', '#DIV/0!suffix'),
        ]:
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression),
                                 {'result': expected, 'error': None})

    def test_concatenation_preserves_errors_for_enclosing_handlers(self):
        p = Parser()
        for source_error in (error.DIV_ZERO, error.NOT_AVAILABLE, error.NUM):
            p.set_function('ERR', lambda value=source_error: value)
            expressions = ('ERR()&"suffix"', '"prefix"&ERR()', 'ERR()&ERR()',
                           str(source_error) + '&"suffix"')
            for expression in expressions:
                with self.subTest(error=str(source_error), expression=expression):
                    self.assertEqual(p.parse(expression),
                                     {'result': None, 'error': str(source_error)})
                    self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                     {'result': 99, 'error': None})
                    expected = ({'result': 77, 'error': None}
                                if source_error is error.NOT_AVAILABLE
                                else {'result': None, 'error': str(source_error)})
                    self.assertEqual(p.parse('IFNA(' + expression + ',77)'), expected)
        self.assertEqual(p.parse('IFERROR((1/0)&"suffix",99)'),
                         {'result': 99, 'error': None})

    def test_concatenation_preserves_the_left_error_when_both_sides_fail(self):
        p = Parser()
        for expression, code in [('#REF!&#N/A', '#REF!'),
                                 ('#N/A&#REF!', '#N/A')]:
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression),
                                 {'result': None, 'error': code})
