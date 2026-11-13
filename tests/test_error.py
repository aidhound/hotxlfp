# -*- coding: utf-8 -*-
import unittest
from hotxlfp import Parser
from hotxlfp.formulas import error


class TestError(unittest.TestCase):
    """ Stuff that should cause errors """

    def test_bare_error_literals_preserve_their_codes(self):
        p = Parser()
        for source_error in (error.ERROR, error.DIV_ZERO, error.NAME,
                             error.NOT_AVAILABLE, error.NULL, error.NUM,
                             error.REF, error.VALUE):
            with self.subTest(error=str(source_error)):
                self.assertEqual(p.parse(str(source_error)),
                                 {'result': None, 'error': str(source_error)})

    def test_error_literals_reach_enclosing_functions(self):
        p = Parser()
        cases = [
            ('IFERROR(#DIV/0!,99)', 99, None),
            ('IFNA(#N/A,77)', 77, None),
            ('IFNA(#DIV/0!,77)', None, '#DIV/0!'),
            ('ISERROR(#VALUE!)', True, None),
            ('IF(FALSE(),#DIV/0!,5)', 5, None),
            ('COUNT(#DIV/0!)', 0, None),
            ('IFERROR(SUM(5,#DIV/0!),99)', 99, None),
            ('IFERROR("#DIV/0!",99)', '#DIV/0!', None),
        ]
        for formula, result, code in cases:
            with self.subTest(formula=formula):
                self.assertEqual(p.parse(formula),
                                 {'result': result, 'error': code})

    def test_syntax_errors_abort_even_inside_error_handlers(self):
        p = Parser()
        for formula in ('1+', 'SUM(1', 'IFERROR(1+,99)',
                        'IFERROR(#DIV/0!,99'):
            with self.subTest(formula=formula):
                with self.assertRaises(error.XLError) as caught:
                    p.parser.parse(formula)
                self.assertIs(caught.exception, error.ERROR)
                self.assertEqual(p.parse(formula),
                                 {'result': None, 'error': '#ERROR!'})
        self.assertEqual(p.parse('1+2'), {'result': 3, 'error': None})

    def test_aggregate_errors_reach_enclosing_functions(self):
        p = Parser()
        for source_error in (error.DIV_ZERO, error.NOT_AVAILABLE):
            p.set_function('DATA', lambda value=source_error: [5, value])
            for aggregate in ('SUM', 'AVERAGE'):
                expression = aggregate + '(DATA())'
                cases = [
                    (expression, None, str(source_error)),
                    ('IFERROR(' + expression + ',99)', 99, None),
                    ('ISERROR(' + expression + ')', True, None),
                    ('IF(FALSE(),' + expression + ',5)', 5, None),
                ]
                if source_error is error.NOT_AVAILABLE:
                    cases.append(('IFNA(' + expression + ',77)', 77, None))
                else:
                    cases.append(('IFNA(' + expression + ',77)',
                                  None, str(source_error)))
                for formula, result, code in cases:
                    with self.subTest(formula=formula, error=str(source_error)):
                        self.assertEqual(p.parse(formula),
                                         {'result': result, 'error': code})

    def test_index_can_select_a_value_before_an_array_error(self):
        p = Parser()
        p.set_function('DATA', lambda: [5, error.DIV_ZERO])
        self.assertEqual(p.parse('INDEX(DATA(),1)'),
                         {'result': 5, 'error': None})

    def test_raised_custom_excel_errors_reach_handlers(self):
        def fail():
            raise error.NOT_AVAILABLE

        p = Parser()
        p.set_function('FAIL', fail)
        self.assertEqual(p.parse('FAIL()'),
                         {'result': None, 'error': '#N/A'})
        self.assertEqual(p.parse('IFNA(FAIL(),77)'),
                         {'result': 77, 'error': None})

    def test_function_event_can_override_an_aggregate_error(self):
        def override(name, args, set_value):
            if name == 'SUM':
                set_value(12)

        p = Parser()
        p.set_function('DATA', lambda: [5, error.DIV_ZERO])
        p.on('callFunction', override)
        self.assertEqual(p.parse('SUM(DATA())'),
                         {'result': 12, 'error': None})

    def test_python_implementation_errors_still_abort_evaluation(self):
        def fail():
            raise ValueError('callback bug')

        p = Parser()
        p.set_function('FAIL', fail)
        self.assertEqual(p.parse('IFERROR(FAIL(),99)'),
                         {'result': None, 'error': '#ERROR!'})

    def test_div_zero(self):
        p = Parser()
        ret = p.parse('2/0')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')
        ret = p.parse('SUM(2/0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')
        ret = p.parse('SUM(1; 2/0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')
        ret = p.parse('SUM(2/0; 1)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')


    def test_wrong_syntax(self):
        p = Parser()
        ret = p.parse('2(6+2)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#ERROR!')
        ret = p.parse('2:5')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#ERROR!')


    def test_error_imaginary(self):
        p = Parser()
        ret = p.parse('IMAGINARY(#ERROR!)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#ERROR!')
        ret = p.parse('IMAGINARY(2/0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')
        ret = p.parse('IMAGINARY("")')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#NUM!')
        ret = p.parse('IMAGINARY(#N/A)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#N/A')

    def test_error_real(self):
        p = Parser()
        ret = p.parse('IMREAL(#ERROR!)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#ERROR!')
        ret = p.parse('IMREAL(2/0)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#DIV/0!')
        ret = p.parse('IMREAL("")')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#NUM!')
        ret = p.parse('IMREAL(#N/A)')
        self.assertEqual(ret['result'], None)
        self.assertEqual(ret['error'], '#N/A')
