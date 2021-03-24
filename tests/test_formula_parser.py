import unittest

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
        func = p.parse('A1')['result']
        result = func({'A1': 4})
        self.assertEqual(result, 4)


if __name__ == '__main__':
    unittest.main()
