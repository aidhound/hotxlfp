# -*- coding: utf-8 -*-
import unittest
from hotxlfp import Parser


class TestOperators(unittest.TestCase):

    def test_plus(self):
        p = Parser(debug=True)
        ret = p.parse('1 + 1')
        self.assertEqual(ret['result'], 2)
        self.assertEqual(ret['error'], None)
        ret = p.parse('1 + "lele"')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#VALUE!')

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

    def test_logic(self):
        p = Parser(debug=True)
        ret = p.parse('"a" > 2')
        self.assertEqual(ret['result'], True)
        self.assertEqual(ret['error'], None)
        ret = p.parse('"a" < 2')
        self.assertEqual(ret['result'], False)
        self.assertEqual(ret['error'], None)
        ret = p.parse('3 = 2')
        self.assertEqual(ret['result'], False)
        self.assertEqual(ret['error'], None)
        ret = p.parse('3 <> 2')
        self.assertEqual(ret['result'], True)
        self.assertEqual(ret['error'], None)
        ret = p.parse('3 >= 2')
        self.assertEqual(ret['result'], True)
        self.assertEqual(ret['error'], None)
        ret = p.parse('3 <= 2')
        self.assertEqual(ret['result'], False)
        self.assertEqual(ret['error'], None)
