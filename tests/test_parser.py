import datetime
import unittest
from hotxlfp import Parser, formulas
from hotxlfp.formulas import error



class TestParser(unittest.TestCase):

    def test_scalar_cell_callbacks_receive_parsed_coordinates(self):
        parser = Parser()
        calls = []
        table = [[row * 100 + col for col in range(27)] for row in range(10)]

        def cell_value(cell, set_value):
            calls.append(cell)
            set_value(table[cell.row.index][cell.col.index])

        parser.on('callCellValue', cell_value)
        for label, normalized, row, col, row_absolute, col_absolute in (
            ('B1', 'B1', 0, 1, False, False),
            ('a10', 'A10', 9, 0, False, False),
            ('$AA$10', '$AA$10', 9, 26, True, True),
            ('$B1', '$B1', 0, 1, False, True),
            ('A$10', 'A$10', 9, 0, True, False),
        ):
            with self.subTest(label=label):
                self.assertEqual(parser.parse(label),
                                 {'result': table[row][col], 'error': None})
                cell = calls[-1]
                self.assertEqual(cell.label, normalized)
                self.assertEqual((cell.row.index, cell.col.index), (row, col))
                self.assertEqual((cell.row.is_absolute, cell.col.is_absolute),
                                 (row_absolute, col_absolute))

    def test_array_functions_accept_scalar_cell_and_range_callbacks(self):
        parser = Parser()
        table = [[10], [20]]

        def cell_value(cell, set_value):
            set_value(table[cell.row.index][cell.col.index])

        def range_value(start, end, set_value):
            set_value([row[start.col.index:end.col.index + 1]
                       for row in table[start.row.index:end.row.index + 1]])

        parser.on('callCellValue', cell_value)
        parser.on('callRangeValue', range_value)
        for name in ('TOCOL', 'TOROW', 'UNIQUE'):
            for source, expected in (
                ('$A$1', [[10]]),
                ('A1:A2', [[10, 20]] if name == 'TOROW' else [[10], [20]]),
            ):
                with self.subTest(name=name, source=source):
                    self.assertEqual(parser.parse(name + '(' + source + ')'),
                                     {'result': expected, 'error': None})

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
        for value in (12, 0, False, '', None, error.NOT_AVAILABLE):
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

    def test_function_events_can_replace_results_with_blank(self):
        def clear(name, args, set_value):
            if name == 'CUSTOM':
                set_value(None)

        for value in (12, error.DIV_ZERO):
            with self.subTest(value=value):
                parser = Parser()
                parser.set_function('CUSTOM', lambda: value)
                parser.on('callFunction', clear)
                self.assertEqual(parser.parse('CUSTOM()'),
                                 {'result': None, 'error': None})
                self.assertEqual(parser.parse('ISBLANK(CUSTOM())'),
                                 {'result': True, 'error': None})

    def test_event_setters_distinguish_blank_from_no_override(self):
        cases = [
            ('callFunction', 'CUSTOM()', 12),
            ('callVariable', 'supplied_name', 12),
            ('callCellValue', 'A1', 12),
            ('callRangeValue', 'A1:A2', [[12], [13]]),
        ]
        for event, expression, value in cases:
            with self.subTest(event=event):
                parser = Parser()
                parser.set_function('CUSTOM', lambda: 7)

                # Every event passes its setter as the last argument.
                def supply(*args):
                    args[-1](value)

                def leave_unchanged(*args):
                    pass

                def clear(*args):
                    args[-1](None)

                parser.on(event, supply)
                parser.on(event, leave_unchanged)
                self.assertEqual(parser.parse(expression),
                                 {'result': value, 'error': None})
                parser.on(event, clear)
                self.assertEqual(parser.parse(expression),
                                 {'result': None, 'error': None})

    def test_nonfinite_numbers_are_errors_before_consumers_run(self):
        for value in (float('nan'), float('inf'), float('-inf'),
                      complex(float('nan'), 0), complex(0, float('inf'))):
            parser = Parser()
            parser.set_function('BAD', lambda: value)
            parser.set_variable('bad_value', value)
            parser.on('callCellValue', lambda cell, set_value: set_value(value))
            for source in ('BAD()', 'bad_value', 'A1'):
                for expression in (source, source + '=0', '-' + source):
                    with self.subTest(value=value, expression=expression):
                        self.assertEqual(parser.parse(expression),
                                         {'result': None, 'error': '#NUM!'})
                        self.assertEqual(parser.parse('IFERROR(' + expression + ',99)'),
                                         {'result': 99, 'error': None})

    def test_numeric_validation_uses_final_callback_values(self):
        sources = [('callFunction', 'DATA()'),
                   ('callVariable', 'input_value'),
                   ('callCellValue', 'A1'),
                   ('callRangeValue', 'A1:A2')]
        cases = [(float('nan'), error.NUM), (float('inf'), error.NUM),
                 (float('-inf'), error.NUM)]
        cases.extend((value, value) for value in (
            0, -2.5, 10 ** 400, complex(3, 4), True, False,
            None, '', '7', 'NaN', 'inf', '2026-11-11',
            datetime.date(2026, 11, 11), error.DIV_ZERO,
        ))
        for event, expression in sources:
            for value, expected_value in cases:
                with self.subTest(event=event, value=value):
                    parser = Parser()
                    parser.set_function('DATA', lambda: float('nan'))
                    parser.set_variable('input_value', float('nan'))
                    parser.on(event, lambda *args: args[-1](float('nan')))
                    parser.on(event, lambda *args: args[-1](value))
                    if isinstance(expected_value, error.XLError):
                        expected = {'result': None, 'error': str(expected_value)}
                    else:
                        expected = {'result': expected_value, 'error': None}
                    actual = parser.parse(expression)
                    self.assertEqual(actual, expected)
                    self.assertIs(type(actual['result']), type(expected['result']))

    def test_numeric_validation_preserves_array_shape_and_error_elements(self):
        invalid = float('nan')
        values = [(invalid, '7', None), [float('inf'), 3.5]]
        expected = [(error.NUM, '7', None), [error.NUM, 3.5]]
        parser = Parser()
        parser.set_function('DATA', lambda: values)
        parser.set_variable('input_values', values)
        parser.on('callCellValue', lambda cell, set_value: set_value(values))
        parser.on('callRangeValue',
                  lambda start, end, set_value: set_value(values))
        for source in ('DATA()', 'input_values', 'A1', 'A1:A2'):
            cases = [
                (source, expected, None),
                ('IFERROR(' + source + ',0)', [(0, '7', None), [0, 3.5]], None),
                ('COUNT(' + source + ')', 2, None),
                ('SUM(' + source + ')', None, '#NUM!'),
            ]
            for expression, result, code in cases:
                with self.subTest(expression=expression):
                    self.assertEqual(parser.parse(expression),
                                     {'result': result, 'error': code})
        self.assertIs(values[0][0], invalid)

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
