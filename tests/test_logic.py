# -*- coding: utf-8 -*-
import unittest
from hotxlfp import Parser


class TestLogic(unittest.TestCase):

    def test_and(self):
        p = Parser(debug=True)
        ret = p.parse('AND(TRUE,TRUE, FALSE)')
        self.assertEqual(ret['result'], False)
        self.assertEqual(ret['error'], None)
        ret = p.parse('AND(TRUE,TRUE, TRUE)')
        self.assertEqual(ret['result'], True)
        self.assertEqual(ret['error'], None)
        ret = p.parse('AND(FALSE)')
        self.assertEqual(ret['result'], False)
        self.assertEqual(ret['error'], None)
        ret = p.parse('AND(TRUE)')
        self.assertEqual(ret['result'], True)
        self.assertEqual(ret['error'], None)

    def test_if(self):
        p = Parser(debug=True)
        ret = p.parse('IF(TRUE,1,3)')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)
        ret = p.parse('IF(FALSE,1,3)')
        self.assertEqual(ret['result'], 3)
        self.assertEqual(ret['error'], None)
        ret = p.parse('IF(,,)=0')
        self.assertEqual(ret['result'], True)
        self.assertEqual(ret['error'], None)
        ret = p.parse('IF(,,)=""')
        self.assertEqual(ret['result'], True)
        self.assertEqual(ret['error'], None)
        ret = p.parse('IF(,,)=B3')
        self.assertEqual(ret['result'], True)
        self.assertEqual(ret['error'], None)

    def test_iferror(self):
        p = Parser(debug=True)
        ret = p.parse('IFERROR(1/0,1)')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)
        ret = p.parse('IFERROR("notme",1)')
        self.assertEqual(ret['result'], "notme")
        self.assertEqual(ret['error'], None)

    def test_ifna(self):
        p = Parser(debug=True)
        ret = p.parse('IFNA(1/0,1)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')
        ret = p.parse('IFNA(NA(),1)')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)
        ret = p.parse('IFNA(2,1)')
        self.assertEqual(ret['result'], 2)
        self.assertEqual(ret['error'], None)

    def test_ifs(self):
        p = Parser(debug=True)
        ret = p.parse('IFS(1=2,2,2=2,3)')
        self.assertEqual(ret['result'], 3)
        self.assertEqual(ret['error'], None)
        ret = p.parse('IFS(1=2,2,2=3,3, TRUE,4)')
        self.assertEqual(ret['result'], 4)
        self.assertEqual(ret['error'], None)
        ret = p.parse('IFS(1=2,2,2=3,3, FALSE,4)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#N/A')

    def test_switch(self):
        p = Parser(debug=True)
        ret = p.parse('SWITCH(2,2,"lele",3, "lili")')
        self.assertEqual(ret['result'], 'lele')
        self.assertEqual(ret['error'], None)
        ret = p.parse('SWITCH(4,2,"lele",3, "lili")')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#N/A')
        ret = p.parse('SWITCH(4,2,"lele",3, "lili","default")')
        self.assertEqual(ret['result'], 'default')
        self.assertEqual(ret['error'], None)
        ret = p.parse('SWITCH(1)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#N/A')

    def test_not(self):
        p = Parser(debug=True)
        ret = p.parse('NOT(TRUE())')
        self.assertEqual(ret['result'], False)
        self.assertEqual(ret['error'], None)
        ret = p.parse('NOT(FALSE())')
        self.assertEqual(ret['result'], True)
        self.assertEqual(ret['error'], None)

    def test_or(self):
        p = Parser(debug=True)
        ret = p.parse('OR(TRUE,TRUE, FALSE)')
        self.assertEqual(ret['result'], True)
        self.assertEqual(ret['error'], None)
        ret = p.parse('OR(TRUE,TRUE, TRUE)')
        self.assertEqual(ret['result'], True)
        self.assertEqual(ret['error'], None)
        ret = p.parse('OR(FALSE)')
        self.assertEqual(ret['result'], False)
        self.assertEqual(ret['error'], None)
        ret = p.parse('OR(TRUE)')
        self.assertEqual(ret['result'], True)
        self.assertEqual(ret['error'], None)

    def test_xor(self):
        p = Parser(debug=True)
        ret = p.parse('XOR(3>0,2<9)')
        self.assertEqual(ret['result'], False)
        self.assertEqual(ret['error'], None)
        ret = p.parse('XOR(3>12,4>6)')
        self.assertEqual(ret['result'], False)
        self.assertEqual(ret['error'], None)
        ret = p.parse('XOR(3>12,4>2)')
        self.assertEqual(ret['result'], True)
        self.assertEqual(ret['error'], None)
