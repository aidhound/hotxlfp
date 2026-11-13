import unittest
from hotxlfp import Parser, formulas
from hotxlfp.formulas import error



class TestParser(unittest.TestCase):

    def test_builtin_function_names_are_case_insensitive(self):
        parser = Parser()
        for expression, expected in [('sum(1,2)', 3), ('aVeRaGe(5,10)', 7.5),
                                      ('sTdEv.p(1,3)', 1)]:
            with self.subTest(expression=expression):
                self.assertEqual(parser.parse(expression),
                                 {'result': expected, 'error': None})

    def test_custom_function_names_are_case_insensitive(self):
        parser = Parser()
        triple = lambda value: value * 3
        parser.set_function('TrIpLe', triple)
        for name in ('TRIPLE', 'triple', 'TrIpLe'):
            with self.subTest(name=name):
                self.assertIs(parser.get_function(name), triple)
                self.assertEqual(parser.parse(name + '(2)'),
                                 {'result': 6, 'error': None})

    def test_function_registration_replaces_different_casing(self):
        parser = Parser()
        parser.set_function('CUSTOM', lambda: 7)
        replacement = lambda: 12
        parser.set_function('custom', replacement)
        for name in ('CUSTOM', 'custom', 'CuStOm'):
            with self.subTest(name=name):
                self.assertIs(parser.get_function(name), replacement)
                self.assertEqual(parser.parse(name + '()'),
                                 {'result': 12, 'error': None})

    def test_custom_function_overrides_builtin_in_all_casings(self):
        parser = Parser()
        parser.set_function('average', lambda *args: 42)
        for name in ('average', 'AVERAGE', 'aVeRaGe'):
            with self.subTest(name=name):
                self.assertEqual(parser.parse(name + '(5,10)'),
                                 {'result': 42, 'error': None})

    def test_function_casing_preserves_strings_variables_and_events(self):
        parser = Parser()
        parser.set_function('EcHo', lambda value: value)
        parser.set_variable('MiXeD', 7)
        parser.set_variable('mixed', 11)
        calls = []
        parser.on('callFunction',
                  lambda name, args, setter: calls.append((name, args)))
        self.assertEqual(parser.parse('eChO("MiXeD")'),
                         {'result': 'MiXeD', 'error': None})
        self.assertEqual(parser.parse('sUm(MiXeD,mixed)'),
                         {'result': 18, 'error': None})
        self.assertEqual(calls, [('eChO', ['MiXeD']), ('sUm', [7, 11])])

    def test_unknown_builtin_lookup_raises_name_error(self):
        self.assertTrue(callable(formulas.get_for('SUM')))
        with self.assertRaises(error.XLError) as caught:
            formulas.get_for('MISSING')
        self.assertIs(caught.exception, error.NAME)

    def test_unknown_functions_return_handleable_name_errors(self):
        parser = Parser()
        for expression in ('MISSING()', 'missing(1)+2', 'SUM(MISSING(),2)'):
            with self.subTest(expression=expression):
                self.assertEqual(parser.parse(expression),
                                 {'result': None, 'error': '#NAME?'})
        self.assertEqual(parser.parse('IFERROR(MISSING(),99)'),
                         {'result': 99, 'error': None})
        self.assertEqual(parser.parse('SUM(1,2)'),
                         {'result': 3, 'error': None})

    def test_custom_blank_results_remain_valid(self):
        parser = Parser()
        parser.set_function('BLANK', lambda: None)
        self.assertEqual(parser.parse('blank()'),
                         {'result': None, 'error': None})
        self.assertEqual(parser.parse('IFERROR(blank(),99)'),
                         {'result': None, 'error': None})

    def test_unknown_variables_return_handleable_name_errors(self):
        parser = Parser()
        for expression in ('missing_name', 'missing_name+2',
                           'SUM(missing_name,2)'):
            with self.subTest(expression=expression):
                self.assertEqual(parser.parse(expression),
                                 {'result': None, 'error': '#NAME?'})
        self.assertEqual(parser.parse('IFERROR(missing_name,99)'),
                         {'result': 99, 'error': None})
        self.assertEqual(parser.parse('ISERROR(missing_name)'),
                         {'result': True, 'error': None})
        parser.set_variable('known_name', 7)
        self.assertEqual(parser.parse('known_name'),
                         {'result': 7, 'error': None})

    def test_variable_events_can_resolve_or_override_values(self):
        for value in (12, 0, False, '', error.NOT_AVAILABLE):
            with self.subTest(value=value):
                parser = Parser()

                def override(name, set_value):
                    if name == 'supplied_name':
                        set_value(value)

                parser.on('callVariable', override)
                expected = ({'result': None, 'error': '#N/A'}
                            if value is error.NOT_AVAILABLE
                            else {'result': value, 'error': None})
                self.assertEqual(parser.parse('supplied_name'), expected)
                parser.set_variable('supplied_name', 7)
                self.assertEqual(parser.parse('supplied_name'), expected)
                self.assertEqual(parser.parse('IFERROR(missing_name,99)'),
                                 {'result': 99, 'error': None})

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
