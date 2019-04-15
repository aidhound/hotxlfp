# -*- coding: utf-8 -*-
import unittest
from hotxlfp.grammarparser import lexer


class TestLexer(unittest.TestCase):

    def test_function(self):
        lex = lexer.build()
        lex.input('ACOTH("foo")')
        expected_token_types = ['FUNCTION', 'LPAREN', 'STRING', 'RPAREN']
        for i, t in enumerate(lex):
            self.assertEqual(t.type, expected_token_types[i])
