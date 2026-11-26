# -*- coding: utf-8 -*-
import unittest
import math
from hotxlfp import Parser
import datetime
from hotxlfp.formulas import error
from hotxlfp.formulas import utils


class TestDateAndTime(unittest.TestCase):

    def test_time_keeps_datetime_results_and_fractional_day_identity(self):
        p = Parser()
        for expression, expected in (
            ('TIME(0,0,0)', datetime.datetime(1899, 12, 31)),
            ('TIME(12,0,0)', datetime.datetime(1899, 12, 31, 12)),
            ('TIME(0,0,0)=0', True), ('TIME(12,0,0)=0.5', True),
            ('TIME(0,0,1)=1/86400', True),
            ('TIME(12,0,0)-TIME(0,0,0)', 0.5),
            ('TIME(12,0,0)+1', datetime.datetime(1900, 1, 1, 12)),
            ('HOUR(TIME(12,0,0))', 12), ('HOUR(0.5)', 12),
            ('MINUTE(TIME(0,15,0))', 15), ('SECOND(TIME(0,0,1))', 1),
            ('DAYS(TIME(12,0,0),TIME(0,0,0))', 0),
            ('TIMEVALUE(TIME(12,0,0))', 0.5),
            ('DATEVALUE(TIME(12,0,0))', 0),
            ('DATE(1900,1,1)=1', True), ('DATE(1900,1,1)=0', False),
            ('DATEVALUE(DATE(1900,1,1))', 1),
        ):
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': expected, 'error': None})

    def test_edate_keeps_zero_day_identity_across_datetime_inputs(self):
        p = Parser()
        p.set_function('ZERO', lambda: datetime.datetime(1899, 12, 31))
        p.set_function('NOON', lambda: datetime.datetime(1899, 12, 31, 12))
        p.set_function('DATEONLY', lambda: datetime.date(1899, 12, 31))
        for source in ('ZERO()', 'NOON()', 'DATEONLY()', 'TIME(12,0,0)', 'EDATE(0,0)'):
            for months, expected in (
                ('0', datetime.datetime(1899, 12, 31)),
                ('1', datetime.datetime(1900, 1, 31)),
                ('12', datetime.datetime(1900, 12, 31)),
            ):
                expression = 'EDATE(' + source + ',' + months + ')'
                with self.subTest(expression=expression):
                    self.assertEqual(p.parse(expression), {'result': expected, 'error': None})
        self.assertEqual(p.parse('EDATE(0,0)=0'), {'result': True, 'error': None})

    def test_date_consumers_preserve_errors_in_every_argument(self):
        p = Parser()
        for name, valid_args in (
            ('DATE', ['2025', '1', '1']),
            ('TIME', ['12', '30', '45']),
            ('DATEVALUE', ['"2025-01-01 12:00:00"']),
            ('TIMEVALUE', ['"12:00"']),
            ('WEEKDAY', ['DATE(2025,1,1)', '2']),
            ('DATEDIF', ['DATE(2024,1,1)', 'DATE(2025,1,1)', '"d"']),
        ):
            for source_error in (error.NOT_AVAILABLE, error.DIV_ZERO, error.NUM):
                p.set_function('FAIL', lambda value=source_error: value)
                for position in range(len(valid_args)):
                    for source in ('FAIL()', str(source_error)):
                        args = valid_args.copy()
                        args[position] = source
                        expression = name + '(' + ','.join(args) + ')'
                        with self.subTest(expression=expression, error=str(source_error)):
                            self.assertEqual(p.parse(expression),
                                             {'result': None, 'error': str(source_error)})
                            self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                             {'result': 99, 'error': None})
                            expected = ({'result': 77, 'error': None}
                                        if source_error is error.NOT_AVAILABLE
                                        else {'result': None, 'error': str(source_error)})
                            self.assertEqual(p.parse('IFNA(' + expression + ',77)'), expected)

    def test_date_consumers_preserve_conversion_error_codes(self):
        p = Parser()
        for source, code in (('"bad"', '#VALUE!'), ('"NaN"', '#NUM!'), ('-1', '#NUM!')):
            for expression in (
                'DATEVALUE(' + source + ')',
                'TIMEVALUE(' + source + ')', 'WEEKDAY(' + source + ')',
                'DATEDIF(' + source + ',DATE(2025,1,1),"d")',
                'DATEDIF(DATE(2024,1,1),' + source + ',"d")',
            ):
                with self.subTest(expression=expression):
                    self.assertEqual(p.parse(expression), {'result': None, 'error': code})
                    self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                     {'result': 99, 'error': None})

    def test_date_error_propagation_keeps_precedence_and_valid_results(self):
        p = Parser()
        for expression, expected in (
            ('TIMEVALUE("12:00")', 0.5), ('TIMEVALUE(0.5)', 0.5),
            ('WEEKDAY(DATE(2025,1,1))', 4),
            ('WEEKDAY(DATE(2025,1,1),2)', 3),
            ('WEEKDAY(DATE(2025,1,1),3)', 2),
            ('DATEDIF(DATE(2024,1,1),DATE(2025,1,1),"d")', 366),
        ):
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': expected, 'error': None})
        for expression, code in (
            ('DATE(#N/A,#DIV/0!,1)', '#N/A'),
            ('DATE(#DIV/0!,1,#N/A)', '#DIV/0!'),
            ('TIME(#N/A,#DIV/0!,0)', '#N/A'),
            ('TIME(#DIV/0!,0,#N/A)', '#DIV/0!'),
            ('DATE("bad",1,1)', '#VALUE!'),
            ('TIME(12,"bad",0)', '#VALUE!'),
            ('WEEKDAY(#DIV/0!,#N/A)', '#DIV/0!'),
            ('DATEDIF(#N/A,#DIV/0!,"d")', '#N/A'),
            ('DATEDIF(#DIV/0!,#N/A,#NUM!)', '#DIV/0!'),
            ('WEEKDAY(DATE(2025,1,1),0)', '#NUM!'),
            ('DATEDIF(DATE(2025,1,1),DATE(2024,1,1),"d")', '#NUM!'),
        ):
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': None, 'error': code})

    def test_days_discards_each_numeric_operands_time_before_subtraction(self):
        p = Parser()
        for expression, expected in (
            ('DAYS(0.5,0)', 0), ('DAYS(1.5,1)', 0),
            ('DAYS(2.1,1.9)', 1), ('DAYS(1.9,2.1)', -1),
            ('DAYS(0.5,NULL)', 0), ('DAYS(NULL,1.5)', -1),
            ('DAYS("1.9",0)', 1), ('DAYS(TRUE(),0)', 1),
            ('DAYS(FALSE(),0)', 0), ('DAYS(61,60)', 1),
            ('DAYS(2958465.9,2958465)', 0),
        ):
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': expected, 'error': None})

    def test_days_discards_native_and_text_date_times_without_changing_arithmetic(self):
        p = Parser()
        day = datetime.datetime(2025, 1, 1)
        p.set_function('DAY', lambda: day)
        p.set_function('NOON', lambda: datetime.datetime(2025, 1, 1, 12))
        p.set_function('DATEONLY', lambda: datetime.date(2025, 1, 2))
        for expression, expected in (
            ('DAYS(NOON(),DAY())', 0), ('DAYS(DAY(),NOON())', 0),
            ('DAYS(DATEONLY(),NOON())', 1),
            ('DAYS("2025-01-01 12:00",DAY())', 0),
            ('DAYS(NOON(),"2025-01-02 01:00")', -1),
            ('NOON()-DAY()', 0.5), ('HOUR(0.5)', 12),
        ):
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': expected, 'error': None})
        self.assertEqual(day, datetime.datetime(2025, 1, 1))

    def test_days_returns_handleable_original_errors_and_validates_ranges(self):
        p = Parser()
        for source_error in (error.NOT_AVAILABLE, error.DIV_ZERO, error.NUM):
            p.set_function('FAIL', lambda value=source_error: value)
            for expression in ('DAYS(FAIL(),1)', 'DAYS(1,FAIL())'):
                with self.subTest(expression=expression, error=str(source_error)):
                    self.assertEqual(p.parse(expression), {'result': None, 'error': str(source_error)})
                    self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                     {'result': 99, 'error': None})
        p.set_function('FAIL', lambda: error.NOT_AVAILABLE)
        self.assertEqual(p.parse('IFNA(DAYS(FAIL(),1),99)'), {'result': 99, 'error': None})
        for expression, code in (
            ('DAYS(-0.5,0)', '#NUM!'), ('DAYS(0,-1)', '#NUM!'),
            ('DAYS(2958466,0)', '#NUM!'), ('DAYS("bad",1)', '#VALUE!'),
            ('DAYS(1,"bad")', '#VALUE!'),
        ):
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': None, 'error': code})
                self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                 {'result': 99, 'error': None})

    def test_edate_zero_day_inputs_shift_to_month_ends(self):
        p = Parser()
        p.set_function('BLANK', lambda: None)
        for source in ('NULL', 'BLANK()', '0', '0.5', '"0.5"'):
            for months, expected in (
                ('0', datetime.datetime(1899, 12, 31)),
                ('NULL', datetime.datetime(1899, 12, 31)),
                ('1', datetime.datetime(1900, 1, 31)),
                ('3', datetime.datetime(1900, 3, 31)),
                ('4', datetime.datetime(1900, 4, 30)),
                ('12', datetime.datetime(1900, 12, 31)),
                ('13', datetime.datetime(1901, 1, 31)),
                ('1.9', datetime.datetime(1900, 1, 31)),
                ('"1.9"', datetime.datetime(1900, 1, 31)),
                ('-0.9', datetime.datetime(1899, 12, 31)),
            ):
                expression = 'EDATE(' + source + ',' + months + ')'
                with self.subTest(expression=expression):
                    self.assertEqual(p.parse(expression), {'result': expected, 'error': None})
            self.assertEqual(p.parse('EDATE(' + source + ',-1)'),
                             {'result': None, 'error': '#NUM!'})

    def test_edate_keeps_real_dates_distinct_and_truncates_time_and_months(self):
        p = Parser()
        stamp = datetime.datetime(2025, 1, 31, 12)
        p.set_function('STAMP', lambda: stamp)
        p.set_function('FIRST', lambda: datetime.date(1900, 1, 1))
        for expression, expected in (
            ('EDATE(1,1)', datetime.datetime(1900, 2, 1)),
            ('EDATE(FIRST(),1)', datetime.datetime(1900, 2, 1)),
            ('EDATE(STAMP(),0)', datetime.datetime(2025, 1, 31)),
            ('EDATE(STAMP(),NULL)', datetime.datetime(2025, 1, 31)),
            ('EDATE(STAMP(),1)', datetime.datetime(2025, 2, 28)),
            ('EDATE(STAMP(),-1.9)', datetime.datetime(2024, 12, 31)),
            ('EDATE(DATE(2024,1,31),1)', datetime.datetime(2024, 2, 29)),
            ('EDATE(DATE(2025,3,31),-1)', datetime.datetime(2025, 2, 28)),
        ):
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': expected, 'error': None})
        self.assertEqual(stamp, datetime.datetime(2025, 1, 31, 12))

    def test_edate_preserves_errors_and_returns_handleable_validation_errors(self):
        p = Parser()
        for source_error in (error.NOT_AVAILABLE, error.DIV_ZERO, error.NUM):
            p.set_function('FAIL', lambda value=source_error: value)
            for expression in ('EDATE(FAIL(),1)', 'EDATE(0,FAIL())'):
                with self.subTest(expression=expression, error=str(source_error)):
                    self.assertEqual(p.parse(expression), {'result': None, 'error': str(source_error)})
                    self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                     {'result': 99, 'error': None})
        for expression, code in (
            ('EDATE("bad",1)', '#VALUE!'), ('EDATE(0,"bad")', '#VALUE!'),
            ('EDATE(TRUE(),1)', '#VALUE!'), ('EDATE(FALSE(),1)', '#VALUE!'),
            ('EDATE(0,TRUE())', '#VALUE!'),
            ('EDATE(-1,1)', '#NUM!'), ('EDATE(DATE(1900,1,1),-1)', '#NUM!'),
            ('EDATE(DATE(9999,12,1),1)', '#NUM!'),
            ('EDATE(#DIV/0!,#N/A)', '#DIV/0!'),
        ):
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': None, 'error': code})
                self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                 {'result': 99, 'error': None})

    def test_time_functions_preserve_fractional_serials_below_one(self):
        p = Parser()
        for expression, expected in (
            ('HOUR(0)', 0), ('HOUR(0.25)', 6), ('HOUR(0.5)', 12),
            ('HOUR(0.75)', 18), ('HOUR("0.5")', 12),
            ('MINUTE(1/96)', 15), ('SECOND(1/86400)', 1),
            ('TIMEVALUE(0.5)', 0.5),
            ('EDATE(0,0)', datetime.datetime(1899, 12, 31)),
        ):
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': expected, 'error': None})
        for expression in ('HOUR(-0.5)', 'MINUTE(-0.5)', 'SECOND(-0.5)'):
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': None, 'error': '#NUM!'})

    def test_datevalue_discards_time_for_text_serials_and_native_dates(self):
        p = Parser()
        p.set_function('NOON', lambda: datetime.datetime(2025, 1, 1, 12))
        p.set_function('DATEONLY', lambda: datetime.date(2025, 1, 1))
        for expression, expected in (
            ('DATEVALUE("2025-01-01 12:00:00")', 45658),
            ('DATEVALUE("2025-01-01 23:59:59")', 45658),
            ('DATEVALUE(NOON())', 45658),
            ('DATEVALUE(DATEONLY())', 45658),
            ('DATEVALUE(45658.5)', 45658),
            ('DATEVALUE("45658.5")', 45658),
            ('DATEVALUE(0.5)', 0),
            ('DATEVALUE("1900-02-28 12:00:00")', 59),
            ('DATEVALUE("1900-03-01 12:00:00")', 61),
        ):
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': expected, 'error': None})

    def test_datevalue_keeps_fractional_serialization_and_arithmetic(self):
        p = Parser()
        noon = datetime.datetime(2025, 1, 1, 12)
        p.set_function('NOON', lambda: noon)
        self.assertEqual(utils.serialize_date(noon), 45658.5)
        for expression, expected in (
            ('NOON()-DATE(2025,1,1)', 0.5),
            ('TIMEVALUE(NOON())', 0.5),
            ('HOUR(NOON())', 12),
            ('N(NOON())-DATEVALUE(NOON())', 0.5),
        ):
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': expected, 'error': None})
        self.assertEqual(noon, datetime.datetime(2025, 1, 1, 12))

    def test_datevalue_uses_excel_serials_at_1900_boundaries(self):
        p = Parser()
        for expression, expected in (
            ('DATEVALUE("1900-01-01")', 1),
            ('DATEVALUE("1900-02-28")', 59),
            ('DATEVALUE("1900-03-01")', 61),
            ('DAYS(DATE(1900,3,1),DATE(1900,2,28))', 2),
            ('TIMEVALUE("00:00:00")', 0),
            ('TIMEVALUE("12:00:00")', 0.5),
        ):
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': expected, 'error': None})

    def test_date_conversion_preserves_nonfinite_numeric_errors(self):
        p = Parser()
        for value in (float('nan'), float('inf'), 'NaN', '1e309'):
            p.set_function('DATA', lambda value=value: value)
            for name in ('YEAR', 'MONTH', 'DAY', 'DATEVALUE'):
                expression = name + '(DATA())'
                with self.subTest(value=value, function=name):
                    self.assertEqual(p.parse(expression),
                                     {'result': None, 'error': '#NUM!'})
                    self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                     {'result': 99, 'error': None})

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

    def test_now(self):
        p = Parser(debug=True)
        now = datetime.datetime.now()
        ret = p.parse('YEAR(NOW())')
        self.assertEqual(ret['result'], now.year)
        self.assertEqual(ret['error'], None)
        ret = p.parse('MONTH(NOW())')
        self.assertEqual(ret['result'], now.month)
        self.assertEqual(ret['error'], None)
        ret = p.parse('DAY(NOW())')
        self.assertEqual(ret['result'], now.day)
        self.assertEqual(ret['error'], None)
        ret = p.parse('HOUR(NOW())')
        self.assertEqual(ret['result'], now.hour)
        self.assertEqual(ret['error'], None)
        ret = p.parse('MINUTE(NOW())')
        self.assertEqual(ret['result'], now.minute)
        self.assertEqual(ret['error'], None)

    def test_datedif(self):
        p = Parser(debug=True)
        ret = p.parse('DATEDIF(DATE(2019,10,6), DATE(2020,10,5), "Y")')
        self.assertEqual(ret['result'], 0)
        self.assertEqual(ret['error'], None)
        ret = p.parse('DATEDIF(DATE(2019,10,6), DATE(2020,10,5), "m")')
        self.assertEqual(ret['result'], 11)
        self.assertEqual(ret['error'], None)
        ret = p.parse('DATEDIF(DATE(2019,10,6), DATE(2020,10,5), "d")')
        self.assertEqual(ret['result'], 365)
        self.assertEqual(ret['error'], None)
        ret = p.parse('DATEDIF(DATE(2019,1,20), DATE(2019,3,10), "md")')
        self.assertEqual(ret['result'], 18)
        self.assertEqual(ret['error'], None)
        ret = p.parse('DATEDIF(DATE(2019,10,6), DATE(2020,10,5), "ym")')
        self.assertEqual(ret['result'], 11)
        self.assertEqual(ret['error'], None)
        ret = p.parse('DATEDIF(DATE(2019,10,4), DATE(2020,10,5), "yd")')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)


    def test_edate(self):
        p = Parser(debug=True)
        ret = p.parse('EDATE(DATE(2019,10,6), -1437)')
        self.assertEqual(ret['result'], datetime.datetime(1900, 1, 6))
        self.assertEqual(ret['error'], None)
        ret = p.parse('EDATE(DATE(2019,10,6), -1)')
        self.assertEqual(ret['result'], datetime.datetime(2019, 9, 6))
        self.assertEqual(ret['error'], None)
        ret = p.parse('EDATE(DATE(2019,10,6), 12)')
        self.assertEqual(ret['result'], datetime.datetime(2020, 10, 6))
        self.assertEqual(ret['error'], None)
        ret = p.parse('EDATE(DATE(2019,10,6), -12)')
        self.assertEqual(ret['result'], datetime.datetime(2018, 10, 6))
        self.assertEqual(ret['error'], None)
        ret = p.parse('EDATE(, 4)')
        self.assertEqual(ret['result'], datetime.datetime(1900, 4, 30))
        self.assertEqual(ret['error'], None)
        ret = p.parse('EDATE(DATE(2019,10,6), )')
        self.assertEqual(ret['result'], datetime.datetime(2019,10,6))
        self.assertEqual(ret['error'], None)
        ret = p.parse('EDATE(0,0)')
        self.assertEqual(ret['result'], datetime.datetime(1899, 12, 31))
        self.assertEqual(ret['error'], None)
        ret = p.parse('EDATE(DATE(1999,7,8), 404)')
        self.assertEqual(ret['result'], datetime.datetime(2033, 3, 8))
        self.assertEqual(ret['error'], None)


    def test_weekday(self):
        p = Parser(debug=True)
        # Day of the week, with numbers 1 (Sunday) through 7 (Saturday) (5)
        ret = p.parse('WEEKDAY("2/14/2008")')
        self.assertEqual(ret['result'], 5)
        self.assertEqual(ret['error'], None)
        ret = p.parse('WEEKDAY("2/14/2008", 1)')
        self.assertEqual(ret['result'], 5)
        self.assertEqual(ret['error'], None)
        ret = p.parse('WEEKDAY("2/16/2008", 1)')
        self.assertEqual(ret['result'], 7)
        self.assertEqual(ret['error'], None)
        ret = p.parse('WEEKDAY("2/17/2008", 1)')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)
        # Day of the week, with numbers 1 (Monday) through 7 (Sunday) (4)
        ret = p.parse('WEEKDAY("2/14/2008", 2)')
        self.assertEqual(ret['result'], 4)
        self.assertEqual(ret['error'], None)
        # Day of the week, with numbers 0 (Monday) through 6 (Sunday) (3)
        ret = p.parse('WEEKDAY("2/14/2008", 3)')
        self.assertEqual(ret['result'], 3)
        self.assertEqual(ret['error'], None)
        # No return type other than 1-3
        ret = p.parse('WEEKDAY("2/14/2008", 4)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#NUM!')
