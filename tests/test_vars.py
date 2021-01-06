# -*- coding: utf-8 -*-
import unittest
from hotxlfp import Parser


class TestVars(unittest.TestCase):

    def test_undefined(self):
        p = Parser()
        ret = p.parse("MY_VAR")
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#NAME?')
        ret = p.parse("MY_VAR + 5")
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#NAME?')
        ret = p.parse("5 + MY_VAR")
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#NAME?')
