# -*- coding: utf-8 -*-
import unittest
import datetime
from hotxlfp import Parser
from hotxlfp.formulas import error


class TestOperators(unittest.TestCase):

    def test_unary_plus_preserves_operand_values_and_types(self):
        p = Parser()
        for expression, expected in (
            ('+1', 1), ('+1.5', 1.5), ('+"1"', '1'),
            ('+"text"', 'text'), ('+""', ''),
            ('+TRUE()', True), ('+FALSE()', False), ('+NULL', None),
            ('ISTEXT(+"1")', True), ('ISNUMBER(+"1")', False),
            ('ISLOGICAL(+TRUE())', True), ('ISBLANK(+NULL)', True),
            ('IFERROR(+"text",99)', 'text'),
            ('IFERROR(+NULL,99)', None),
            ('+{1,"2";TRUE(),NULL}', [[1, '2'], [True, None]]),
        ):
            with self.subTest(expression=expression):
                result = p.parse(expression)
                self.assertEqual(result, {'result': expected, 'error': None})
                self.assertIs(type(result['result']), type(expected))
        for value in ([1, '2', True, None], (1, '2', True, None),
                      datetime.date(2025, 1, 1), datetime.datetime(2025, 1, 1, 12)):
            p.set_function('DATA', lambda value=value: value)
            with self.subTest(value=value):
                result = p.parse('+DATA()')
                self.assertEqual(result, {'result': value, 'error': None})
                self.assertIs(type(result['result']), type(value))

    def test_unary_plus_precedence(self):
        p = Parser()
        for expression, expected in (
            ('+1&2', '12'), ('1&+2', '12'), ('+"1"&2', '12'),
            ('++1', 1), ('+-2', -2), ('-+2', -2),
            ('1++2', 3), ('1+-2', -1), ('2*+3', 6),
            ('+(1+2)*3', 9), ('+1%', 0.01), ('+1=1', True),
            ('SUM(+1,+2)', 3),
        ):
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': expected, 'error': None})

    def test_unary_plus_preserves_calculation_errors(self):
        p = Parser()
        for source_error in (error.DIV_ZERO, error.NOT_AVAILABLE, error.NUM):
            p.set_function('FAIL', lambda value=source_error: value)
            p.set_function('DATA', lambda value=source_error: [1, value])
            for source in (str(source_error), 'FAIL()', 'SUM(DATA())'):
                expression = '+' + source
                with self.subTest(expression=expression, error=str(source_error)):
                    self.assertEqual(p.parse(expression),
                                     {'result': None, 'error': str(source_error)})
                    self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                     {'result': 99, 'error': None})
                    expected = ({'result': 77, 'error': None}
                                if source_error is error.NOT_AVAILABLE
                                else {'result': None, 'error': str(source_error)})
                    self.assertEqual(p.parse('IFNA(' + expression + ',77)'), expected)

    def test_number_minus_date_returns_a_numeric_difference(self):
        p = Parser()
        day = datetime.datetime(2025, 1, 1)
        p.set_function('D', lambda: day)
        p.set_function('NOON', lambda: datetime.datetime(2025, 1, 1, 12))
        p.set_function('DATEONLY', lambda: datetime.date(2025, 1, 1))
        p.set_function('BLANK', lambda: None)
        for expression, expected in (
            ('NULL-D()', -45658), ('BLANK()-D()', -45658),
            ('0-D()', -45658), ('1-D()', -45657), ('-1-D()', -45659),
            ('45658-D()', 0), ('45659-D()', 1),
            ('45658.5-D()', 0.5), ('0-NOON()', -45658.5),
            ('0-DATEONLY()', -45658), ('"45658"-D()', 0),
            ('TRUE()-D()', -45657), ('FALSE()-D()', -45658),
            ('IFERROR(NULL-D(),99)', -45658),
        ):
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': expected, 'error': None})
        self.assertEqual(day, datetime.datetime(2025, 1, 1))

    def test_numeric_date_subtraction_preserves_date_shifts_and_error_inputs(self):
        p = Parser()
        day = datetime.datetime(2025, 1, 1)
        noon = datetime.datetime(2025, 1, 1, 12)
        p.set_function('D', lambda: day)
        p.set_function('NOON', lambda: noon)
        p.set_function('FAIL', lambda: error.DIV_ZERO)
        for expression, expected in (
            ('D()-D()', 0), ('D()-NULL', day), ('D()-0', day),
            ('D()+NULL', day), ('NULL+D()', day),
            ('D()-1', datetime.datetime(2024, 12, 31)),
            ('D()+1', datetime.datetime(2025, 1, 2)),
            ('1+D()', datetime.datetime(2025, 1, 2)),
            ('D()+0.5', noon), ('NOON()-0.5', day),
            ('NOON()-D()', 0.5), ('D()-NOON()', -0.5), ('NULL-NULL', 0),
        ):
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': expected, 'error': None})
        for expression in ('D()-FAIL()', '0-FAIL()', 'FAIL()-D()'):
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': None, 'error': '#DIV/0!'})
                self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                 {'result': 99, 'error': None})
        for expression in ('D()-""', '""-D()'):
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': None, 'error': '#VALUE!'})

    def test_numeric_date_subtraction_handles_array_cells_in_both_orders(self):
        p = Parser()
        day = datetime.datetime(2025, 1, 1)
        noon = datetime.datetime(2025, 1, 1, 12)
        p.set_function('D', lambda: day)
        p.set_function('NOON', lambda: noon)
        p.set_function('FAIL', lambda: error.DIV_ZERO)
        for expression, expected in (
            ('{NULL,45659}-D()', [[-45658, 1]]),
            ('0-{D(),NOON()}', [[-45658, -45658.5]]),
            ('{NULL;1}-{D(),NOON()}', [[-45658, -45658.5], [-45657, -45657.5]]),
            ('{D(),NOON()}-NULL', [[day, noon]]),
            ('{D(),NOON()}-0.5', [[datetime.datetime(2024, 12, 31, 12), day]]),
            ('{D();NOON()}-{D(),NOON()}', [[0, -0.5], [0.5, 0]]),
            ('IFERROR({NULL,FAIL()}-D(),99)', [[-45658, 99]]),
            ('IFERROR(0-{D(),FAIL()},99)', [[-45658, 99]]),
        ):
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': expected, 'error': None})

    def test_date_arithmetic_uses_correct_1900_serial_boundaries(self):
        p = Parser()
        for expression, expected in (
            ('DATE(1900,1,1)+1', datetime.datetime(1900, 1, 2)),
            ('DATE(1900,1,1)+0.5', datetime.datetime(1900, 1, 1, 12)),
            ('DATE(1900,3,1)+1', datetime.datetime(1900, 3, 2)),
            ('DATE(1900,3,1)-DATE(1900,2,28)', 2),
            ('DATE(1900,1,1)=1', True),
            ('DATE(1900,3,1)=61', True),
            ('DATE(1900,1,1)=NULL', False),
        ):
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': expected, 'error': None})

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
        # Blanks compare as zero; January 1, 1900 has serial 1.
        ret = p.parse('DATE(1900, 1, 1)=B3')
        self.assertEqual(ret['result'], False)
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
        self.assertEqual(ret['result'], -43787)
        self.assertEqual(ret['error'], None)
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
        self.assertEqual(ret['result'], datetime.datetime(1899, 12, 31))
        self.assertEqual(ret['error'], None)
        # Date times blank
        ret = p.parse('DATE(2019,11,20) * B3')
        self.assertEqual(ret['result'], datetime.datetime(1899, 12, 31))
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
        self.assertEqual(ret['result'], -43788)
        self.assertEqual(ret['error'], None)
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
        # 1 / 43789 of a day retains its fractional seconds on the placeholder.
        self.assertEqual(ret['result'], datetime.datetime(1899, 12, 31, 0, 0, 1, 973098))
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
        self.assertEqual(ret['result'], -43789)
        self.assertEqual(ret['error'], None)
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
        self.assertEqual(ret['result'], datetime.datetime(1899, 12, 31))
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

    def test_arithmetic_broadcasts_rows_and_columns_in_both_orders(self):
        p = Parser()
        p.set_function('ROW', lambda: [[2, 4]])
        p.set_function('COL', lambda: [[8], [16]])
        for expression, expected in (
            ('ROW()+COL()', [[10, 12], [18, 20]]),
            ('COL()+ROW()', [[10, 12], [18, 20]]),
            ('ROW()-COL()', [[-6, -4], [-14, -12]]),
            ('COL()-ROW()', [[6, 4], [14, 12]]),
            ('ROW()*COL()', [[16, 32], [32, 64]]),
            ('COL()*ROW()', [[16, 32], [32, 64]]),
            ('ROW()/COL()', [[0.25, 0.5], [0.125, 0.25]]),
            ('COL()/ROW()', [[4, 2], [8, 4]]),
        ):
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': expected, 'error': None})

    def test_arithmetic_broadcasts_vectors_over_matrices(self):
        p = Parser()
        p.set_function('MATRIX', lambda: [[1, 2], [3, 4]])
        for vector, forward, reverse in (
            ([[10, 20]], [[-9, -18], [-7, -16]], [[9, 18], [7, 16]]),
            ([[10], [20]], [[-9, -8], [-17, -16]], [[9, 8], [17, 16]]),
            ([[10]], [[-9, -8], [-7, -6]], [[9, 8], [7, 6]]),
        ):
            p.set_function('VECTOR', lambda: vector)
            for expression, expected in (('MATRIX()-VECTOR()', forward),
                                          ('VECTOR()-MATRIX()', reverse)):
                with self.subTest(vector=vector, expression=expression):
                    self.assertEqual(p.parse(expression), {'result': expected, 'error': None})

    def test_array_broadcasting_preserves_flat_columns_and_nested_shapes(self):
        p = Parser()
        for left, right, expected in (
            ([1], [2, 4, 8], [3, 5, 9]),
            ([1, 2], [[10, 20]], [[11, 21], [12, 22]]),
            ([[10, 20]], [1, 2], [[11, 21], [12, 22]]),
            ([1, 2], [[10], [20]], [[11], [22]]),
            (((1, 2),), ((10,), (20,)), [[11, 12], [21, 22]]),
            ((1, 2), 10, [11, 12]),
            ([], 1, []),
            ([1], [], []),
        ):
            p.set_function('LEFTARRAY', lambda: left)
            p.set_function('RIGHTARRAY', lambda: right)
            with self.subTest(left=left, right=right):
                self.assertEqual(p.parse('LEFTARRAY()+RIGHTARRAY()'),
                                 {'result': expected, 'error': None})

    def test_array_broadcasting_pads_unmatched_cells_with_na(self):
        p = Parser()
        for left, right, expected in (
            ([1, 2, 3], [10, 20], [11, 22, error.NOT_AVAILABLE]),
            ([[1, 2, 3]], [[10, 20]], [[11, 22, error.NOT_AVAILABLE]]),
            ([[1], [2], [3]], [[10], [20]], [[11], [22], [error.NOT_AVAILABLE]]),
            ([[1, 2], [3, 4]], [[10, 20], [30, 40], [50, 60]],
             [[11, 22], [33, 44], [error.NOT_AVAILABLE, error.NOT_AVAILABLE]]),
        ):
            p.set_function('LEFTARRAY', lambda: left)
            p.set_function('RIGHTARRAY', lambda: right)
            for expression in ('LEFTARRAY()+RIGHTARRAY()', 'RIGHTARRAY()+LEFTARRAY()'):
                with self.subTest(left=left, right=right, expression=expression):
                    self.assertEqual(p.parse(expression), {'result': expected, 'error': None})
                    fallback = ([99 if isinstance(value, error.XLError) else value for value in expected]
                                if not isinstance(expected[0], list) else
                                [[99 if isinstance(value, error.XLError) else value for value in row]
                                 for row in expected])
                    self.assertEqual(p.parse('IFNA(' + expression + ',99)'),
                                     {'result': fallback, 'error': None})

    def test_broadcast_arithmetic_preserves_cell_errors_and_numeric_validation(self):
        p = Parser()
        p.set_function('ROW', lambda: [[2, 4]])
        p.set_function('COL', lambda: [[2], [0]])
        self.assertEqual(p.parse('ROW()/COL()'),
                         {'result': [[1, 2], [error.DIV_ZERO, error.DIV_ZERO]], 'error': None})
        self.assertEqual(p.parse('IFERROR(ROW()/COL(),99)'),
                         {'result': [[1, 2], [99, 99]], 'error': None})
        p.set_function('ROW', lambda: [[1, error.DIV_ZERO]])
        p.set_function('COL', lambda: [[10], [20]])
        for expression in ('ROW()+COL()', 'COL()+ROW()'):
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression),
                                 {'result': [[11, error.DIV_ZERO], [21, error.DIV_ZERO]], 'error': None})
        p.set_function('ROW', lambda: [[1e308, 2]])
        p.set_function('COL', lambda: [[2], [3]])
        self.assertEqual(p.parse('ROW()*COL()'),
                         {'result': [[error.NUM, 4], [error.NUM, 6]], 'error': None})

    def test_array_broadcasting_uses_nested_range_callbacks(self):
        p = Parser()
        ranges = {'A1': [[1, 2]], 'C1': [[10], [20], [30]]}
        p.on('callRangeValue', lambda start, end, set_value: set_value(ranges[start.label]))
        for expression in ('A1:B1+C1:C3', 'C1:C3+A1:B1'):
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression),
                                 {'result': [[11, 12], [21, 22], [31, 32]], 'error': None})

    def test_array_broadcasting_rejects_malformed_arrays(self):
        p = Parser()
        for values in ([[1], [2, 3]], [1, [2]], [[[1]]], []):
            p.set_function('DATA', lambda: values)
            for expression in ('DATA()+{1;2}', '{1;2}+DATA()'):
                with self.subTest(values=values, expression=expression):
                    self.assertEqual(p.parse(expression), {'result': None, 'error': '#VALUE!'})

    def test_arrays(self):
        p = Parser(debug=True)
        ret = p.parse('2/{1;2;4}')
        self.assertEqual(ret['result'], [[2], [1], [0.5]])
        self.assertEqual(ret['error'], None)
        ret = p.parse('{1;2;4}/2')
        self.assertEqual(ret['result'], [[0.5], [1], [2]])
        self.assertEqual(ret['error'], None)
        ret = p.parse('{1;2;4}*2')
        self.assertEqual(ret['result'], [[2], [4], [8]])
        self.assertEqual(ret['error'], None)
        ret = p.parse('2*{1;2;4}')
        self.assertEqual(ret['result'], [[2], [4], [8]])
        self.assertEqual(ret['error'], None)
        ret = p.parse('2+{1;2;4}')
        self.assertEqual(ret['result'], [[3], [4], [6]])
        self.assertEqual(ret['error'], None)
        ret = p.parse('{1;2;4}+2')
        self.assertEqual(ret['result'], [[3], [4], [6]])
        self.assertEqual(ret['error'], None)
        ret = p.parse('2-{1;2;4}')
        self.assertEqual(ret['result'], [[1], [0], [-2]])
        self.assertEqual(ret['error'], None)
        ret = p.parse('{1;2;4}-2')
        self.assertEqual(ret['result'], [[-1], [0], [2]])
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

    def test_arithmetic_precedes_concatenation(self):
        p = Parser()
        for expression, expected in (
            ('1/3&""', '0.333333333333333'),
            ('1+2&"x"', '3x'), ('"x"&1+2', 'x3'),
            ('3-1&"x"', '2x'), ('"x"&3-1', 'x2'),
            ('2*3&"x"', '6x'), ('"x"&2*3', 'x6'),
            ('8/2&"x"', '4x'), ('"x"&8/2', 'x4'),
            ('2^3&"x"', '8x'), ('"x"&2%', 'x0.02'),
            ('"a"&1+2&"b"', 'a3b'),
        ):
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': expected, 'error': None})

    def test_concatenation_precedes_comparisons_and_respects_parentheses(self):
        p = Parser()
        for expression, expected in (
            ('1+2&"x"="3x"', True), ('"x"&1+2="x3"', True),
            ('1&2<>"12"', False), ('"a"&1<"b"', True),
            ('1&2&3', '123'), ('(1&2)+3', 15),
            ('1&(2+3)', '15'), ('1/(3&"")', 1 / 3),
        ):
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': expected, 'error': None})

    def test_concatenation_precedence_preserves_arrays_and_error_handling(self):
        p = Parser()
        for expression, expected in (
            ('{1,2}+1&"x"', [['2x', '3x']]),
            ('"x"&{2;4}/2', [['x1'], ['x2']]),
            ('IFERROR(1/0&"x",99)', 99),
            ('IFERROR("x"&1/0,99)', 99),
        ):
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': expected, 'error': None})

    def test_concatenation_treats_blank_operands_as_empty_text(self):
        p = Parser()
        p.set_function('BLANK', lambda: None)
        for expression, expected in [
            ('BLANK()&"x"', 'x'),
            ('"x"&BLANK()', 'x'),
            ('BLANK()&BLANK()', ''),
            ('0&BLANK()', '0'),
            ('BLANK()&0', '0'),
            ('FALSE()&BLANK()', 'FALSE'),
            ('BLANK()&TRUE()', 'TRUE'),
            ('"None"&BLANK()', 'None'),
        ]:
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression),
                                 {'result': expected, 'error': None})

    def test_concatenation_formats_native_numeric_and_boolean_array_values(self):
        p = Parser()
        p.set_function('DATA', lambda: [[1.0, True], [1 / 3, False]])
        self.assertEqual(p.parse('DATA()&"x"'),
                         {'result': [['1x', 'TRUEx'], ['0.333333333333333x', 'FALSEx']],
                          'error': None})

    def test_concatenation_treats_blank_array_cells_as_empty_text(self):
        p = Parser()
        p.set_function('BLANK', lambda: None)
        for expression, expected in [
            ('{BLANK(),"a"}&"x"', [['x', 'ax']]),
            ('"x"&{BLANK();"a"}', [['x'], ['xa']]),
            ('{BLANK(),0;FALSE(),"a"}&BLANK()', [['', '0'], ['FALSE', 'a']]),
            ('{BLANK(),"a"}&{BLANK(),"b"}', [['', 'ab']]),
            ('{BLANK();"a"}&{"x","y"}', [['x', 'y'], ['ax', 'ay']]),
        ]:
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression),
                                 {'result': expected, 'error': None})

    def test_concatenation_preserves_errors_with_blank_operands(self):
        p = Parser()
        p.set_function('BLANK', lambda: None)
        p.set_function('FAIL', lambda: error.DIV_ZERO)
        for expression in ('BLANK()&FAIL()', 'FAIL()&BLANK()'):
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression),
                                 {'result': None, 'error': '#DIV/0!'})
                self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                 {'result': 99, 'error': None})
        self.assertEqual(p.parse('IFERROR({BLANK(),FAIL()}&"x",99)'),
                         {'result': [['x', 99]], 'error': None})
        self.assertEqual(p.parse('IFERROR("x"&{FAIL(),BLANK()},99)'),
                         {'result': [[99, 'x']], 'error': None})

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
