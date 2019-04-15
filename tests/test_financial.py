# -*- coding: utf-8 -*-
import unittest
import math
from hotxlfp import Parser


class TestFinancial(unittest.TestCase):

    def test_pv(self):
        p = Parser(debug=True)
        ret = p.parse('PV(8%/12, 12*20, 500,,0)')
        self.assertEqual(round(ret['result'], 2), -59777.15)
        self.assertEqual(ret['error'], None)
        ret = p.parse('PV(8%/12, 12*20, 500)')
        self.assertEqual(round(ret['result'], 2), -59777.15)
        self.assertEqual(ret['error'], None)
        ret = p.parse('PV(1/0, 12*20, 500)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#VALUE!')
        ret = p.parse('PV(0, 12*20, 500)')
        self.assertEqual(ret['result'], -120000)
