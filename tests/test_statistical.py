# -*- coding: utf-8 -*-
import unittest
from hotxlfp import Parser


class TestStatistical(unittest.TestCase):

    def test_average(self):
        p = Parser(debug=True)
        ret = p.parse('AVERAGE(1)')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)
        # with an array
        ret = p.parse('AVERAGE({1,2,3})')
        self.assertEqual(ret['result'], 2)
        self.assertEqual(ret['error'], None)

    def test_avedev(self):
        p = Parser(debug=True)
        ret = p.parse('AVEDEV(1)')
        self.assertEqual(ret['result'], 0)
        self.assertEqual(ret['error'], None)
        # with an array
        ret = p.parse('AVEDEV({1;2;3;4})')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)

    def test_averagea(self):
        p = Parser(debug=True)
        ret = p.parse('AVERAGEA(1;"2")')
        self.assertEqual(ret['result'], 1.5)
        self.assertEqual(ret['error'], None)
        ret = p.parse('AVERAGEA(1;"2";TRUE;TRUE)')
        self.assertEqual(ret['result'], 1.25)
        self.assertEqual(ret['error'], None)

    def test_averagif(self):
        p = Parser(debug=True)
        ret = p.parse('AVERAGEIF({1;2;3;4};">2")')
        self.assertEqual(ret['result'], 3.5)
        self.assertEqual(ret['error'], None)
        ret = p.parse('AVERAGEIF({1;2;3;4};">2";{4;3;2;1})')
        self.assertEqual(ret['result'], 1.5)
        self.assertEqual(ret['error'], None)

    def test_count(self):
        p = Parser(debug=True)
        ret = p.parse('COUNT(1;"2")')
        self.assertEqual(ret['result'], 2)
        self.assertEqual(ret['error'], None)
        # with an array
        ret = p.parse('COUNT({1;2;3;4})')
        self.assertEqual(ret['result'], 4)
        self.assertEqual(ret['error'], None)

    def test_counta(self):
        p = Parser(debug=True)
        ret = p.parse('COUNTA(1;"2")')
        self.assertEqual(ret['result'], 2)
        self.assertEqual(ret['error'], None)
        # with an array
        ret = p.parse('COUNTA({1;2;3;""})')
        self.assertEqual(ret['result'], 3)
        self.assertEqual(ret['error'], None)
        ret = p.parse('COUNTA(1;2;3;NULL)')
        self.assertEqual(ret['result'], 3)
        self.assertEqual(ret['error'], None)

    def test_countblank(self):
        p = Parser(debug=True)
        ret = p.parse('COUNTBLANK(1;"2")')
        self.assertEqual(ret['result'], 0)
        self.assertEqual(ret['error'], None)
        ret = p.parse('COUNTBLANK(1;2;3;"")')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)
        ret = p.parse('COUNTBLANK(1;2;3;NULL)')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)
        # with an array
        ret = p.parse('COUNTBLANK({1;2;3;4})')
        self.assertEqual(ret['result'], 0)
        self.assertEqual(ret['error'], None)
        ret = p.parse('COUNTBLANK({1;2;3;""})')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)

    def test_countif(self):
        p = Parser(debug=True)
        ret = p.parse('COUNTIF({1;3};">2")')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)
        ret = p.parse('COUNTIF({"foo";"bar"};"foo")')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)
        ret = p.parse('COUNTIF({"foo bar";"baz"};"foo bar")')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)
        ret = p.parse(u'COUNTIF({"áà ãâä";"baz"}; "áà ãâä")')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)
        ret = p.parse(u'COUNTIF({"áà ã,â,ä";"baz"}; "áà ã,â,ä")')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)
        ret = p.parse(u'COUNTIF({"áà ã(â)ä";"baz"}; "áà ã(â)ä")')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)

    def test_max(self):
        p = Parser(debug=True)
        ret = p.parse('MAX({1;3};4)')
        self.assertEqual(ret['result'], 4)
        self.assertEqual(ret['error'], None)
        ret = p.parse('MAX({1;2;3})')
        self.assertEqual(ret['result'], 3)
        self.assertEqual(ret['error'], None)

    def test_min(self):
        p = Parser(debug=True)
        ret = p.parse('MIN({1;3};0)')
        self.assertEqual(ret['result'], 0)
        self.assertEqual(ret['error'], None)
        ret = p.parse('MIN({1;2;3})')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)

    def test_var(self):
        p = Parser(debug=True)
        ret = p.parse('VAR.S({1345;1301;1368;1322;1310;1370;1318;1350;1303;1299})')
        self.assertTrue(str(ret['result']).startswith('754.2'))
        self.assertEqual(ret['error'], None)
        ret = p.parse('VAR.P({1345;1301;1368;1322;1310;1370;1318;1350;1303;1299})')
        self.assertEqual(ret['result'], 678.84)
        self.assertEqual(ret['error'], None)

    def test_stdev(self):
        p = Parser(debug=True)
        ret = p.parse('STDEV.S({1345;1301;1368;1322;1310;1370;1318;1350;1303;1299})')
        self.assertTrue(str(ret['result']).startswith('27.46'))
        self.assertEqual(ret['error'], None)
        ret = p.parse('STDEV.P({1345;1301;1368;1322;1310;1370;1318;1350;1303;1299})')
        self.assertTrue(str(ret['result']).startswith('26.05'))
        self.assertEqual(ret['error'], None)

    def test_median(self):
        p = Parser(debug=True)
        ret = p.parse('MEDIAN({1;2;3;4;5;6})')
        self.assertEqual(ret['result'], 3.5)
        self.assertEqual(ret['error'], None)
        ret = p.parse('MEDIAN({1;2;3;4;5})')
        self.assertEqual(ret['result'], 3)
        self.assertEqual(ret['error'], None)
        ret = p.parse('MEDIAN({1;2;3;4;5;"lala"})')
        self.assertEqual(ret['result'], 3)
        self.assertEqual(ret['error'], None)

    def test_mode(self):
        p = Parser(debug=True)
        ret = p.parse('MODE({5.6;4;4;3;2;4})')
        self.assertEqual(ret['result'], 4)
        self.assertEqual(ret['error'], None)
