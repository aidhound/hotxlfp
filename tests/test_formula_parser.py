import unittest

import numpy as np
from hotxlfp import Parser


class TestFormulaParser(unittest.TestCase):
    def test_plus(self):
        p = Parser(debug=True)
        func = p.parse('A + B + C')['result']
        result = func({'A': 3.43, 'B': 5.23, 'C': 6.34})
        self.assertEqual(result, 15)

        p = Parser(debug=True)
        func = p.parse('SUM(A, B, SUM(3, C)) + 5')['result']
        result = func({'A': 4, 'B': 2, 'C': 6})
        self.assertEqual(result, 20)

        p = Parser(debug=True)
        func = p.parse('SUM(A,, B, SUM(3, C)) + 5')['result']
        result = func({'A': 4, 'B': 2, 'C': 6})
        self.assertEqual(result, 20)

        p = Parser(debug=True)
        func = p.parse('SUM(A;; B; SUM(3, C)) + 5')['result']
        result = func({'A': 4, 'B': 2, 'C': 6})
        self.assertEqual(result, 20)

        p = Parser(debug=True)
        func = p.parse('MAX(A;; B; 100) + MIN(A, B, C)')['result']
        result = func({'A': 4.234, 'B': 223, 'C': 6})
        self.assertEqual(result, 223 + 4.234)

    def test_sqrt(self):
        p = Parser(debug=True)
        func = p.parse('SQRT(A)')['result']
        result = func({'A': 16.0})
        self.assertEqual(result, 4)

        p = Parser(debug=True)
        func = p.parse('SQRT(100)')['result']
        result = func({})
        self.assertEqual(result, 10)

    def test_string(self):
        p = Parser(debug=True)
        func = p.parse('CONCAT(A, B) & C')['result']
        result = func({'A': 'testing', 'B': 'abc', 'C': 5})
        self.assertEqual(result, 'testingabc5')

        p = Parser(debug=True)
        func = p.parse('CONCAT(A, B) & MAX(D, 50) & C')['result']
        result = func({'A': 'testing', 'B': 'abc', 'C': 5, 'D': 100})
        self.assertEqual(result, 'testingabc1005')

        p = Parser(debug=True)
        func = p.parse('A & B')['result']
        result = func({'A': 'testing', 'B': 'abc'})
        self.assertEqual(result, 'testingabc')

    def test_if(self):
        p = Parser(debug=True)
        func = p.parse('IF(A < B, C, D)')['result']
        result = func({'A': 2, 'B': 3, 'C': 4, 'D': 5})
        self.assertEqual(result, 4)

        p = Parser(debug=True)
        func = p.parse('IF(A > B, C, D)')['result']
        result = func({'A': 2, 'B': 3, 'C': 4, 'D': 5})
        self.assertEqual(result, 5)

    def test_logical(self):
        p = Parser(debug=True)
        func = p.parse('100 > 10.0')['result']
        result = func({})
        self.assertEqual(result, True)

        p = Parser(debug=True)
        func = p.parse('A > 10.0')['result']
        result = func({'A': 100})
        self.assertEqual(result, True)

    def test_variable_name(self):
        p = Parser(debug=True)
        func = p.parse('a1')['result']
        result = func({'a1': 5})
        self.assertEqual(result, 5)

    def test_array_add(self):
        p = Parser(debug=True)
        func = p.parse('a1 + 2')['result']
        result = func({'a1': np.array([4])})
        self.assertEqual(result, [6])

        func = p.parse('a1 + a1')['result']
        result = func({'a1': np.array([4, 5])})
        assert (result == [8, 10]).all()

    def test_array_if(self):
        p = Parser(debug=True)
        func = p.parse('IF(a1 + a1 < 4, 1, 2)')['result']
        result = func({'a1': np.array([1, 4])})
        assert (result == [1, 2]).all()

        p = Parser(debug=True)
        func = p.parse('IF(3 < 4, a1, 2)')['result']
        result = func({'a1': np.array([1, 2])})
        assert (result == [1, 2]).all()

    def test_array_if_exp(self):
        p = Parser(debug=True)
        func = p.parse('IF(((((a1+2)/3)*EXP(5)))<0.11, ' +
                       '(a1/2.2222),((( a1+9999)/33)*EXP(3)))')['result']
        input_vals = [1, 123, -432]
        answer = [
            6086.52634,
            6160.781962,
            -194.401944,
        ]
        result = func({'a1': np.array(input_vals)})
        assert(np.abs(result - np.array(answer)) < 0.00001).all()


if __name__ == '__main__':
    unittest.main()
