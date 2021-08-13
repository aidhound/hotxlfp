import unittest
from hotxlfp import Parser



class TestParser(unittest.TestCase):

    def test_parser_within_parser(self):

        def parse(formula):
            parser = Parser(debug=True)
            result = parser.parse(formula)
            return result['result']

        parser = Parser(debug=True)
        parser.set_function('EVAL', parse)
        first_result = parser.parse('EVAL("1+1")')['result']
        second_result = parser.parse('EVAL("1+1")')['result']
        self.assertEqual(first_result, second_result)
