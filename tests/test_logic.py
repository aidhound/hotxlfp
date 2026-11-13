# -*- coding: utf-8 -*-
import unittest
from hotxlfp import Parser
from hotxlfp.formulas import error


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

    def test_and_or_preserve_direct_errors_even_after_decisive_values(self):
        p = Parser()
        for source_error in (error.DIV_ZERO, error.NOT_AVAILABLE):
            p.set_function('ERR', lambda value=source_error: value)
            for name in ('AND', 'OR'):
                for source in ('ERR()', str(source_error)):
                    for value in ('TRUE()', 'FALSE()'):
                        for args in (value + ',' + source, source + ',' + value):
                            expression = name + '(' + args + ')'
                            with self.subTest(expression=expression,
                                              error=str(source_error)):
                                self.assertEqual(p.parse(expression),
                                                 {'result': None, 'error': str(source_error)})
                                self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                                 {'result': 99, 'error': None})
                                expected = ({'result': 77, 'error': None}
                                            if source_error is error.NOT_AVAILABLE
                                            else {'result': None, 'error': str(source_error)})
                                self.assertEqual(p.parse('IFNA(' + expression + ',77)'),
                                                 expected)
        for name in ('AND', 'OR'):
            self.assertEqual(p.parse(name + '(missing_value,TRUE())'),
                             {'result': None, 'error': '#NAME?'})

    def test_and_or_preserve_the_first_error_in_nested_arrays(self):
        p = Parser()
        for name, decisive_value in (('AND', False), ('OR', True)):
            for first_error, second_error in ((error.NOT_AVAILABLE, error.DIV_ZERO),
                                              (error.DIV_ZERO, error.NOT_AVAILABLE)):
                values = [decisive_value, (first_error, [second_error])]
                p.set_function('DATA', lambda values=values: values)
                expression = name + '(DATA())'
                with self.subTest(expression=expression, error=str(first_error)):
                    self.assertEqual(p.parse(expression),
                                     {'result': None, 'error': str(first_error)})
                    self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                     {'result': 99, 'error': None})

    def test_and_or_preserve_boolean_results_for_valid_arrays(self):
        p = Parser()
        for values, and_result, or_result in [
            ([True, (1, 2)], True, True),
            ([True, (0, False)], False, True),
            ([False, (0, False)], False, False),
        ]:
            p.set_function('DATA', lambda values=values: values)
            for name, expected in (('AND', and_result), ('OR', or_result)):
                with self.subTest(function=name, values=values):
                    actual = p.parse(name + '(DATA())')
                    self.assertEqual(actual, {'result': expected, 'error': None})
                    self.assertIs(actual['result'], expected)

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

    def test_if_preserves_errors_from_its_condition(self):
        p = Parser()
        for source_error in (error.DIV_ZERO, error.NOT_AVAILABLE, error.NUM):
            p.set_function('ERR', lambda value=source_error: value)
            p.set_function('DATA', lambda value=source_error: [5, value])
            for condition in (str(source_error), 'ERR()', 'SUM(DATA())'):
                expression = 'IF(' + condition + ',1,2)'
                with self.subTest(error=str(source_error), condition=condition):
                    self.assertEqual(p.parse(expression),
                                     {'result': None, 'error': str(source_error)})
                    self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                     {'result': 99, 'error': None})
                    expected = ({'result': 77, 'error': None}
                                if source_error is error.NOT_AVAILABLE
                                else {'result': None, 'error': str(source_error)})
                    self.assertEqual(p.parse('IFNA(' + expression + ',77)'), expected)
        self.assertEqual(p.parse('IF(missing_condition,1,2)'),
                         {'result': None, 'error': '#NAME?'})
        self.assertEqual(p.parse('IFERROR(IF(missing_condition,1,2),99)'),
                         {'result': 99, 'error': None})

    def test_if_preserves_errors_only_from_the_selected_branch(self):
        p = Parser()
        p.set_function('DATA', lambda: [5, error.DIV_ZERO])
        for expression, result, code in [
            ('IF(TRUE(),SUM(DATA()),5)', None, '#DIV/0!'),
            ('IF(FALSE(),5,SUM(DATA()))', None, '#DIV/0!'),
            ('IF(FALSE(),SUM(DATA()),5)', 5, None),
            ('IF(TRUE(),5,SUM(DATA()))', 5, None),
        ]:
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression),
                                 {'result': result, 'error': code})

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

    def test_iferror_arrays_preserve_shape_and_ordinary_values(self):
        p = Parser()
        cases = [
            ([5, error.DIV_ZERO, None, '', False, '#DIV/0!'],
             [5, 0, None, '', False, '#DIV/0!']),
            ((5, error.NOT_AVAILABLE, None), (5, 0, None)),
            ([[5, error.DIV_ZERO], (error.NOT_AVAILABLE, None)],
             [[5, 0], (0, None)]),
        ]
        for values, expected in cases:
            with self.subTest(values=values):
                p.set_function('DATA', lambda values=values: values)
                self.assertEqual(p.parse('IFERROR(DATA(),0)'),
                                 {'result': expected, 'error': None})

    def test_ifna_arrays_only_replace_na_errors(self):
        p = Parser()
        cases = [
            ([5, error.NOT_AVAILABLE, error.DIV_ZERO, None, '#N/A'],
             [5, 77, error.DIV_ZERO, None, '#N/A']),
            ((error.NOT_AVAILABLE, 5), (77, 5)),
            ([[5, error.DIV_ZERO], (error.NOT_AVAILABLE, None)],
             [[5, error.DIV_ZERO], (77, None)]),
        ]
        for values, expected in cases:
            with self.subTest(values=values):
                p.set_function('DATA', lambda values=values: values)
                self.assertEqual(p.parse('IFNA(DATA(),77)'),
                                 {'result': expected, 'error': None})

    def test_array_error_handlers_do_not_modify_input(self):
        p = Parser()
        values = [[5, error.DIV_ZERO], [error.NOT_AVAILABLE, None]]
        p.set_function('DATA', lambda: values)
        for name in ('IFERROR', 'IFNA'):
            with self.subTest(function=name):
                p.parse(name + '(DATA(),0)')
                self.assertEqual(values,
                                 [[5, error.DIV_ZERO], [error.NOT_AVAILABLE, None]])

    def test_array_error_handlers_preserve_empty_arrays(self):
        p = Parser()
        for values in ([], (), [[], ()]):
            p.set_function('DATA', lambda values=values: values)
            for name in ('IFERROR', 'IFNA'):
                with self.subTest(function=name, values=values):
                    self.assertEqual(p.parse(name + '(DATA(),0)'),
                                     {'result': values, 'error': None})

    def test_aggregates_consume_arrays_after_error_substitution(self):
        p = Parser()
        cases = [
            ([5, error.DIV_ZERO, None], 'SUM(IFERROR(DATA(),0))', 5, None),
            ([5, error.DIV_ZERO, None], 'AVERAGE(IFERROR(DATA(),0))', 2.5, None),
            ([5, error.DIV_ZERO, None], 'AVERAGE(IFERROR(DATA(),""))', 5, None),
            ([5, error.NOT_AVAILABLE], 'SUM(IFNA(DATA(),0))', 5, None),
            ([5, error.DIV_ZERO], 'SUM(IFNA(DATA(),0))', None, '#DIV/0!'),
        ]
        for values, expression, result, code in cases:
            with self.subTest(expression=expression):
                p.set_function('DATA', lambda values=values: values)
                self.assertEqual(p.parse(expression),
                                 {'result': result, 'error': code})

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

    def test_ifs_preserves_errors_in_conditions_before_a_match(self):
        p = Parser()
        for source_error in (error.DIV_ZERO, error.NOT_AVAILABLE, error.NUM):
            p.set_function('ERR', lambda value=source_error: value)
            p.set_function('DATA', lambda value=source_error: [5, value])
            for condition in (str(source_error), 'ERR()', 'SUM(DATA())'):
                for args in (condition + ',1,TRUE(),2',
                             'FALSE(),0,' + condition + ',1,TRUE(),2'):
                    expression = 'IFS(' + args + ')'
                    with self.subTest(expression=expression, error=str(source_error)):
                        self.assertEqual(p.parse(expression),
                                         {'result': None, 'error': str(source_error)})
                        self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                         {'result': 99, 'error': None})
                        expected = ({'result': 77, 'error': None}
                                    if source_error is error.NOT_AVAILABLE
                                    else {'result': None, 'error': str(source_error)})
                        self.assertEqual(p.parse('IFNA(' + expression + ',77)'), expected)
        for expression, code in [
            ('IFS(missing_condition,1,TRUE(),2)', '#NAME?'),
            ('IFS(#N/A,1,#DIV/0!,2)', '#N/A'),
            ('IFS(#DIV/0!,1,#N/A,2)', '#DIV/0!'),
        ]:
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': None, 'error': code})

    def test_ifs_preserves_errors_only_from_reached_conditions_or_selected_results(self):
        p = Parser()
        p.set_function('ERR', lambda: error.DIV_ZERO)
        for expression, result, code in [
            ('IFS(TRUE(),5,ERR(),1)', 5, None),
            ('IFS(TRUE(),5,missing_condition,1)', 5, None),
            ('IFS(FALSE(),ERR(),TRUE(),5)', 5, None),
            ('IFS(TRUE(),5,FALSE(),ERR())', 5, None),
            ('IFS(TRUE(),ERR(),TRUE(),5)', None, '#DIV/0!'),
            ('IFS(FALSE(),0,TRUE(),ERR())', None, '#DIV/0!'),
            ('IFS(FALSE(),ERR(),FALSE(),5)', None, '#N/A'),
        ]:
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression),
                                 {'result': result, 'error': code})

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
        ret = p.parse('SWITCH(4,2,"lele",3, "lili", 0)')
        self.assertEqual(ret['result'], 0)
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

    def test_not_preserves_errors_for_enclosing_handlers(self):
        p = Parser()
        for source_error in (error.DIV_ZERO, error.NOT_AVAILABLE, error.NUM):
            p.set_function('ERR', lambda value=source_error: value)
            p.set_function('DATA', lambda value=source_error: [5, value])
            for source in (str(source_error), 'ERR()', 'SUM(DATA())'):
                expression = 'NOT(' + source + ')'
                with self.subTest(source=source, error=str(source_error)):
                    self.assertEqual(p.parse(expression),
                                     {'result': None, 'error': str(source_error)})
                    self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                     {'result': 99, 'error': None})
                    expected = ({'result': 77, 'error': None}
                                if source_error is error.NOT_AVAILABLE
                                else {'result': None, 'error': str(source_error)})
                    self.assertEqual(p.parse('IFNA(' + expression + ',77)'), expected)
        self.assertEqual(p.parse('NOT(missing_value)'),
                         {'result': None, 'error': '#NAME?'})

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

    def test_xor_preserves_scalar_and_nested_errors(self):
        p = Parser()
        for source_error in (error.DIV_ZERO, error.NOT_AVAILABLE, error.NUM):
            p.set_function('ERR', lambda value=source_error: value)
            p.set_function('DATA', lambda value=source_error:
                           [False, (value, error.DIV_ZERO)])
            for expression in ('XOR(' + str(source_error) + ')',
                               'XOR(TRUE(),ERR())', 'XOR(ERR(),FALSE())',
                               'XOR(DATA())', 'XOR(SUM(DATA()),TRUE())'):
                with self.subTest(expression=expression, error=str(source_error)):
                    self.assertEqual(p.parse(expression),
                                     {'result': None, 'error': str(source_error)})
                    self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                     {'result': 99, 'error': None})
                    expected = ({'result': 77, 'error': None}
                                if source_error is error.NOT_AVAILABLE
                                else {'result': None, 'error': str(source_error)})
                    self.assertEqual(p.parse('IFNA(' + expression + ',77)'), expected)
        self.assertEqual(p.parse('XOR(missing_value)'),
                         {'result': None, 'error': '#NAME?'})

    def test_xor_preserves_valid_nested_parity(self):
        p = Parser()
        for values, expected in [
            ([True, (False, False)], True),
            ([True, (True, False)], False),
            ([True, [True, (True,)]], True),
            ([False, (False,)], False),
        ]:
            with self.subTest(values=values):
                p.set_function('DATA', lambda values=values: values)
                actual = p.parse('XOR(DATA())')
                self.assertEqual(actual, {'result': expected, 'error': None})
                self.assertIs(actual['result'], expected)
