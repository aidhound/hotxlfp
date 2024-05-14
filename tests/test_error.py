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


    def test_wrong_syntax(self):
        p = Parser()
        ret = p.parse('2(6+2)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#ERROR!')
        ret = p.parse('2:5')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#ERROR!')


    def test_error_imaginary(self):
        p = Parser()
        ret = p.parse('IMAGINARY("#ERROR!")')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#ERROR!')
        ret = p.parse('IMAGINARY("2/0")')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#ERROR!')
        ret = p.parse('IMAGINARY("")')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#ERROR!')
        ret = p.parse('IMAGINARY("#N/A!")')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#ERROR!')
        ret = p.parse('IMAGINARY("#DIV/0!")')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#ERROR!')

    def test_error_real(self):
        p = Parser()
        ret = p.parse('IMREAL("#ERROR!")')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#ERROR!')
        ret = p.parse('IMREAL("2/0")')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#ERROR!')
        ret = p.parse('IMREAL("")')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#ERROR!')
        ret = p.parse('IMREAL("#N/A!")')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#ERROR!')
        ret = p.parse('IMREAL("#DIV/0!")')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#ERROR!')