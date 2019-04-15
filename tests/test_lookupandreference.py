# -*- coding: utf-8 -*-
import unittest
from hotxlfp import Parser


class TestLookupAndReference(unittest.TestCase):

    def test_choose(self):
        p = Parser(debug=True)
        ret = p.parse('CHOOSE(1,1,3)')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)
        ret = p.parse('CHOOSE(2,1,3)')
        self.assertEqual(ret['result'], 3)
        self.assertEqual(ret['error'], None)
        ret = p.parse('CHOOSE(255,1,3)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#VALUE!')
        ret = p.parse('CHOOSE(3,1,3)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#VALUE!')
        ret = p.parse('CHOOSE(1)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#N/A')

    def test_match(self):
        p = Parser(debug=True)
        ret = p.parse('MATCH(39,{25,38,40,41},1)')
        self.assertEqual(ret['result'], 2)
        self.assertEqual(ret['error'], None)
        ret = p.parse('MATCH("f?o",{"eee","aaa","foa","foo"},0)')
        self.assertEqual(ret['result'], 4)
        self.assertEqual(ret['error'], None)
        ret = p.parse('MATCH(39,{25,38,40,41},-1)')
        self.assertEqual(ret['result'], 3)
        self.assertEqual(ret['error'], None)
