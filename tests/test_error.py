# -*- coding: utf-8 -*-
import unittest
from hotxlfp import Parser


class TestError(unittest.TestCase):
    """ Stuff that should cause errors """

    def test_div_zero(self):
        p = Parser()
        ret = p.parse('2/0')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')
        ret = p.parse('SUM(2/0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')
        ret = p.parse('SUM(1; 2/0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')
        ret = p.parse('SUM(2/0; 1)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')

