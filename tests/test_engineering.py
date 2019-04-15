# -*- coding: utf-8 -*-
import unittest
import math
from hotxlfp import Parser


class TestEngineering(unittest.TestCase):

    def test_hex2dec(self):
        p = Parser(debug=True)
        ret = p.parse('HEX2DEC("A5")')
        self.assertEqual(ret['result'], 165)
        self.assertEqual(ret['error'], None)
        ret = p.parse('HEX2DEC("FFFFFFFF5B")')
        self.assertEqual(ret['result'], -165)
        self.assertEqual(ret['error'], None)
        ret = p.parse('HEX2DEC("3DA408B9")')
        self.assertEqual(ret['result'], 1034160313)
        self.assertEqual(ret['error'], None)
        ret = p.parse('HEX2DEC("ZZZ")')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#VALUE!')

    def test_dec2hex(self):
        p = Parser(debug=True)
        ret = p.parse('DEC2HEX(100, 4)')
        self.assertEqual(ret['result'], '0064')
        self.assertEqual(ret['error'], None)
        ret = p.parse('DEC2HEX(-54)')
        self.assertEqual(ret['result'], 'FFFFFFFFCA')
        self.assertEqual(ret['error'], None)
        ret = p.parse('DEC2HEX(28)')
        self.assertEqual(ret['result'], '1C')
        self.assertEqual(ret['error'], None)
        ret = p.parse('DEC2HEX(64,1)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#NUM!')

    def test_delta(self):
        p = Parser(debug=True)
        ret = p.parse('DELTA(5, 4)')
        self.assertEqual(ret['result'], 0)
        self.assertEqual(ret['error'], None)
        ret = p.parse('DELTA(5, 5)')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)
        ret = p.parse('DELTA(0.5, 0)')
        self.assertEqual(ret['result'], 0)
        self.assertEqual(ret['error'], None)

    def test_complex(self):
        p = Parser(debug=True)
        ret = p.parse('COMPLEX(3, 5)')
        self.assertEqual(ret['result'], complex(3, 5))
        self.assertEqual(ret['error'], None)
