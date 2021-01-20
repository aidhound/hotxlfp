# -*- coding: utf-8 -*-
import unittest
import math
from hotxlfp import Parser
import datetime


class TestDateAndTime(unittest.TestCase):

    def test_date(self):
        p = Parser(debug=True)
        ret = p.parse('DATE(2020;10;12)')
        self.assertEqual(ret['result'], datetime.datetime(2020, 10, 12))
        self.assertEqual(ret['error'], None)
        ret = p.parse('DATE(95;10;12)')
        self.assertEqual(ret['result'], datetime.datetime(1995, 10, 12))
        self.assertEqual(ret['error'], None)

    def test_datevalue(self):
        p = Parser(debug=True)
        ret = p.parse('DATEVALUE("8/22/2011")')
        self.assertEqual(ret['result'], 40777)
        self.assertEqual(ret['error'], None)
        ret = p.parse('DATEVALUE("22-MAY-2011")')
        self.assertEqual(ret['result'], 40685)
        self.assertEqual(ret['error'], None)
        ret = p.parse('DATEVALUE("2011/02/23")')
        self.assertEqual(ret['result'], 40597)
        self.assertEqual(ret['error'], None)

    def test_year(self):
        p = Parser(debug=True)
        ret = p.parse('YEAR("2020-10-12 10:04:11")')
        self.assertEqual(ret['result'], 2020)
        self.assertEqual(ret['error'], None)
        ret = p.parse('YEAR(41193)')  # 2012-10-11 in serial
        self.assertEqual(ret['result'], 2012)
        self.assertEqual(ret['error'], None)
        ret = p.parse('YEAR(1/0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')

    def test_month(self):
        p = Parser(debug=True)
        ret = p.parse('MONTH("2020-10-12 10:04:11")')
        self.assertEqual(ret['result'], 10)
        self.assertEqual(ret['error'], None)
        ret = p.parse('MONTH(1/0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')

    def test_day(self):
        p = Parser(debug=True)
        ret = p.parse('DAY("2020-10-12 10:04:11")')
        self.assertEqual(ret['result'], 12)
        self.assertEqual(ret['error'], None)
        ret = p.parse('DAY(1/0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')

    def test_hour(self):
        p = Parser(debug=True)
        ret = p.parse('HOUR("10:04:11")')
        self.assertEqual(ret['result'], 10)
        self.assertEqual(ret['error'], None)
        ret = p.parse('HOUR(1/0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')

    def test_minute(self):
        p = Parser(debug=True)
        ret = p.parse('MINUTE("10:04:11")')
        self.assertEqual(ret['result'], 4)
        self.assertEqual(ret['error'], None)
        ret = p.parse('MINUTE(1/0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')

    def test_second(self):
        p = Parser(debug=True)
        ret = p.parse('SECOND("10:04:11")')
        self.assertEqual(ret['result'], 11)
        self.assertEqual(ret['error'], None)
        ret = p.parse('SECOND(1/0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')

    def test_today(self):
        today = datetime.date.today()
        today_datetime = datetime.datetime(today.year, today.month, today.day)
        p = Parser(debug=True)
        ret = p.parse('YEAR(TODAY())')
        self.assertEqual(ret['result'], today.year)
        self.assertEqual(ret['error'], None)
        ret = p.parse('MONTH(TODAY())')
        self.assertEqual(ret['result'], today.month)
        self.assertEqual(ret['error'], None)
        ret = p.parse('DAY(TODAY())')
        self.assertEqual(ret['result'], today.day)
        self.assertEqual(ret['error'], None)
        ret = p.parse('HOUR(TODAY())')
        self.assertEqual(ret['result'], 0)
        self.assertEqual(ret['error'], None)
        ret = p.parse('MINUTE(TODAY())')
        self.assertEqual(ret['result'], 0)
        self.assertEqual(ret['error'], None)
        ret = p.parse('SECOND(TODAY())')
        self.assertEqual(ret['result'], 0)
        self.assertEqual(ret['error'], None)

    def test_days(self):
        p = Parser(debug=True)
        ret = p.parse('DAYS("3/15/11","2/1/11")')
        self.assertEqual(ret['result'], 42)
        self.assertEqual(ret['error'], None)
        ret = p.parse('DAYS("foo","2/1/11")')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#VALUE!')
        ret = p.parse('DAYS(TODAY(),TODAY()-1)')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)
