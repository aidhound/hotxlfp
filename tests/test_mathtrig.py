# -*- coding: utf-8 -*-
import unittest
import math
from hotxlfp import Parser


class TestMathTrig(unittest.TestCase):

    def test_abs(self):
        p = Parser(debug=True)
        ret = p.parse('ABS(1)')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)
        ret = p.parse('ABS(-1)')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)
        ret = p.parse('ABS("a")')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#VALUE!')

    def test_acos(self):
        p = Parser(debug=True)
        ret = p.parse('ACOS(-0.5)')
        self.assertTrue(str(ret['result']).startswith('2.094395102'))
        self.assertEqual(ret['error'], None)
        ret = p.parse('ACOS(-0.5)*180/PI()')
        self.assertTrue(str(ret['result']).startswith('120.0'))
        self.assertEqual(ret['error'], None)
        ret = p.parse('ACOS(1/0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')

    def test_acosh(self):
        p = Parser(debug=True)
        ret = p.parse('ACOSH(1)')
        self.assertEqual(ret['result'], 0)
        self.assertEqual(ret['error'], None)
        ret = p.parse('ACOSH(10)')
        self.assertTrue(str(ret['result']).startswith('2.9932228'))
        self.assertEqual(ret['error'], None)
        ret = p.parse('ACOSH(1/0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')

    def test_acosh_domain_and_overflow_errors_are_handleable(self):
        p = Parser()
        p.set_function('HUGE', lambda: 10**400)
        for source in ('0', '-2', '0.5', '"0.5"', 'HUGE()'):
            expression = 'ACOSH(' + source + ')'
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': None, 'error': '#NUM!'})
                self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                 {'result': 99, 'error': None})
                self.assertEqual(p.parse('IFNA(' + expression + ',99)'),
                                 {'result': None, 'error': '#NUM!'})

    def test_acosh_keeps_large_valid_results_and_original_errors(self):
        p = Parser()
        p.set_function('LARGE', lambda: 1e200)
        for source, expected in (
            ('1', 0), ('"10"', math.acosh(10)),
            ('1.0000000000000002', math.acosh(1.0000000000000002)),
            ('LARGE()', math.acosh(1e200)),
            ('"1e200"', math.acosh(1e200)), ('"1e308"', math.acosh(1e308)),
        ):
            with self.subTest(source=source):
                result = p.parse('ACOSH(' + source + ')')
                self.assertIsNone(result['error'])
                self.assertAlmostEqual(result['result'], expected, delta=1e-14)
        for source, code in (
            ('#N/A', '#N/A'), ('#DIV/0!', '#DIV/0!'),
            ('"bad"', '#VALUE!'), ('"NaN"', '#NUM!'),
        ):
            expression = 'ACOSH(' + source + ')'
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': None, 'error': code})
                self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                 {'result': 99, 'error': None})
                expected = ({'result': 77, 'error': None} if code == '#N/A'
                            else {'result': None, 'error': code})
                self.assertEqual(p.parse('IFNA(' + expression + ',77)'), expected)

    def test_acot(self):
        p = Parser(debug=True)
        ret = p.parse('ACOT(2)')
        self.assertTrue(str(ret['result']).startswith('0.4636'))
        self.assertEqual(ret['error'], None)
        ret = p.parse('ACOT(1/0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')

    def test_acot_zero_and_negative_inputs_use_excels_angle_range(self):
        p = Parser()
        p.set_function('ZERO', lambda: -0.0)
        for source, expected in (
            ('0', math.pi / 2), ('ZERO()', math.pi / 2),
            ('-1', 3 * math.pi / 4), ('"-2"', math.pi - math.atan(0.5)),
            ('1', math.pi / 4), ('2', math.atan(0.5)),
            ('"1e308"', 1e-308), ('"-1e308"', math.pi),
            ('"1e-308"', math.pi / 2), ('"-1e-308"', math.pi / 2),
        ):
            expression = 'ACOT(' + source + ')'
            with self.subTest(expression=expression):
                for wrapped in (expression, 'IFERROR(' + expression + ',99)'):
                    result = p.parse(wrapped)
                    self.assertIsNone(result['error'])
                    self.assertTrue(math.isclose(result['result'], expected, rel_tol=1e-14))

    def test_acot_preserves_errors_and_handles_numeric_overflow(self):
        p = Parser()
        p.set_function('HUGE', lambda: 10**400)
        for source, code in (
            ('#N/A', '#N/A'), ('#DIV/0!', '#DIV/0!'),
            ('"bad"', '#VALUE!'), ('"NaN"', '#NUM!'), ('HUGE()', '#NUM!'),
        ):
            expression = 'ACOT(' + source + ')'
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': None, 'error': code})
                self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                 {'result': 99, 'error': None})
                expected = ({'result': 77, 'error': None} if code == '#N/A'
                            else {'result': None, 'error': code})
                self.assertEqual(p.parse('IFNA(' + expression + ',77)'), expected)

    def test_acoth(self):
        p = Parser(debug=True)
        ret = p.parse('ACOTH(6)')
        self.assertTrue(str(ret['result']).startswith('0.168'))
        self.assertEqual(ret['error'], None)
        ret = p.parse('ACOTH(1/0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')

    def test_acoth_invalid_domains_return_handleable_numeric_errors(self):
        p = Parser()
        for source in ('-1', '-0.5', '0', '0.5', '1', '"1"'):
            expression = 'ACOTH(' + source + ')'
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': None, 'error': '#NUM!'})
                self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                 {'result': 99, 'error': None})
                self.assertEqual(p.parse('IFNA(' + expression + ',99)'),
                                 {'result': None, 'error': '#NUM!'})

    def test_acoth_valid_inputs_keep_precision_and_original_errors(self):
        p = Parser()
        p.set_function('LARGE', lambda: 1e20)
        for source, expected in (
            ('2', math.log(3) / 2), ('-2', -math.log(3) / 2),
            ('"6"', 0.16823611831060645),
            ('LARGE()', 1e-20), ('"-1e20"', -1e-20),
            ('1.000001', math.log(2000001) / 2),
            ('-1.000001', -math.log(2000001) / 2),
        ):
            expression = 'ACOTH(' + source + ')'
            with self.subTest(expression=expression):
                result = p.parse(expression)
                self.assertIsNone(result['error'])
                self.assertTrue(math.isclose(result['result'], expected, rel_tol=1e-10))
        for source, code in (
            ('#N/A', '#N/A'), ('#DIV/0!', '#DIV/0!'),
            ('"bad"', '#VALUE!'), ('"NaN"', '#NUM!'),
        ):
            expression = 'ACOTH(' + source + ')'
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': None, 'error': code})
                self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                 {'result': 99, 'error': None})
                expected = ({'result': 77, 'error': None} if code == '#N/A'
                            else {'result': None, 'error': code})
                self.assertEqual(p.parse('IFNA(' + expression + ',77)'), expected)

    def test_sin(self):
        p = Parser(debug=True)
        ret = p.parse('SIN(PI()/2)')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)
        ret = p.parse('SIN(1/0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')

    def test_sinh(self):
        p = Parser(debug=True)
        ret = p.parse('2.868*SINH(0.0342*1.03)')
        self.assertAlmostEqual(ret['result'], 0.1010491, places=7)
        self.assertEqual(ret['error'], None)
        ret = p.parse('SINH(1/0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')

    def test_asin(self):
        p = Parser(debug=True)
        ret = p.parse('ASIN(-0.5)')
        self.assertAlmostEqual(ret['result'], -0.523598776, places=9)
        self.assertEqual(ret['error'], None)
        ret = p.parse('ASIN(1/0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')

    def test_asinh(self):
        p = Parser(debug=True)
        ret = p.parse('ASINH(-2.5)')
        self.assertAlmostEqual(ret['result'], -1.647231146, places=9)
        self.assertEqual(ret['error'], None)
        ret = p.parse('ASINH(1/0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')

    def test_cos(self):
        p = Parser(debug=True)
        ret = p.parse('COS(0)')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)
        ret = p.parse('COS(1/0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')

    def test_cosh(self):
        p = Parser(debug=True)
        ret = p.parse('COSH(4)')
        self.assertAlmostEqual(ret['result'], 27.308233, places=6)
        self.assertEqual(ret['error'], None)
        ret = p.parse('COSH(1/0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')

    def test_sinh_and_cosh_overflow_errors_are_handleable(self):
        p = Parser()
        p.set_function('HUGE', lambda: 10**400)
        for name in ('SINH', 'COSH'):
            for source in ('1000', '-1000', '"1000"', '"-1000"', 'HUGE()'):
                expression = name + '(' + source + ')'
                with self.subTest(expression=expression):
                    self.assertEqual(p.parse(expression), {'result': None, 'error': '#NUM!'})
                    self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                     {'result': 99, 'error': None})
                    self.assertEqual(p.parse('IFNA(' + expression + ',99)'),
                                     {'result': None, 'error': '#NUM!'})

    def test_sinh_and_cosh_keep_valid_results_and_original_errors(self):
        p = Parser()
        p.set_function('DATA', lambda: -4)
        for name, function in (('SINH', math.sinh), ('COSH', math.cosh)):
            for source, value in (('0', 0), ('4', 4), ('"-4"', -4),
                                  ('DATA()', -4), ('700', 700), ('-700', -700)):
                expression = name + '(' + source + ')'
                with self.subTest(expression=expression):
                    result = p.parse(expression)
                    self.assertIsNone(result['error'])
                    self.assertTrue(math.isclose(result['result'], function(value), rel_tol=1e-14))
            for source, code in (
                ('#N/A', '#N/A'), ('#DIV/0!', '#DIV/0!'),
                ('"bad"', '#VALUE!'), ('"NaN"', '#NUM!'),
            ):
                expression = name + '(' + source + ')'
                with self.subTest(expression=expression):
                    self.assertEqual(p.parse(expression), {'result': None, 'error': code})
                    self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                     {'result': 99, 'error': None})
                    expected = ({'result': 77, 'error': None} if code == '#N/A'
                                else {'result': None, 'error': code})
                    self.assertEqual(p.parse('IFNA(' + expression + ',77)'), expected)

    def test_cot(self):
        p = Parser(debug=True)
        ret = p.parse('COT(30)')
        self.assertAlmostEqual(ret['result'], -0.156, places=3)
        self.assertEqual(ret['error'], None)
        ret = p.parse('COT(45)')
        self.assertAlmostEqual(ret['result'], 0.617, places=3)
        self.assertEqual(ret['error'], None)
        ret = p.parse('COT(1/0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')

    def test_cot_zero_and_range_errors_are_handleable(self):
        p = Parser()
        p.set_function('ZERO', lambda: -0.0)
        p.set_function('HUGE', lambda: 10**400)
        for source, code in (
            ('0', '#DIV/0!'), ('"0"', '#DIV/0!'), ('ZERO()', '#DIV/0!'),
            ('2^27', '#NUM!'), ('-(2^27)', '#NUM!'),
            ('2^27+1', '#NUM!'), ('"-134217729"', '#NUM!'),
            ('HUGE()', '#NUM!'),
        ):
            expression = 'COT(' + source + ')'
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': None, 'error': code})
                self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                 {'result': 99, 'error': None})
                self.assertEqual(p.parse('IFNA(' + expression + ',77)'),
                                 {'result': None, 'error': code})

    def test_cot_keeps_valid_results_and_original_errors(self):
        p = Parser()
        for source, value in (('1', 1), ('"-1"', -1),
                              ('2^27-1', 2**27 - 1), ('-(2^27-1)', -(2**27 - 1))):
            with self.subTest(source=source):
                result = p.parse('COT(' + source + ')')
                self.assertIsNone(result['error'])
                self.assertTrue(math.isclose(result['result'], math.cos(value) / math.sin(value),
                                             rel_tol=1e-14))
        for source, code in (('#N/A', '#N/A'), ('#DIV/0!', '#DIV/0!'),
                             ('"bad"', '#VALUE!'), ('"NaN"', '#NUM!')):
            expression = 'COT(' + source + ')'
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': None, 'error': code})
                self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                 {'result': 99, 'error': None})
                expected = ({'result': 77, 'error': None} if code == '#N/A'
                            else {'result': None, 'error': code})
                self.assertEqual(p.parse('IFNA(' + expression + ',77)'), expected)

    def test_tan(self):
        p = Parser(debug=True)
        ret = p.parse('TAN(45*PI()/180)')
        self.assertAlmostEqual(ret['result'], 1, places=9)
        self.assertEqual(ret['error'], None)
        ret = p.parse('TAN(1/0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')

    def test_tanh(self):
        p = Parser(debug=True)
        ret = p.parse('TANH(0.5)')
        self.assertAlmostEqual(ret['result'], 0.462117, places=6)
        self.assertEqual(ret['error'], None)
        ret = p.parse('TANH(1/0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')

    def test_atan(self):
        p = Parser(debug=True)
        ret = p.parse('ATAN(1)*180/PI()')
        self.assertEqual(ret['result'], 45)
        self.assertEqual(ret['error'], None)
        ret = p.parse('ATAN(1/0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')

    def test_atan2(self):
        p = Parser(debug=True)
        ret = p.parse('ATAN2(1, 1)')
        self.assertAlmostEqual(ret['result'], 0.785398163, places=9)
        self.assertEqual(ret['error'], None)
        ret = p.parse('ATAN2(1, 0.8)')
        self.assertAlmostEqual(ret['result'], 0.674740942, places=9)
        self.assertEqual(ret['error'], None)
        ret = p.parse('ATAN2(0, 0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')

    def test_atan2_axes_and_quadrants(self):
        p = Parser()
        p.set_function('ZERO', lambda: -0.0)
        for args, expected in (
            ('1,0', 0), ('-1,0', math.pi),
            ('1,ZERO()', 0), ('-1,ZERO()', math.pi),
            ('0,1', math.pi / 2), ('0,-1', -math.pi / 2),
            ('1,1', math.pi / 4), ('-1,1', 3 * math.pi / 4),
            ('-1,-1', -3 * math.pi / 4), ('1,-1', -math.pi / 4),
            ('"-1","0"', math.pi),
        ):
            expression = 'ATAN2(' + args + ')'
            with self.subTest(expression=expression):
                for wrapped in (expression, 'IFERROR(' + expression + ',99)'):
                    result = p.parse(wrapped)
                    self.assertIsNone(result['error'])
                    self.assertAlmostEqual(result['result'], expected)

    def test_atan2_errors_remain_handleable_in_each_coordinate(self):
        p = Parser()
        p.set_function('HUGE', lambda: 10**400)
        for args, code in (
            ('0,0', '#DIV/0!'), ('"0","0"', '#DIV/0!'),
            ('#N/A,1', '#N/A'), ('1,#N/A', '#N/A'),
            ('#DIV/0!,1', '#DIV/0!'), ('1,#DIV/0!', '#DIV/0!'),
            ('"bad",1', '#VALUE!'), ('1,"bad"', '#VALUE!'),
            ('"NaN",1', '#NUM!'), ('1,"NaN"', '#NUM!'),
            ('HUGE(),1', '#NUM!'), ('1,HUGE()', '#NUM!'),
        ):
            expression = 'ATAN2(' + args + ')'
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': None, 'error': code})
                self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                 {'result': 99, 'error': None})
                expected = ({'result': 77, 'error': None} if code == '#N/A'
                            else {'result': None, 'error': code})
                self.assertEqual(p.parse('IFNA(' + expression + ',77)'), expected)

    def test_remaining_trig_functions_return_handleable_conversion_overflow(self):
        p = Parser()
        for value in (10**400, -(10**400)):
            p.set_function('HUGE', lambda value=value: value)
            for name in ('SIN', 'COS', 'TAN', 'ASINH', 'TANH', 'ATAN'):
                expression = name + '(HUGE())'
                with self.subTest(function=name, negative=value < 0):
                    self.assertEqual(p.parse(expression), {'result': None, 'error': '#NUM!'})
                    self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                     {'result': 99, 'error': None})
                    self.assertEqual(p.parse('IFNA(' + expression + ',77)'),
                                     {'result': None, 'error': '#NUM!'})

    def test_remaining_trig_functions_keep_valid_inputs_and_original_errors(self):
        p = Parser()
        for name, function in (
            ('SIN', math.sin), ('COS', math.cos), ('TAN', math.tan),
            ('ASINH', math.asinh), ('TANH', math.tanh), ('ATAN', math.atan),
        ):
            for source, value in (('0', 0), ('"-0.5"', -0.5), ('"1e308"', 1e308)):
                expression = name + '(' + source + ')'
                with self.subTest(expression=expression):
                    result = p.parse(expression)
                    self.assertIsNone(result['error'])
                    self.assertTrue(math.isclose(result['result'], function(value), rel_tol=1e-14))
            for source, code in (('#N/A', '#N/A'), ('#DIV/0!', '#DIV/0!'),
                                 ('"bad"', '#VALUE!'), ('"NaN"', '#NUM!')):
                expression = name + '(' + source + ')'
                with self.subTest(expression=expression):
                    self.assertEqual(p.parse(expression), {'result': None, 'error': code})
                    self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                     {'result': 99, 'error': None})
                    expected = ({'result': 77, 'error': None} if code == '#N/A'
                                else {'result': None, 'error': code})
                    self.assertEqual(p.parse('IFNA(' + expression + ',77)'), expected)

    def test_atanh(self):
        p = Parser(debug=True)
        ret = p.parse('ATANH(0.76159416)')
        self.assertAlmostEqual(ret['result'], 1.00000001, places=9)
        self.assertEqual(ret['error'], None)
        ret = p.parse('ATANH(1/0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')

    def test_inverse_trig_domain_errors_remain_handleable(self):
        p = Parser()
        p.set_function('HUGE', lambda: 10**1000)
        for name, inputs in (
            ('ACOS', ('-2', '2', '-1.0001', '1.0001', '"2"', 'HUGE()')),
            ('ASIN', ('-2', '2', '-1.0001', '1.0001', '"2"', 'HUGE()')),
            ('ATANH', ('-2', '2', '-1', '1', '"1"', 'HUGE()')),
        ):
            for source in inputs:
                expression = name + '(' + source + ')'
                with self.subTest(expression=expression):
                    self.assertEqual(p.parse(expression),
                                     {'result': None, 'error': '#NUM!'})
                    self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                     {'result': 99, 'error': None})
                    self.assertEqual(p.parse('IFNA(' + expression + ',77)'),
                                     {'result': None, 'error': '#NUM!'})

    def test_inverse_trig_keeps_valid_boundary_results(self):
        p = Parser()
        for expression, expected in (
            ('ACOS(-1)', math.pi), ('ACOS(1)', 0),
            ('ASIN(-1)', -math.pi / 2), ('ASIN(1)', math.pi / 2),
            ('ASIN(0)', 0), ('ATANH(0)', 0),
            ('ATANH(-0.5)', -0.5493061443340549),
            ('ATANH("0.5")', 0.5493061443340549),
        ):
            with self.subTest(expression=expression):
                result = p.parse(expression)
                self.assertEqual(result['error'], None)
                self.assertAlmostEqual(result['result'], expected)

    def test_sqrt(self):
        p = Parser(debug=True)
        ret = p.parse('SQRT(16)')
        self.assertEqual(ret['result'], 4)
        self.assertEqual(ret['error'], None)
        ret = p.parse('SQRT(1/0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')

    def test_sqrt_and_exp_return_handleable_numeric_errors(self):
        p = Parser()
        p.set_function('HUGE', lambda: 10**1000)
        for expression in ('SQRT(-1)', 'SQRT("-1")', 'SQRT(HUGE())',
                           'EXP(1000)', 'EXP("1000")', 'EXP(HUGE())'):
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression),
                                 {'result': None, 'error': '#NUM!'})
                self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                 {'result': 99, 'error': None})
                self.assertEqual(p.parse('IFNA(' + expression + ',77)'),
                                 {'result': None, 'error': '#NUM!'})

    def test_sqrt_and_exp_keep_valid_results(self):
        p = Parser()
        for expression, expected in (('SQRT(0)', 0), ('SQRT("16")', 4),
                                     ('EXP(0)', 1), ('EXP("1")', math.e),
                                     ('EXP(-1)', 1 / math.e)):
            with self.subTest(expression=expression):
                result = p.parse(expression)
                self.assertEqual(result['error'], None)
                self.assertAlmostEqual(result['result'], expected)

    def test_round(self):
        p = Parser(debug=True)
        ret = p.parse('ROUND(23.7825, 2)')
        self.assertEqual(ret['result'], 23.78)
        self.assertEqual(ret['error'], None)
        ret = p.parse('ROUND(23.789, 2)')
        self.assertEqual(ret['result'], 23.79)
        self.assertEqual(ret['error'], None)

    def test_roundup(self):
        p = Parser(debug=True)
        ret = p.parse('ROUNDUP(23.7825, 2)')
        self.assertEqual(ret['result'], 23.79)
        self.assertEqual(ret['error'], None)

    def test_rounddown(self):
        p = Parser(debug=True)
        ret = p.parse('ROUNDDOWN(23.7895, 2)')
        self.assertEqual(ret['result'], 23.78)
        self.assertEqual(ret['error'], None)

    def test_ln(self):
        p = Parser(debug=True)
        ret = p.parse('LN(EXP(1))')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)
        ret = p.parse('LN(EXP(3))')
        self.assertEqual(ret['result'], 3)
        self.assertEqual(ret['error'], None)

    def test_logarithm_domain_errors_remain_handleable(self):
        p = Parser()
        for expression, code in (
            ('LN(0)', '#NUM!'), ('LN(-1)', '#NUM!'), ('LN("-1")', '#NUM!'),
            ('LOG(0)', '#NUM!'), ('LOG(-1,2)', '#NUM!'),
            ('LOG(8,0)', '#NUM!'), ('LOG(8,-1)', '#NUM!'),
            ('LOG(8,1)', '#DIV/0!'), ('LOG(1,1)', '#DIV/0!'),
            ('LOG(0,1)', '#NUM!'), ('LOG(-1,0)', '#NUM!'),
            ('LOG10(0)', '#NUM!'), ('LOG10(-1)', '#NUM!'),
        ):
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': None, 'error': code})
                self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                 {'result': 99, 'error': None})
                self.assertEqual(p.parse('IFNA(' + expression + ',77)'),
                                 {'result': None, 'error': code})

    def test_log(self):
        p = Parser(debug=True)
        ret = p.parse('LOG(10)')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)
        ret = p.parse('LOG(8, 2)')
        self.assertEqual(ret['result'], 3)
        self.assertEqual(ret['error'], None)
        for expression, expected in (('LN(1)', 0), ('LOG(0.5,0.5)', 1),
                                     ('LOG(8,0.5)', -3), ('LOG("8","2")', 3)):
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': expected, 'error': None})

    def test_log10(self):
        p = Parser(debug=True)
        ret = p.parse('LOG10(10)')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)
        ret = p.parse('LOG10(100000)')
        self.assertEqual(ret['result'], 5)
        self.assertEqual(ret['error'], None)

    def test_sum(self):
        p = Parser(debug=True)
        ret = p.parse('SUM(10)')
        self.assertEqual(ret['result'], 10)
        self.assertEqual(ret['error'], None)
        ret = p.parse('SUM(1;2)')
        self.assertEqual(ret['result'], 3)
        self.assertEqual(ret['error'], None)
        ret = p.parse('SUM(1;2;"aa")')
        self.assertEqual(ret['result'], 3)
        self.assertEqual(ret['error'], None)
        ret = p.parse('SUM(1;2;{4;5};"aa")')
        self.assertEqual(ret['result'], 12)
        self.assertEqual(ret['error'], None)
        ret = p.parse('SUM(,,,)')
        self.assertEqual(ret['result'], 0)
        self.assertEqual(ret['error'], None)
        ret = p.parse('SUM(TRUE,,"2")')
        self.assertEqual(ret['result'], 3)
        self.assertEqual(ret['error'], None)

    def test_sumif(self):
        p = Parser(debug=True)
        ret = p.parse('SUMIF({1;4;5}, ">0")')
        self.assertEqual(ret['result'], 10)
        self.assertEqual(ret['error'], None)
        ret = p.parse('SUMIF({1;4;5}, ">1")')
        self.assertEqual(ret['result'], 9)
        self.assertEqual(ret['error'], None)

    def test_ceiling(self):
        p = Parser(debug=True)
        ret = p.parse('CEILING(2.5, 1)')
        self.assertEqual(ret['result'], 3)
        self.assertEqual(ret['error'], None)
        ret = p.parse('CEILING(-2.5, -2)')
        self.assertEqual(ret['result'], -4)
        self.assertEqual(ret['error'], None)
        ret = p.parse('CEILING(-2.5, 2)')
        self.assertEqual(ret['result'], -2)
        self.assertEqual(ret['error'], None)
        ret = p.parse('CEILING(1.5, 0.1)')
        self.assertEqual(ret['result'], 1.5)
        self.assertEqual(ret['error'], None)
        ret = p.parse('CEILING(0.234, 0.01)')
        self.assertEqual(ret['result'], 0.24)
        self.assertEqual(ret['error'], None)

    def test_floor(self):
        p = Parser(debug=True)
        ret = p.parse('FLOOR(3.7,2)')
        self.assertEqual(ret['result'], 2)
        self.assertEqual(ret['error'], None)
        ret = p.parse('FLOOR(-2.5,-2)')
        self.assertEqual(ret['result'], -2)
        self.assertEqual(ret['error'], None)
        ret = p.parse('FLOOR(2.5,-2)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#NUM!')
        ret = p.parse('FLOOR(1.58,0.1)')
        self.assertEqual(ret['result'], 1.5)
        self.assertEqual(ret['error'], None)
        ret = p.parse('FLOOR(0.234,0.01)')
        self.assertEqual(ret['result'], 0.23)
        self.assertEqual(ret['error'], None)
        ret = p.parse('FLOOR(-5.6; 1)')
        self.assertEqual(ret['result'], -6)
        self.assertEqual(ret['error'], None)
        ret = p.parse('FLOOR(-5.6; -1)')
        self.assertEqual(ret['result'], -5)
        self.assertEqual(ret['error'], None)


    def test_quotient(self):
        p = Parser(debug=True)
        ret = p.parse('QUOTIENT(5, 2)')
        self.assertEqual(ret['result'], 2)
        self.assertEqual(ret['error'], None)
        ret = p.parse('QUOTIENT(4.5, 3.1)')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)
        ret = p.parse('QUOTIENT(-10, 3)')
        self.assertEqual(ret['result'], -3)
        self.assertEqual(ret['error'], None)
        ret = p.parse('QUOTIENT(3, 0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')

    def test_mod(self):
        p = Parser(debug=True)
        ret = p.parse('MOD(3, 2)')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)
        ret = p.parse('MOD(-3, 2)')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)
        ret = p.parse('MOD(3, -2)')
        self.assertEqual(ret['result'], -1)
        self.assertEqual(ret['error'], None)
        ret = p.parse('MOD(-3, -2)')
        self.assertEqual(ret['result'], -1)
        self.assertEqual(ret['error'], None)
        ret = p.parse('MOD(1/0, 1)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')
        ret = p.parse('MOD(1, 1/0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')
        ret = p.parse('MOD(3, 0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')

    def test_radians(self):
        p = Parser(debug=True)
        ret = p.parse('RADIANS(270)')
        self.assertTrue(str(ret['result']).startswith('4.7123'))
        self.assertEqual(ret['error'], None)
        ret = p.parse('RADIANS(1/0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')

    def test_degrees(self):
        p = Parser(debug=True)
        ret = p.parse('DEGREES(PI())')
        self.assertEqual(ret['result'], 180)
        self.assertEqual(ret['error'], None)
        ret = p.parse('DEGREES(1/0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')

    def test_power(self):
        p = Parser(debug=True)
        ret = p.parse('POWER(5,2)')
        self.assertEqual(ret['result'], 25)
        self.assertEqual(ret['error'], None)
        ret = p.parse('POWER(98.6,3.2)')
        self.assertTrue(str(ret['result']).startswith('2401077.222'))
        self.assertEqual(ret['error'], None)
        ret = p.parse('POWER(4,5/4)')
        self.assertTrue(str(ret['result']).startswith('5.656854249'))
        self.assertEqual(ret['error'], None)

    def test_product(self):
        p = Parser(debug=True)
        ret = p.parse('PRODUCT(10)')
        self.assertEqual(ret['result'], 10)
        self.assertEqual(ret['error'], None)
        ret = p.parse('PRODUCT(1;2)')
        self.assertEqual(ret['result'], 2)
        self.assertEqual(ret['error'], None)
        ret = p.parse('PRODUCT(1;2;"aa")')
        self.assertEqual(ret['result'], 2)
        self.assertEqual(ret['error'], None)
        ret = p.parse('PRODUCT(1;2;{4;5};"aa")')
        self.assertEqual(ret['result'], 40)
        self.assertEqual(ret['error'], None)

    def test_odd(self):
        p = Parser(debug=True)
        ret = p.parse('ODD(1.5)')
        self.assertEqual(ret['result'], 3)
        self.assertEqual(ret['error'], None)
        ret = p.parse('ODD(3)')
        self.assertEqual(ret['result'], 3)
        self.assertEqual(ret['error'], None)
        ret = p.parse('ODD(2)')
        self.assertEqual(ret['result'], 3)
        self.assertEqual(ret['error'], None)
        ret = p.parse('ODD(-1)')
        self.assertEqual(ret['result'], -1)
        self.assertEqual(ret['error'], None)
        ret = p.parse('ODD(-2)')
        self.assertEqual(ret['result'], -3)
        self.assertEqual(ret['error'], None)
        ret = p.parse('ODD(1/0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')

    def test_even(self):
        p = Parser(debug=True)
        ret = p.parse('EVEN(1.5)')
        self.assertEqual(ret['result'], 2)
        self.assertEqual(ret['error'], None)
        ret = p.parse('EVEN(3)')
        self.assertEqual(ret['result'], 4)
        self.assertEqual(ret['error'], None)
        ret = p.parse('EVEN(2)')
        self.assertEqual(ret['result'], 2)
        self.assertEqual(ret['error'], None)
        ret = p.parse('EVEN(-1)')
        self.assertEqual(ret['result'], -2)
        self.assertEqual(ret['error'], None)
        ret = p.parse('EVEN(1/0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')

    def test_decimal(self):
        p = Parser(debug=True)
        ret = p.parse('DECIMAL("FF";16)')
        self.assertEqual(ret['result'], 255)
        self.assertEqual(ret['error'], None)
        ret = p.parse('DECIMAL(111;2)')
        self.assertEqual(ret['result'], 7)
        self.assertEqual(ret['error'], None)
        ret = p.parse('DECIMAL("zap";36)')
        self.assertEqual(ret['result'], 45745)
        self.assertEqual(ret['error'], None)

    def test_numeric_text_consumers_use_shared_text_conversion(self):
        p = Parser()
        for expression, expected in (('DECIMAL(10.0,2)', 2), ('ARABIC(NULL)', 0)):
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': expected, 'error': None})
        for expression in ('DECIMAL(#N/A,2)', 'ARABIC(#N/A)'):
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': None, 'error': '#N/A'})
                self.assertEqual(p.parse('IFNA(' + expression + ',99)'),
                                 {'result': 99, 'error': None})

    def test_base(self):
        p = Parser(debug=True)
        ret = p.parse('BASE(7,2)')
        self.assertEqual(ret['result'], '111')
        self.assertEqual(ret['error'], None)
        ret = p.parse('BASE(100,16)')
        self.assertEqual(ret['result'], '64')
        self.assertEqual(ret['error'], None)
        ret = p.parse('BASE(15,2,10)')
        self.assertEqual(ret['result'], '0000001111')
        self.assertEqual(ret['error'], None)

    def test_fact(self):
        p = Parser(debug=True)
        ret = p.parse('FACT(5)')
        self.assertEqual(ret['result'], 120)
        self.assertEqual(ret['error'], None)
        ret = p.parse('FACT(1.9)')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)
        ret = p.parse('FACT(0)')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)
        ret = p.parse('FACT(-1)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#NUM!')
        ret = p.parse('FACT(1)')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)

    def test_factdouble(self):
        p = Parser(debug=True)
        ret = p.parse('FACTDOUBLE(6)')
        self.assertEqual(ret['result'], 48)
        self.assertEqual(ret['error'], None)
        ret = p.parse('FACTDOUBLE(7)')
        self.assertEqual(ret['result'], 105)
        self.assertEqual(ret['error'], None)
        ret = p.parse('FACTDOUBLE(0)')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)
        ret = p.parse('FACTDOUBLE(1)')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)
        ret = p.parse('FACTDOUBLE(-10)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#NUM!')
        ret = p.parse('FACTDOUBLE("foo")')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#VALUE!')

    def test_roman(self):
        p = Parser(debug=True)
        ret = p.parse('ROMAN(499,0)')
        self.assertEqual(ret['result'], 'CDXCIX')
        self.assertEqual(ret['error'], None)
        ret = p.parse('ROMAN(499,1)')
        self.assertEqual(ret['result'], 'LDVLIV')
        self.assertEqual(ret['error'], None)
        ret = p.parse('ROMAN(499,2)')
        self.assertEqual(ret['result'], 'XDIX')
        self.assertEqual(ret['error'], None)
        ret = p.parse('ROMAN(499,3)')
        self.assertEqual(ret['result'], 'VDIV')
        self.assertEqual(ret['error'], None)
        ret = p.parse('ROMAN(499,4)')
        self.assertEqual(ret['result'], 'ID')
        self.assertEqual(ret['error'], None)
        ret = p.parse('ROMAN(4000)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#VALUE!')
        ret = p.parse('ROMAN(499,TRUE())')
        self.assertEqual(ret['result'], 'CDXCIX')
        self.assertEqual(ret['error'], None)
        ret = p.parse('ROMAN(499,FALSE())')
        self.assertEqual(ret['result'], 'ID')
        self.assertEqual(ret['error'], None)

    def test_arabic(self):
        p = Parser(debug=True)
        ret = p.parse('ARABIC("M")')
        self.assertEqual(ret['result'], 1000)
        self.assertEqual(ret['error'], None)
        ret = p.parse('ARABIC("LVII")')
        self.assertEqual(ret['result'], 57)
        self.assertEqual(ret['error'], None)
        ret = p.parse('ARABIC("mcmxii")')
        self.assertEqual(ret['result'], 1912)
        self.assertEqual(ret['error'], None)
        ret = p.parse('ARABIC(ROMAN(499))')
        self.assertEqual(ret['result'], 499)
        self.assertEqual(ret['error'], None)
        ret = p.parse('ARABIC(ROMAN(499, 4))')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#VALUE!')

    def test_rand(self):
        p = Parser()
        ret = p.parse('RAND(2)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#ERROR!')
        for i in range(1000):
            ret = p.parse('RAND()')
            self.assertGreaterEqual(ret['result'], 0)
            self.assertLessEqual(ret['result'], 1)
            self.assertEqual(ret['error'], None)

    def test_randbetween(self):
        p = Parser()
        ret = p.parse('RANDBETWEEN(2)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#ERROR!')
        ret = p.parse('RANDBETWEEN("a", 2)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#VALUE!')
        ret = p.parse('RANDBETWEEN(2, "a")')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#VALUE!')
        for i in range(1000):
            ret = p.parse('RANDBETWEEN(10; 100)')
            self.assertGreaterEqual(ret['result'], 10)
            self.assertLessEqual(ret['result'], 100)
            self.assertEqual(ret['error'], None)

    def test_int(self):
        p = Parser()
        ret = p.parse('INT(101.001)')
        self.assertEqual(ret['result'], 101)
        self.assertEqual(ret['error'], None)
        ret = p.parse('INT(99.99)')
        self.assertEqual(ret['result'], 99)
        self.assertEqual(ret['error'], None)
        ret = p.parse('INT(0)')
        self.assertEqual(ret['result'], 0)
        self.assertEqual(ret['error'], None)
        ret = p.parse('INT(-10.8)')
        self.assertEqual(ret['result'], -11)
        self.assertEqual(ret['error'], None)
        ret = p.parse('INT(-72.34)')
        self.assertEqual(ret['result'], -73)
        self.assertEqual(ret['error'], None)
        ret = p.parse('INT(-72)')
        self.assertEqual(ret['result'], -72)
        self.assertEqual(ret['error'], None)

    def test_sumifs(self):
        p = Parser(debug=True)
        ret = p.parse('SUMIFS({1;4;5;100}, {1;4;5;100},"<>200")')
        self.assertEqual(ret['result'], 110)
        self.assertEqual(ret['error'], None)
        ret = p.parse('SUMIFS({1;4;5}, {3;5;9},"<7")')
        self.assertEqual(ret['result'], 5)
        self.assertEqual(ret['error'], None)
        ret = p.parse('SUMIFS({1;4;5}, ">1","<5")')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#ERROR!')
        ret = p.parse('SUMIFS({1;4;5}, {1;4;5;100},"<5")')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#VALUE!')
        ret = p.parse('SUMIFS({1;4;5;100}, {1;4;5;100},"<>200", {1;4;300;100},"<100", {2;-3;5;2},">1")')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)

    def test_sumifs_accepts_flat_row_column_and_matrix_ranges(self):
        p = Parser()
        for shape in (lambda values: values,
                      lambda values: [values],
                      lambda values: [[value] for value in values],
                      lambda values: [values[:2], values[2:]],
                      lambda values: (tuple(values[:2]), tuple(values[2:]))):
            sums = shape([10, 20, 30, 40])
            first = shape([1, 2, 3, 4])
            second = shape(['x', 'y', 'x', 'y'])
            p.set_function('SUMDATA', lambda: sums)
            p.set_function('FIRST', lambda: first)
            p.set_function('SECOND', lambda: second)
            for expression, expected in (
                ('SUMIFS(SUMDATA(),FIRST(),">1")', 90),
                ('SUMIFS(SUMDATA(),FIRST(),">1",SECOND(),"x")', 30),
                ('SUMIFS(SUMDATA(),FIRST(),">9")', 0),
            ):
                with self.subTest(sums=sums, expression=expression):
                    self.assertEqual(p.parse(expression), {'result': expected, 'error': None})

    def test_sumifs_accepts_nested_range_callbacks(self):
        for label, values, expected in (
            ('A1:C1', [[1, 2, 3]], 5),
            ('A1:A3', [[1], [2], [3]], 5),
            ('A1:B2', [[1, 2], [3, 4]], 9),
        ):
            p = Parser()
            p.on('callRangeValue', lambda start, end, set_value: set_value(values))
            expression = 'SUMIFS(' + label + ',' + label + ',">1")'
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': expected, 'error': None})

    def test_sumifs_treats_flat_vectors_as_columns(self):
        p = Parser()
        for sums, criteria in (([10, 20, 30], [[1], [2], [3]]),
                               ([[10], [20], [30]], [1, 2, 3]), ([], [])):
            p.set_function('SUMDATA', lambda: sums)
            p.set_function('CRITERIA', lambda: criteria)
            with self.subTest(sums=sums, criteria=criteria):
                self.assertEqual(p.parse('SUMIFS(SUMDATA(),CRITERIA(),">1")'),
                                 {'result': 50 if sums else 0, 'error': None})

    def test_sumifs_rejects_mismatched_and_invalid_range_shapes(self):
        p = Parser()
        for sums, criteria in (
            ([[10, 20]], [[1], [2]]),
            ([[10, 20], [30, 40]], [[1, 2, 3, 4]]),
            ([[10, 20], [30, 40]], [[1], [2]]),
            ([[10], [20, 30]], [[1], [2, 3]]),
            ([10, [20]], [1, [2]]),
            ([[[10]]], [[[1]]]),
            ([10, 20], [[1], [2, 3]]),
        ):
            p.set_function('SUMDATA', lambda: sums)
            p.set_function('CRITERIA', lambda: criteria)
            expression = 'SUMIFS(SUMDATA(),CRITERIA(),">1")'
            with self.subTest(sums=sums, criteria=criteria):
                self.assertEqual(p.parse(expression), {'result': None, 'error': '#VALUE!'})
                self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                 {'result': 99, 'error': None})

    def test_sign(self):
        p = Parser(debug=True)
        ret = p.parse('SIGN(2)')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)
        ret = p.parse('SIGN(-2)')
        self.assertEqual(ret['result'], -1)
        self.assertEqual(ret['error'], None)
        ret = p.parse('SIGN(0)')
        self.assertEqual(ret['result'], 0)
        self.assertEqual(ret['error'], None)
        ret = p.parse('SIGN("a")')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#VALUE!')
