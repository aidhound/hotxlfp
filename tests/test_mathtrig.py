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

    def test_acot(self):
        p = Parser(debug=True)
        ret = p.parse('ACOT(2)')
        self.assertTrue(str(ret['result']).startswith('0.4636'))
        self.assertEqual(ret['error'], None)
        ret = p.parse('ACOT(1/0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')

    def test_acoth(self):
        p = Parser(debug=True)
        ret = p.parse('ACOTH(6)')
        self.assertTrue(str(ret['result']).startswith('0.168'))
        self.assertEqual(ret['error'], None)
        ret = p.parse('ACOTH(1/0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')

    def test_sin(self):
        p = Parser(debug=True)
        ret = p.parse('SIN(PI()/2)')
        self.assertTrue(['result'], 1)
        self.assertEqual(ret['error'], None)
        ret = p.parse('SIN(1/0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')

    def test_sinh(self):
        p = Parser(debug=True)
        ret = p.parse('2.868*SINH(0.0342*1.03)')
        self.assertTrue(['result'], 0.1010491)
        self.assertEqual(ret['error'], None)
        ret = p.parse('SINH(1/0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')

    def test_asin(self):
        p = Parser(debug=True)
        ret = p.parse('ASIN(-0.5)')
        self.assertTrue(['result'], -0.523598776)
        self.assertEqual(ret['error'], None)
        ret = p.parse('ASIN(1/0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')

    def test_asinh(self):
        p = Parser(debug=True)
        ret = p.parse('ASINH(-2.5)')
        self.assertTrue(['result'], -1.647231146)
        self.assertEqual(ret['error'], None)
        ret = p.parse('ASINH(1/0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')

    def test_cos(self):
        p = Parser(debug=True)
        ret = p.parse('COS(0)')
        self.assertTrue(['result'], 1)
        self.assertEqual(ret['error'], None)
        ret = p.parse('COS(1/0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')

    def test_cosh(self):
        p = Parser(debug=True)
        ret = p.parse('COSH(4)')
        self.assertTrue(['result'], 27.308233)
        self.assertEqual(ret['error'], None)
        ret = p.parse('COSH(1/0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')

    def test_tan(self):
        p = Parser(debug=True)
        ret = p.parse('TAN(45*PI()/180)')
        self.assertTrue(['result'], 1)
        self.assertEqual(ret['error'], None)
        ret = p.parse('TAN(1/0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')

    def test_tanh(self):
        p = Parser(debug=True)
        ret = p.parse('TANH(0.5)')
        self.assertTrue(['result'], 0.462117)
        self.assertEqual(ret['error'], None)
        ret = p.parse('TANH(1/0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')

    def test_atan(self):
        p = Parser(debug=True)
        ret = p.parse('ATAN(1)*180/PI()')
        self.assertTrue(['result'], 1)
        self.assertEqual(ret['error'], None)
        ret = p.parse('ATAN(1/0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')

    def test_atan2(self):
        p = Parser(debug=True)
        ret = p.parse('ATAN2(1, 1)')
        self.assertTrue(['result'], 0.785398163)
        self.assertEqual(ret['error'], None)

    def test_atanh(self):
        p = Parser(debug=True)
        ret = p.parse('ATANH(0.76159416)')
        self.assertTrue(['result'], 1.00000001)
        self.assertEqual(ret['error'], None)
        ret = p.parse('ATANH(1/0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')

    def test_sqrt(self):
        p = Parser(debug=True)
        ret = p.parse('SQRT(16)')
        self.assertTrue(['result'], 4)
        self.assertEqual(ret['error'], None)
        ret = p.parse('SQRT(1/0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')

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

    def test_log(self):
        p = Parser(debug=True)
        ret = p.parse('LOG(10)')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)
        ret = p.parse('LOG(8, 2)')
        self.assertEqual(ret['result'], 3)
        self.assertEqual(ret['error'], None)

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
