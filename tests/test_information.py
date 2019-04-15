# -*- coding: utf-8 -*-

import unittest
from hotxlfp import Parser


class TestStatistical(unittest.TestCase):

    def test_error_type(self):
        p = Parser(debug=True)
        ret = p.parse('ERROR.TYPE(1/0)')
        self.assertEqual(ret['result'], 2)
        self.assertEqual(ret['error'], None)

    def test_iserr(self):
        p = Parser(debug=True)
        ret = p.parse('ISERR(1/0)')
        self.assertEqual(ret['result'], True)
        self.assertEqual(ret['error'], None)

    def test_iserror(self):
        p = Parser(debug=True)
        ret = p.parse('ISERROR(1/0)')
        self.assertEqual(ret['result'], True)
        self.assertEqual(ret['error'], None)
        p = Parser(debug=True)
        ret = p.parse('ISERROR(1/2)')
        self.assertEqual(ret['result'], False)
        self.assertEqual(ret['error'], None)

    def test_iseven(self):
        p = Parser(debug=True)
        ret = p.parse('ISEVEN(1)')
        self.assertEqual(ret['result'], False)
        self.assertEqual(ret['error'], None)
        ret = p.parse('ISEVEN(-1)')
        self.assertEqual(ret['result'], False)
        self.assertEqual(ret['error'], None)
        ret = p.parse('ISEVEN(2)')
        self.assertEqual(ret['result'], True)
        self.assertEqual(ret['error'], None)
        ret = p.parse('ISEVEN(-2)')
        self.assertEqual(ret['result'], True)
        self.assertEqual(ret['error'], None)
        ret = p.parse('ISEVEN(1000)')
        self.assertEqual(ret['result'], True)
        self.assertEqual(ret['error'], None)
        ret = p.parse('ISEVEN("A")')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#VALUE!')
        ret = p.parse('ISEVEN(2.21)')
        self.assertEqual(ret['result'], True)
        self.assertEqual(ret['error'], None)

    def test_isodd(self):
        p = Parser(debug=True)
        ret = p.parse('ISODD(1)')
        self.assertEqual(ret['result'], True)
        self.assertEqual(ret['error'], None)
        ret = p.parse('ISODD(-1)')
        self.assertEqual(ret['result'], True)
        self.assertEqual(ret['error'], None)
        ret = p.parse('ISODD(2)')
        self.assertEqual(ret['result'], False)
        self.assertEqual(ret['error'], None)
        ret = p.parse('ISODD(-2)')
        self.assertEqual(ret['result'], False)
        self.assertEqual(ret['error'], None)
        ret = p.parse('ISODD(1000)')
        self.assertEqual(ret['result'], False)
        self.assertEqual(ret['error'], None)
        ret = p.parse('ISODD("A")')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#VALUE!')
        ret = p.parse('ISODD(2.21)')
        self.assertEqual(ret['result'], False)
        self.assertEqual(ret['error'], None)

    def test_istext(self):
        p = Parser(debug=True)
        ret = p.parse('ISTEXT("foo")')
        self.assertEqual(ret['result'], True)
        self.assertEqual(ret['error'], None)
        ret = p.parse('ISTEXT(NA())')
        self.assertEqual(ret['result'], False)
        self.assertEqual(ret['error'], None)
        ret = p.parse('ISTEXT(1)')
        self.assertEqual(ret['result'], False)
        self.assertEqual(ret['error'], None)

    def test_isna(self):
        p = Parser(debug=True)
        ret = p.parse('ISNA(NA())')
        self.assertEqual(ret['result'], True)
        self.assertEqual(ret['error'], None)
        ret = p.parse('ISNA(1/0)')
        self.assertEqual(ret['result'], False)
        self.assertEqual(ret['error'], None)
