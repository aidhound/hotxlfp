# -*- coding: utf-8 -*-
import unittest
import math
from hotxlfp import Parser
from hotxlfp.formulas import error


class TestText(unittest.TestCase):

    def test_text_arguments_coerce_numbers_and_booleans_like_excel(self):
        p = Parser()
        for source, text in (('123', '123'), ('0', '0'), ('1.0', '1'),
                             ('2.5', '2.5'), ('TRUE()', 'TRUE'), ('FALSE()', 'FALSE')):
            for expression, expected in (
                (source + '&"x"', text + 'x'),
                ('"x"&' + source, 'x' + text),
                ('CLEAN(' + source + ')', text),
                ('TRIM(' + source + ')', text),
                ('LOWER(' + source + ')', text.lower()),
                ('UPPER(' + source + ')', text.upper()),
                ('PROPER(' + source + ')', text.title()),
                ('CODE(' + source + ')', ord(text[0])),
                ('TEXTJOIN("|",TRUE(),' + source + ',"x")', text + '|x'),
            ):
                with self.subTest(expression=expression):
                    self.assertEqual(p.parse(expression), {'result': expected, 'error': None})
            for name, suffix, expected in (
                ('LEN', '', len(text)), ('LENB', '', len(text)),
                ('LEFT', ',2', text[:2]), ('LEFTB', ',2', text[:2]),
                ('RIGHT', ',2', text[-2:]), ('RIGHTB', ',2', text[-2:]),
                ('MID', ',2,2', text[1:3]), ('MIDB', ',2,2', text[1:3]),
                ('CONCAT', ',"x"', text + 'x'), ('CONCATENATE', ',"x"', text + 'x'),
            ):
                expression = name + '(' + source + suffix + ')'
                with self.subTest(expression=expression):
                    self.assertEqual(p.parse(expression), {'result': expected, 'error': None})

    def test_substitute_converts_every_text_argument(self):
        p = Parser()
        for expression, expected in (
            ('SUBSTITUTE(123,2,9)', '193'),
            ('SUBSTITUTE(TRUE(),"R","x")', 'TxUE'),
            ('SUBSTITUTE("x0x",0,FALSE())', 'xFALSEx'),
            ('SUBSTITUTE("aba","a",0,2)', 'ab0'),
            ('SUBSTITUTE("aba","a",FALSE())', 'FALSEbFALSE'),
        ):
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': expected, 'error': None})

    def test_textjoin_converts_delimiters_and_keeps_zeroes_and_booleans(self):
        p = Parser()
        for expression, expected in (
            ('TEXTJOIN(1,TRUE(),"a","b")', 'a1b'),
            ('TEXTJOIN(TRUE(),TRUE(),"a","b")', 'aTRUEb'),
            ('TEXTJOIN(NULL,FALSE(),"a","b")', 'ab'),
            ('TEXTJOIN("|",TRUE(),{"",NULL;0,FALSE()})', '0|FALSE'),
            ('TEXTJOIN("|",FALSE(),{"",NULL;0,FALSE()})', '||0|FALSE'),
        ):
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': expected, 'error': None})

    def test_code_uses_the_first_converted_character_and_rejects_empty_text(self):
        p = Parser()
        self.assertEqual(p.parse('CODE("ABC")'), {'result': 65, 'error': None})
        for source in ('""', 'NULL'):
            self.assertEqual(p.parse('CODE(' + source + ')'),
                             {'result': None, 'error': '#VALUE!'})

    def test_text_format_arguments_keep_excel_validation(self):
        p = Parser()
        for expression, expected in (
            ('TEXT(12,1)', '1'), ('TEXT(12,NULL)', ''),
            ('TEXT(TRUE(),"0")', 'TRUE'), ('TEXT(FALSE(),"0")', 'FALSE'),
        ):
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': expected, 'error': None})
        self.assertEqual(p.parse('TEXT(12,TRUE())'),
                         {'result': None, 'error': '#VALUE!'})

    def test_text_consumers_preserve_errors_in_every_argument(self):
        p = Parser()
        for name, valid_args in (
            ('CODE', ['"A"']),
            ('SUBSTITUTE', ['"abc"', '"a"', '"x"', '1']),
            ('TEXTJOIN', ['","', 'TRUE()', '"a"', '"b"']),
            ('TEXT', ['12', '"0"']),
        ):
            for source_error in (error.DIV_ZERO, error.NOT_AVAILABLE, error.NUM):
                p.set_function('ERR', lambda value=source_error: value)
                for position in range(len(valid_args)):
                    for source in (str(source_error), 'ERR()'):
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

    def test_textjoin_preserves_nested_errors_with_either_empty_policy(self):
        p = Parser()
        for source_error in (error.NOT_AVAILABLE, error.DIV_ZERO):
            p.set_function('DATA', lambda value=source_error: ['a', (None, ['b', value])])
            for ignore_empty in ('TRUE()', 'FALSE()'):
                expression = 'TEXTJOIN(",",' + ignore_empty + ',DATA())'
                with self.subTest(expression=expression, error=str(source_error)):
                    self.assertEqual(p.parse(expression),
                                     {'result': None, 'error': str(source_error)})
                    self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                     {'result': 99, 'error': None})
                    expected = ({'result': 77, 'error': None}
                                if source_error is error.NOT_AVAILABLE
                                else {'result': None, 'error': str(source_error)})
                    self.assertEqual(p.parse('IFNA(' + expression + ',77)'), expected)

    def test_text_consumers_preserve_error_precedence_and_valid_inputs(self):
        p = Parser()
        for expression, result, code in (
            ('SUBSTITUTE(#DIV/0!,"a","x",#N/A)', None, '#DIV/0!'),
            ('SUBSTITUTE("",#N/A,"x")', None, '#N/A'),
            ('SUBSTITUTE("abc","",#DIV/0!)', None, '#DIV/0!'),
            ('TEXTJOIN(#N/A,#DIV/0!,"a")', None, '#N/A'),
            ('TEXTJOIN(",",TRUE(),{"a",#DIV/0!},#N/A)', None, '#DIV/0!'),
            ('TEXT(#DIV/0!,#N/A)', None, '#DIV/0!'),
            ('CODE("A")', 65, None),
            ('SUBSTITUTE("#N/A","N","X")', '#X/A', None),
            ('SUBSTITUTE("abc","a","x",2)', 'abc', None),
            ('SUBSTITUTE("abc","a","x","bad")', None, '#VALUE!'),
            ('SUBSTITUTE("abc","a","x",0)', None, '#VALUE!'),
            ('TEXTJOIN(",",TRUE(),{"a",,"#N/A"})', 'a,#N/A', None),
            ('TEXTJOIN(",",FALSE(),{"a",,"b"})', 'a,,b', None),
            ('TEXTJOIN(1,TRUE(),"a")', 'a', None),
            ('TEXT(12,"0.00")', '12.00', None),
            ('TEXT(12,1)', '1', None),
        ):
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': result, 'error': code})

    def test_char(self):
        p = Parser(debug=True)
        ret = p.parse('CHAR(65)')
        self.assertEqual(ret['result'], 'A')
        self.assertEqual(ret['error'], None)
        ret = p.parse('CHAR(33)')
        self.assertEqual(ret['result'], '!')
        self.assertEqual(ret['error'], None)
        ret = p.parse('CHAR(1/0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')

    def test_code(self):
        p = Parser(debug=True)
        ret = p.parse('CODE("A")')
        self.assertEqual(ret['result'], 65)
        self.assertEqual(ret['error'], None)
        ret = p.parse('CODE("!")')
        self.assertEqual(ret['result'], 33)
        self.assertEqual(ret['error'], None)

    def test_clean(self):
        p = Parser(debug=True)
        ret = p.parse('CLEAN(CHAR(9)&"Monthly report"&CHAR(10))')
        self.assertEqual(ret['result'], 'Monthly report')
        self.assertEqual(ret['error'], None)
        ret = p.parse('CLEAN(B3)')
        self.assertEqual(ret['result'], '')
        self.assertEqual(ret['error'], None)
        ret = p.parse('CLEAN(1/0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')
        ret = p.parse('CLEAN(223)')
        self.assertEqual(ret['result'], '223')
        self.assertEqual(ret['error'], None)

    def test_concatenate_treats_blank_elements_as_empty_text(self):
        p = Parser()
        p.set_function('BLANK', lambda: None)
        p.set_function('DATA', lambda: [None, ('x', [None, 'y']), None])
        for name in ('CONCAT', 'CONCATENATE'):
            for args, expected in (
                ('NULL,"x"', 'x'), ('BLANK(),"x"', 'x'),
                ('{BLANK(),"x";"y",BLANK()}', 'xy'), ('DATA()', 'xy'),
                ('NULL,BLANK(),""', ''), ('{NULL,BLANK();BLANK(),NULL}', ''),
                ('"None",NULL,"x"', 'Nonex'), ('', ''),
            ):
                expression = name + '(' + args + ')'
                with self.subTest(expression=expression):
                    self.assertEqual(p.parse(expression), {'result': expected, 'error': None})

    def test_concatenate_keeps_zero_booleans_literal_text_and_order(self):
        p = Parser()
        p.set_function('DATA', lambda: [None, (0, [False, True]), 2.5, 'None'])
        for name in ('CONCAT', 'CONCATENATE'):
            for args, expected in (
                ('0,"x"', '0x'), ('FALSE(),TRUE(),0', 'FALSETRUE0'),
                ('{NULL,0;FALSE(),TRUE()}', '0FALSETRUE'),
                ('DATA()', '0FALSETRUE2.5None'), ('"#DIV/0!",NULL,"x"', '#DIV/0!x'),
                ('NULL," ","x"', ' x'),
            ):
                expression = name + '(' + args + ')'
                with self.subTest(expression=expression):
                    self.assertEqual(p.parse(expression), {'result': expected, 'error': None})

    def test_concatenate_preserves_first_nested_error_among_blanks(self):
        p = Parser()
        p.set_function('BLANK', lambda: None)
        for first, second in ((error.DIV_ZERO, error.NOT_AVAILABLE),
                               (error.NOT_AVAILABLE, error.DIV_ZERO)):
            p.set_function('FAIL', lambda value=first: value)
            p.set_function('DATA', lambda: [None, (0, [False, first]), None, second])
            for name in ('CONCAT', 'CONCATENATE'):
                for args in ('NULL,FAIL(),BLANK()', '{BLANK(),FAIL()}',
                             'NULL,DATA(),BLANK()'):
                    expression = name + '(' + args + ')'
                    with self.subTest(expression=expression, error=str(first)):
                        self.assertEqual(p.parse(expression), {'result': None, 'error': str(first)})
                        self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                         {'result': 99, 'error': None})
                        expected = ({'result': 77, 'error': None} if first is error.NOT_AVAILABLE
                                    else {'result': None, 'error': str(first)})
                        self.assertEqual(p.parse('IFNA(' + expression + ',77)'), expected)

    def test_concatenate(self):
        p = Parser(debug=True)
        ret = p.parse('CONCAT("The"," ","sun"," ","will"," ","come"," ","up"," ","tomorrow.")')
        self.assertEqual(ret['result'], 'The sun will come up tomorrow.')
        self.assertEqual(ret['error'], None)
        ret = p.parse('CONCAT(1/0, 14,"sun")')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')

    def test_len(self):
        p = Parser(debug=True)
        ret = p.parse('LEN("Phoenix, AZ")')
        self.assertEqual(ret['result'], 11)
        self.assertEqual(ret['error'], None)
        ret = p.parse('LEN("     One   ")')
        self.assertEqual(ret['result'], 11)
        self.assertEqual(ret['error'], None)
        ret = p.parse('LEN(B3)')
        self.assertEqual(ret['result'], 0)
        self.assertEqual(ret['error'], None)
        ret = p.parse('LEN(3)')
        self.assertEqual(ret['result'], 1)
        self.assertEqual(ret['error'], None)
        ret = p.parse('LEN(223)')
        self.assertEqual(ret['result'], 3)
        self.assertEqual(ret['error'], None)
        ret = p.parse('LEN(1/0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')


    def test_lower(self):
        p = Parser(debug=True)
        ret = p.parse('LOWER("aBcDe")')
        self.assertEqual(ret['result'], 'abcde')
        self.assertEqual(ret['error'], None)
        ret = p.parse('LOWER(B3)')
        self.assertEqual(ret['result'], '')
        self.assertEqual(ret['error'], None)
        ret = p.parse('LOWER(223)')
        self.assertEqual(ret['result'], '223')
        self.assertEqual(ret['error'], None)
        ret = p.parse('LOWER(1/0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')

    def test_upper(self):
        p = Parser(debug=True)
        ret = p.parse('UPPER("aBcDe")')
        self.assertEqual(ret['result'], 'ABCDE')
        self.assertEqual(ret['error'], None)
        ret = p.parse('UPPER(B3)')
        self.assertEqual(ret['result'], '')
        self.assertEqual(ret['error'], None)
        ret = p.parse('UPPER(223)')
        self.assertEqual(ret['result'], '223')
        self.assertEqual(ret['error'], None)
        ret = p.parse('UPPER(1/0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')

    def test_proper(self):
        p = Parser(debug=True)
        ret = p.parse('PROPER("aBcDe")')
        self.assertEqual(ret['result'], 'Abcde')
        self.assertEqual(ret['error'], None)
        ret = p.parse('PROPER("76budGet")')
        self.assertEqual(ret['result'], '76Budget')
        self.assertEqual(ret['error'], None)
        ret = p.parse('PROPER(B3)')
        self.assertEqual(ret['result'], '')
        self.assertEqual(ret['error'], None)
        ret = p.parse('PROPER(223)')
        self.assertEqual(ret['result'], '223')
        self.assertEqual(ret['error'], None)
        ret = p.parse('PROPER(1/0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')

    def test_substitute_normalizes_blank_source_search_and_replacement(self):
        p = Parser()
        p.set_function('BLANK', lambda: None)
        for blank in ('NULL', 'BLANK()', '""'):
            for args, expected in (
                (blank + ',"a","b"', ''),
                ('"aba",' + blank + ',"b"', 'aba'),
                ('"aba",' + blank + ',' + blank, 'aba'),
                (blank + ',' + blank + ',' + blank, ''),
            ):
                expression = 'SUBSTITUTE(' + args + ')'
                with self.subTest(expression=expression):
                    self.assertEqual(p.parse(expression), {'result': expected, 'error': None})

    def test_substitute_empty_replacement_deletes_selected_occurrences(self):
        p = Parser()
        p.set_function('BLANK', lambda: None)
        for replacement in ('""', 'NULL', 'BLANK()'):
            for occurrence, expected in (('', 'b'), (',1', 'ba'), (',2', 'ab'),
                                         (',3', 'aba'), (',"2"', 'ab')):
                expression = 'SUBSTITUTE("aba","a",' + replacement + occurrence + ')'
                with self.subTest(expression=expression):
                    self.assertEqual(p.parse(expression), {'result': expected, 'error': None})
        self.assertEqual(p.parse('SUBSTITUTE("aAa","a","")'), {'result': 'A', 'error': None})

    def test_substitute_blanks_keep_occurrence_validation_and_errors(self):
        p = Parser()
        for args in ('NULL,"a","b"', '"aba",NULL,"b"', '"aba","a",NULL', 'NULL,NULL,NULL'):
            for occurrence in ('0', '-1', '"bad"', 'NULL'):
                expression = 'SUBSTITUTE(' + args + ',' + occurrence + ')'
                with self.subTest(expression=expression):
                    self.assertEqual(p.parse(expression), {'result': None, 'error': '#VALUE!'})
        for source_error in (error.DIV_ZERO, error.NOT_AVAILABLE):
            p.set_function('FAIL', lambda value=source_error: value)
            for position in range(4):
                args = ['NULL', 'NULL', 'NULL', '1']
                args[position] = 'FAIL()'
                expression = 'SUBSTITUTE(' + ','.join(args) + ')'
                with self.subTest(expression=expression, error=str(source_error)):
                    self.assertEqual(p.parse(expression), {'result': None, 'error': str(source_error)})
                    self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                     {'result': 99, 'error': None})
                    expected = ({'result': 77, 'error': None} if source_error is error.NOT_AVAILABLE
                                else {'result': None, 'error': str(source_error)})
                    self.assertEqual(p.parse('IFNA(' + expression + ',77)'), expected)
        for expression in ('SUBSTITUTE()', 'SUBSTITUTE(NULL,"a")'):
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': None, 'error': '#ERROR!'})

    def test_substitute(self):
        p = Parser(debug=True)
        ret = p.parse('SUBSTITUTE("ccc", "a", "b")')
        self.assertEqual(ret['result'], 'ccc')
        self.assertEqual(ret['error'], None)
        ret = p.parse('SUBSTITUTE("ccc", "a", "b", 2)')
        self.assertEqual(ret['result'], 'ccc')
        self.assertEqual(ret['error'], None)
        ret = p.parse('SUBSTITUTE("ola a todos e todas as meninas e os meninos", "a", "b")')
        self.assertEqual(ret['result'], "olb b todos e todbs bs meninbs e os meninos")
        self.assertEqual(ret['error'], None)
        ret = p.parse('SUBSTITUTE("ola a todos e todas as meninas e os meninos", "a", "b", 2)')
        self.assertEqual(ret['result'], "ola b todos e todas as meninas e os meninos")
        self.assertEqual(ret['error'], None)
        ret = p.parse('SUBSTITUTE("ola a todos e todas as meninas e os meninos", "a", "b", 0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#VALUE!')
        ret = p.parse('SUBSTITUTE("ola a todos e todas as meninas e os meninos", "os", "a", 3)')
        self.assertEqual(ret['result'], "ola a todos e todas as meninas e os menina")
        self.assertEqual(ret['error'], None)
        ret = p.parse('SUBSTITUTE("ola a todos e todas as meninas e os meninos", "os", "a", 2)')
        self.assertEqual(ret['result'], "ola a todos e todas as meninas e a meninos")
        self.assertEqual(ret['error'], None)
        ret = p.parse('SUBSTITUTE("ola a todos e todas as meninas e os meninos", "a", "b", "a")')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#VALUE!')
        ret = p.parse('SUBSTITUTE(, "a", "b", "a")')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#VALUE!')
        ret = p.parse('SUBSTITUTE(;;)')
        self.assertEqual(ret['result'], '')
        self.assertEqual(ret['error'], None)
        ret = p.parse('SUBSTITUTE(;;;)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#VALUE!')

    def test_textjoin(self):
        p = Parser(debug=True)
        ret = p.parse('TEXTJOIN(";", TRUE, {"1";"2";"3"})')
        self.assertEqual(ret['result'], '1;2;3')
        self.assertEqual(ret['error'], None)
        ret = p.parse('TEXTJOIN(";", TRUE, {"1",,"2","3"})')
        self.assertEqual(ret['result'], '1;2;3')
        ret = p.parse('TEXTJOIN(";", FALSE, {"1",,"2","3"})')
        self.assertEqual(ret['result'], '1;;2;3')
        self.assertEqual(ret['error'], None)
        ret = p.parse('TEXTJOIN(1, FALSE, {"1",,"2","3"})')
        self.assertEqual(ret['result'], '111213')
        self.assertEqual(ret['error'], None)

    def test_slicing_functions_treat_blank_sources_as_empty_text(self):
        p = Parser()
        p.set_function('BLANK', lambda: None)
        for name in ('LEFT', 'LEFTB', 'RIGHT', 'RIGHTB', 'MID', 'MIDB'):
            tails = (',1', ',1,0', ',1,1', ',5,2') if name.startswith('MID') else ('', ',0', ',1', ',5')
            for source in ('NULL', 'BLANK()', '""'):
                for tail in tails:
                    expression = name + '(' + source + tail + ')'
                    with self.subTest(expression=expression):
                        self.assertEqual(p.parse(expression), {'result': '', 'error': None})

    def test_blank_slicing_keeps_position_type_and_argument_count_checks(self):
        p = Parser()
        p.set_function('BLANK', lambda: None)
        for name in ('LEFT', 'LEFTB', 'RIGHT', 'RIGHTB', 'MID', 'MIDB'):
            invalid_tails = (',0,1', ',1,-1') if name.startswith('MID') else (',-1',)
            for source in ('NULL', 'BLANK()'):
                for tail in invalid_tails:
                    expression = name + '(' + source + tail + ')'
                    with self.subTest(expression=expression):
                        self.assertEqual(p.parse(expression), {'result': None, 'error': '#VALUE!'})
            for source, expected in (('0', '0'),
                                     ('FALSE()', 'E' if name.startswith('RIGHT') else 'F')):
                expression = name + '(' + source + ',1)'
                with self.subTest(expression=expression):
                    self.assertEqual(p.parse(expression), {'result': expected, 'error': None})
            with self.subTest(name=name, missing_arguments=True):
                self.assertEqual(p.parse(name + '()'), {'result': None, 'error': '#ERROR!'})
            if name.startswith('MID'):
                self.assertEqual(p.parse(name + '(NULL)'), {'result': None, 'error': '#ERROR!'})

    def test_blank_slicing_preserves_errors_in_numeric_arguments(self):
        p = Parser()
        p.set_function('BLANK', lambda: None)
        for source_error in (error.DIV_ZERO, error.NOT_AVAILABLE):
            p.set_function('FAIL', lambda value=source_error: value)
            for name in ('LEFT', 'LEFTB', 'RIGHT', 'RIGHTB', 'MID', 'MIDB'):
                tails = (',FAIL(),1', ',1,FAIL()') if name.startswith('MID') else (',FAIL()',)
                for source in ('NULL', 'BLANK()'):
                    for tail in tails:
                        expression = name + '(' + source + tail + ')'
                        with self.subTest(expression=expression, error=str(source_error)):
                            self.assertEqual(p.parse(expression),
                                             {'result': None, 'error': str(source_error)})
                            self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                             {'result': 99, 'error': None})

    def test_left(self):
        p = Parser(debug=True)
        ret = p.parse('LEFT("Sale Price", 4)')
        self.assertEqual(ret['result'], 'Sale')
        self.assertEqual(ret['error'], None)
        ret = p.parse('LEFT("Sweeden")')
        self.assertEqual(ret['result'], 'S')
        self.assertEqual(ret['error'], None)
        ret = p.parse('LEFT("Sale Price", -1)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#VALUE!')
        ret = p.parse('LEFT("Sale Price", 400)')
        self.assertEqual(ret['result'], 'Sale Price')
        self.assertEqual(ret['error'], None)

    def test_left_and_leftb_preserve_errors_in_either_argument(self):
        p = Parser()
        for name in ('LEFT', 'LEFTB'):
            for source_error in (error.DIV_ZERO, error.NOT_AVAILABLE, error.NUM):
                p.set_function('ERR', lambda value=source_error: value)
                for args in (str(source_error), str(source_error) + ',1',
                             'ERR(),1', '"Sale Price",' + str(source_error),
                             '"Sale Price",ERR()'):
                    expression = name + '(' + args + ')'
                    with self.subTest(expression=expression, error=str(source_error)):
                        self.assertEqual(p.parse(expression),
                                         {'result': None, 'error': str(source_error)})
                        self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                         {'result': 99, 'error': None})
                        expected = ({'result': 77, 'error': None}
                                    if source_error is error.NOT_AVAILABLE
                                    else {'result': None, 'error': str(source_error)})
                        self.assertEqual(p.parse('IFNA(' + expression + ',77)'), expected)

    def test_left_and_leftb_preserve_the_first_error_and_ordinary_text(self):
        p = Parser()
        for name in ('LEFT', 'LEFTB'):
            for args, result, code in [
                ('#DIV/0!,#N/A', None, '#DIV/0!'),
                ('#N/A,#DIV/0!', None, '#N/A'),
                ('"#N/A",2', '#N', None),
                ('"Sale Price",0', '', None),
            ]:
                expression = name + '(' + args + ')'
                with self.subTest(expression=expression):
                    self.assertEqual(p.parse(expression),
                                     {'result': result, 'error': code})

    def test_right_and_mid_preserve_errors_in_every_argument(self):
        p = Parser()
        for name, valid_args in (
            ('RIGHT', ['"Sale Price"', '5']),
            ('RIGHTB', ['"Sale Price"', '5']),
            ('MID', ['"Sale Price"', '2', '5']),
            ('MIDB', ['"Sale Price"', '2', '5']),
        ):
            for source_error in (error.DIV_ZERO, error.NOT_AVAILABLE, error.NUM):
                p.set_function('ERR', lambda value=source_error: value)
                for position in range(len(valid_args)):
                    for source in (str(source_error), 'ERR()'):
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

    def test_right_and_mid_preserve_first_errors_and_default_lengths(self):
        p = Parser()
        for name, args, result, code in (
            ('RIGHT', '#DIV/0!,#N/A', None, '#DIV/0!'),
            ('RIGHTB', '#N/A,#DIV/0!', None, '#N/A'),
            ('MID', '"abc",#DIV/0!,#N/A', None, '#DIV/0!'),
            ('MIDB', '#N/A,#DIV/0!,1', None, '#N/A'),
            ('RIGHT', '#N/A', None, '#N/A'),
            ('RIGHTB', '"#N/A"', 'A', None),
            ('MID', '#N/A,1', None, '#N/A'),
            ('MIDB', '"#N/A",2', 'N', None),
        ):
            expression = name + '(' + args + ')'
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': result, 'error': code})

    def test_right_and_rightb_zero_length_returns_empty_text(self):
        p = Parser()
        for name in ('RIGHT', 'RIGHTB'):
            for args, result, code in (
                ('"abc",0', '', None),
                ('"ㅍa",0', '', None),
                ('"",0', '', None),
                ('123,0', '', None),
                ('#N/A,0', None, '#N/A'),
                ('#DIV/0!,0', None, '#DIV/0!'),
            ):
                expression = name + '(' + args + ')'
                with self.subTest(expression=expression):
                    self.assertEqual(p.parse(expression), {'result': result, 'error': code})

    def test_right(self):
        p = Parser(debug=True)
        ret = p.parse('RIGHT("Sale Price", 5)')
        self.assertEqual(ret['result'], 'Price')
        self.assertEqual(ret['error'], None)
        ret = p.parse('RIGHT("Stock Number")')
        self.assertEqual(ret['result'], 'r')
        self.assertEqual(ret['error'], None)
        ret = p.parse('RIGHT("Sale Price", -1)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#VALUE!')
        ret = p.parse('RIGHT("Sale Price", 400)')
        self.assertEqual(ret['result'], 'Sale Price')
        self.assertEqual(ret['error'], None)

    def test_mid(self):
        p = Parser(debug=True)
        ret = p.parse('MID("Fluid Flow", 1, 5)')
        self.assertEqual(ret['result'], 'Fluid')
        self.assertEqual(ret['error'], None)
        ret = p.parse('MID("Fluid Flow", 7, 20)')
        self.assertEqual(ret['result'], 'Flow')
        self.assertEqual(ret['error'], None)
        ret = p.parse('MID("Fluid Flow", 20, 5)')
        self.assertEqual(ret['result'], '')
        self.assertEqual(ret['error'], None)
        ret = p.parse('MID("Fluid Flow", -1)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#VALUE!')


    def test_leftb(self):
        p = Parser(debug=True)
        ret = p.parse('LEFTB("Sale Price", 4)')
        self.assertEqual(ret['result'], 'Sale')
        self.assertEqual(ret['error'], None)
        ret = p.parse('LEFTB("Sweeden")')
        self.assertEqual(ret['result'], 'S')
        self.assertEqual(ret['error'], None)
        ret = p.parse('LEFTB("Sale Price", -1)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#VALUE!')
        ret = p.parse('LEFTB("Sale Price", 400)')
        self.assertEqual(ret['result'], 'Sale Price')
        self.assertEqual(ret['error'], None)
        ret = p.parse('LEFTB("ㅍa", 1)')
        self.assertEqual(ret['result'], 'ㅍ')
        self.assertEqual(ret['error'], None)
        ret = p.parse('LEFTB("aㅍ", 1)')
        self.assertEqual(ret['result'], 'a')
        self.assertEqual(ret['error'], None)

    def test_rightb(self):
        p = Parser(debug=True)
        ret = p.parse('RIGHTB("Sale Price", 5)')
        self.assertEqual(ret['result'], 'Price')
        self.assertEqual(ret['error'], None)
        ret = p.parse('RIGHTB("Stock Number")')
        self.assertEqual(ret['result'], 'r')
        self.assertEqual(ret['error'], None)
        ret = p.parse('RIGHTB("Sale Price", -1)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#VALUE!')
        ret = p.parse('RIGHTB("Sale Price", 400)')
        self.assertEqual(ret['result'], 'Sale Price')
        self.assertEqual(ret['error'], None)
        ret = p.parse('RIGHTB("aㅍ", 1)')
        self.assertEqual(ret['result'], 'ㅍ')
        self.assertEqual(ret['error'], None)
        ret = p.parse('RIGHTB("ㅍa", 1)')
        self.assertEqual(ret['result'], 'a')
        self.assertEqual(ret['error'], None)

    def test_midb(self):
        p = Parser(debug=True)
        ret = p.parse('MIDB("Fluid Flow", 1, 5)')
        self.assertEqual(ret['result'], 'Fluid')
        self.assertEqual(ret['error'], None)
        ret = p.parse('MIDB("Fluid Flow", 7, 20)')
        self.assertEqual(ret['result'], 'Flow')
        self.assertEqual(ret['error'], None)
        ret = p.parse('MIDB("Fluid Flow", 20, 5)')
        self.assertEqual(ret['result'], '')
        self.assertEqual(ret['error'], None)
        ret = p.parse('MIDB("Fluid Flow", -1)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#VALUE!')
        ret = p.parse('MIDB("aㅍa", 2, 2)')
        self.assertEqual(ret['result'], 'ㅍa')
        self.assertEqual(ret['error'], None)
        ret = p.parse('MIDB("aㅍa", 1, 2)')
        self.assertEqual(ret['result'], 'aㅍ')
        self.assertEqual(ret['error'], None)
        ret = p.parse('MIDB("aㅍa", 2, 1)')
        self.assertEqual(ret['result'], 'ㅍ')
        self.assertEqual(ret['error'], None)

    def test_text(self):
        p = Parser(debug=True)
        ret = p.parse('TEXT(100.25,"???/???")')
        self.assertEqual(ret['result'], '401/4')
        self.assertEqual(ret['error'], None)
        ret = p.parse('TEXT(DATE(2024,4,3),"yyyy")')
        self.assertEqual(ret['result'], '2024')
        self.assertEqual(ret['error'], None)
        ret = p.parse('TEXT(DATE(2004,4,3),"yy")')
        self.assertEqual(ret['result'], '04')
        self.assertEqual(ret['error'], None)
        ret = p.parse('TEXT(DATE(2004,4,3),"mmmmm")')
        self.assertEqual(ret['result'], 'A')
        self.assertEqual(ret['error'], None)
        ret = p.parse('TEXT(DATE(2004,4,3),"mmmm")')
        self.assertEqual(ret['result'], 'April')
        self.assertEqual(ret['error'], None)
        ret = p.parse('TEXT(DATE(2004,4,3),"mmm")')
        self.assertEqual(ret['result'], 'Apr')
        self.assertEqual(ret['error'], None)
        ret = p.parse('TEXT(DATE(2004,4,3),"mm")')
        self.assertEqual(ret['result'], '04')
        self.assertEqual(ret['error'], None)
        ret = p.parse('TEXT(DATE(2004,4,3),"m")')
        self.assertEqual(ret['result'], '4')
        self.assertEqual(ret['error'], None)
        ret = p.parse('TEXT(DATE(2004,4,3),"dddd")')
        self.assertEqual(ret['result'], 'Saturday')
        self.assertEqual(ret['error'], None)
        ret = p.parse('TEXT(DATE(2004,4,3),"ddd")')
        self.assertEqual(ret['result'], 'Sat')
        self.assertEqual(ret['error'], None)
        ret = p.parse('TEXT(DATE(2004,4,3),"dd")')
        self.assertEqual(ret['result'], '03')
        self.assertEqual(ret['error'], None)
        ret = p.parse('TEXT(DATE(2004,4,3),"d")')
        self.assertEqual(ret['result'], '3')
        self.assertEqual(ret['error'], None)
        ret = p.parse('TEXT(DATE(2004,4,3),"dd-mm-yyy")')
        self.assertEqual(ret['result'], '03-04-2004')
        self.assertEqual(ret['error'], None)
        ret = p.parse('TEXT(DATE(2004,4,3),"dddd, mmmm dd")')
        self.assertEqual(ret['result'], 'Saturday, April 03')
        self.assertEqual(ret['error'], None)
        ret = p.parse('TEXT(DATE(2004,4,3),"ddd, mmm d")')
        self.assertEqual(ret['result'], 'Sat, Apr 3')
        self.assertEqual(ret['error'], None)
        ret = p.parse('TEXT(DATE(2004,4,3),"mmmmm yy")')
        self.assertEqual(ret['result'], 'A 04')
        self.assertEqual(ret['error'], None)
        ret = p.parse('TEXT(100,"$#,##0")')
        self.assertEqual(ret['result'], '$100')
        self.assertEqual(ret['error'], None)
        ret = p.parse('TEXT(100,"#,##0€")')
        self.assertEqual(ret['result'], '100€')
        self.assertEqual(ret['error'], None)
        ret = p.parse('TEXT(0.85,"0%")')
        self.assertEqual(ret['result'], '85%')
        self.assertEqual(ret['error'], None)
        ret = p.parse('TEXT(0.85,"0")')
        self.assertEqual(ret['result'], '1')
        self.assertEqual(ret['error'], None)
        ret = p.parse('TEXT(0.5,"0")')
        self.assertEqual(ret['result'], '1')
        self.assertEqual(ret['error'], None)
        ret = p.parse('TEXT(0.4,"0")')
        self.assertEqual(ret['result'], '0')
        self.assertEqual(ret['error'], None)
        ret = p.parse('TEXT(3.141592654,"0.000")')
        self.assertEqual(ret['result'], '3.142')
        self.assertEqual(ret['error'], None)
        ret = p.parse('TEXT(25000000000,"0.0E+00")')
        self.assertEqual(ret['result'], '2.5E+10')
        self.assertEqual(ret['error'], None)
        ret = p.parse('TEXT(8.9,"#.000")')
        self.assertEqual(ret['result'], '8.900')
        self.assertEqual(ret['error'], None)
        ret = p.parse('TEXT(.631,"0.#")')
        self.assertEqual(ret['result'], '0.6')
        self.assertEqual(ret['error'], None)
        ret = p.parse('TEXT(1234.568,"#.0#")')
        self.assertEqual(ret['result'], '1234.57')
        self.assertEqual(ret['error'], None)
        ret = p.parse('TEXT(1234.59,"####.#")')
        self.assertEqual(ret['result'], '1234.6')
        self.assertEqual(ret['error'], None)
        ret = p.parse('TEXT(8.9, "#.000")')
        self.assertEqual(ret['result'], "8.900")
        self.assertEqual(ret['error'], None)
        ret = p.parse('TEXT(.631, "0.#")')
        self.assertEqual(ret['result'], "0.6")
        self.assertEqual(ret['error'], None)
        ret = p.parse('TEXT(1234.568, "#.0#")')
        self.assertEqual(ret['result'], "1234.57")
        self.assertEqual(ret['error'], None)
        ret = p.parse('TEXT(12, "#.0#")')
        self.assertEqual(ret['result'], "12.00")
        self.assertEqual(ret['error'], None)
        ret = p.parse('TEXT(5.25, "# ???/???")')
        self.assertEqual(ret['result'], "5 1/4")
        self.assertEqual(ret['error'], None)

    def test_trim_blank_source_returns_empty_text_for_enclosing_functions(self):
        p = Parser()
        p.set_function('BLANK', lambda: None)
        for expression, expected in (
            ('TRIM(NULL)', ''), ('TRIM(BLANK())', ''), ('TRIM("")', ''),
            ('AVERAGEA(TRIM(BLANK()),2)', 1), ('AVERAGEA(NULL,2)', 2),
        ):
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': expected, 'error': None})

    def test_trim_converts_nonstring_values_and_keeps_errors_and_argument_count_checks(self):
        p = Parser()
        for source_error in (error.DIV_ZERO, error.NOT_AVAILABLE):
            p.set_function('FAIL', lambda value=source_error: value)
            expression = 'TRIM(FAIL())'
            with self.subTest(error=str(source_error)):
                self.assertEqual(p.parse(expression), {'result': None, 'error': str(source_error)})
                self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                 {'result': 99, 'error': None})
                expected = ({'result': 77, 'error': None} if source_error is error.NOT_AVAILABLE
                            else {'result': None, 'error': str(source_error)})
                self.assertEqual(p.parse('IFNA(' + expression + ',77)'), expected)
        for expression, expected in (('TRIM(0)', '0'), ('TRIM(FALSE())', 'FALSE'),
                                    ('TRIM(3.14)', '3.14')):
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': expected, 'error': None})
        for expression in ('TRIM()', 'TRIM(NULL,1)'):
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': None, 'error': '#ERROR!'})

    def test_trim(self):
        p = Parser(debug=True)
        ret = p.parse('TRIM(" test ")')
        self.assertEqual(ret['result'], 'test')
        self.assertEqual(ret['error'], None)
        ret = p.parse('TRIM(" test   3 spaces later")')
        self.assertEqual(ret['result'], 'test 3 spaces later')
        self.assertEqual(ret['error'], None)
        ret = p.parse('TRIM("     ")')
        self.assertEqual(ret['result'], '')
        self.assertEqual(ret['error'], None)
        ret = p.parse('TRIM(3.14)')
        self.assertEqual(ret['result'], '3.14')
        self.assertEqual(ret['error'], None)
