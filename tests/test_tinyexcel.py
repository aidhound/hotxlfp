# -*- coding: utf-8 -*-
import unittest
from hotxlfp import Parser


class TestTinyExcel(unittest.TestCase):

    def test_tinyexcel(self):
        # Our tiny excel table and functions to access it
        table = [
            [0, None, None, None],
            [1, None, None, None],
            [2, None, None, None],
            [3, None, None, None],
            [4, None, None, None]
        ]

        def cellvalue(cell, valsetter):
            valsetter(table[cell.row.index][cell.col.index])

        def rangevalue(start, end, valsetter):
            result = []
            for i in range(start.row.index, end.row.index + 1):
                result.append(table[i][start.col.index: end.col.index + 1])
            valsetter(result)

        # Make and setup our parser
        p = Parser(debug=True)
        p.on('callCellValue', cellvalue)
        p.on('callRangeValue', rangevalue)
        # Check a cells is blank
        res = p.parse('ISBLANK(B1)')
        self.assertEqual(res['result'], True)
        self.assertEqual(res['error'], None)
        # Let's try getting a range
        res = p.parse('A1:A5')
        self.assertEqual(res['result'], [[0], [1], [2], [3], [4]])
        self.assertEqual(res['error'], None)
        # Now use a formula on it
        res = p.parse('SUM(A1:A5)')
        self.assertEqual(res['result'], 10)
        self.assertEqual(res['error'], None)
        res = p.parse('SUM(A5:A1)')
        self.assertEqual(res['result'], 10)
        self.assertEqual(res['error'], None)
        # Now lets try a custom function

        def triple(x):
            return x * 3
        p.set_function('TRIPLE', triple)
        res = p.parse('TRIPLE(A4)')
        self.assertEqual(res['result'], 9)
        self.assertEqual(res['error'], None)
        # And a custom variable
        p.set_variable('x', 2)
        res = p.parse('TRIPLE(x)')
        self.assertEqual(res['result'], 6)
        self.assertEqual(res['error'], None)

        # Sanity check
        self.assertEqual(p.get_function('TRIPLE'), triple)
        self.assertEqual(p.get_variable('x'), 2)
