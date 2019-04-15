# -*- coding: utf-8 -*-
import unittest
import math
from hotxlfp import Parser


class TestText(unittest.TestCase):

    def test_char(self):
        p = Parser(debug=True)
        ret = p.parse('CHAR(65)')
        self.assertEqual(ret['result'], 'A')
        self.assertEqual(ret['error'], None)
        ret = p.parse('CHAR(33)')
        self.assertEqual(ret['result'], '!')
        self.assertEqual(ret['error'], None)

    def test_code(self):
        p = Parser(debug=True)
        ret = p.parse('CODE("A")')
        self.assertEqual(ret['result'], 65)
        self.assertEqual(ret['error'], None)
        ret = p.parse('CODE("!")')
        self.assertEqual(ret['result'], 33)
        self.assertEqual(ret['error'], None)

    def test_clean(self):
        p = Parser(debug=True)
        ret = p.parse('CLEAN(CHAR(9)&"Monthly report"&CHAR(10))')
        self.assertEqual(ret['result'], 'Monthly report')
        self.assertEqual(ret['error'], None)

    def test_concatenate(self):
        p = Parser(debug=True)
        ret = p.parse('CONCAT("The"," ","sun"," ","will"," ","come"," ","up"," ","tomorrow.")')
        self.assertEqual(ret['result'], 'The sun will come up tomorrow.')
        self.assertEqual(ret['error'], None)

    def test_lower(self):
        p = Parser(debug=True)
        ret = p.parse('LOWER("aBcDe")')
        self.assertEqual(ret['result'], 'abcde')
        self.assertEqual(ret['error'], None)

    def test_upper(self):
        p = Parser(debug=True)
        ret = p.parse('UPPER("aBcDe")')
        self.assertEqual(ret['result'], 'ABCDE')
        self.assertEqual(ret['error'], None)

    def test_proper(self):
        p = Parser(debug=True)
        ret = p.parse('PROPER("aBcDe")')
        self.assertEqual(ret['result'], 'Abcde')
        self.assertEqual(ret['error'], None)
        ret = p.parse('PROPER("76budGet")')
        self.assertEqual(ret['result'], '76Budget')
        self.assertEqual(ret['error'], None)
