# -*- coding: utf-8 -*-
import unittest
from hotxlfp import Parser
from hotxlfp.formulas import error, utils


class TestError(unittest.TestCase):
    """ Stuff that should cause errors """

    def test_conditional_functions_match_excel_criteria_with_error_cells(self):
        p = Parser()
        criteria_values = [1, error.DIV_ZERO, error.NOT_AVAILABLE, 2]
        data = [10, 20, 30, 40]
        for criterion, positions in (
            ('>0', [0, 3]), ('<2', [0]), ('>=1', [0, 3]), ('<=1', [0]),
            ('1', [0]), ('=1', [0]), ('<>1', [1, 2, 3]),
            ('#DIV/0!', [1]), ('=#DIV/0!', [1]), ('<>#DIV/0!', [0, 2, 3]),
            ('#N/A', [2]), ('<>#N/A', [0, 1, 3]),
            ('*', []), ('<>*', [0, 1, 2, 3]), ('=', []), ('<>', [0, 1, 2, 3]),
            ('x', []), ('<>x', [0, 1, 2, 3]), ('>#DIV/0!', [2]), ('<#DIV/0!', []),
        ):
            selected = [data[i] for i in positions]
            sumif_result = 0
            for i in positions:
                if isinstance(criteria_values[i], error.XLError):
                    sumif_result = criteria_values[i]
                    break
                sumif_result += criteria_values[i]
            for shape in (lambda values: values, lambda values: [values],
                          lambda values: [[value] for value in values]):
                p.set_function('CRITERIA', lambda: shape(criteria_values))
                p.set_function('DATA', lambda: shape(data))
                for name, args, expected in (
                    ('COUNTIF', 'CRITERIA(),"' + criterion + '"', len(selected)),
                    ('SUMIF', 'CRITERIA(),"' + criterion + '"', sumif_result),
                    ('AVERAGEIF', 'CRITERIA(),"' + criterion + '",DATA()',
                     sum(selected) / len(selected) if selected else error.DIV_ZERO),
                    ('SUMIFS', 'DATA(),CRITERIA(),"' + criterion + '"', sum(selected)),
                    ('AVERAGEIFS', 'DATA(),CRITERIA(),"' + criterion + '"',
                     sum(selected) / len(selected) if selected else error.DIV_ZERO),
                    ('MAXIFS', 'DATA(),CRITERIA(),"' + criterion + '"', max(selected, default=0)),
                ):
                    expression = name + '(' + args + ')'
                    result = ({'result': None, 'error': str(expected)}
                              if isinstance(expected, error.XLError)
                              else {'result': expected, 'error': None})
                    with self.subTest(expression=expression, shape=shape(data)):
                        self.assertEqual(p.parse(expression), result)

    def test_conditional_functions_match_typed_error_criteria(self):
        p = Parser()
        for source_error in (error.DIV_ZERO, error.NOT_AVAILABLE, error.NUM):
            p.set_function('ERR', lambda: source_error)
            for source in (str(source_error), 'ERR()'):
                for name, args, expected in (
                    ('COUNTIF', '{1,ERR()},' + source, 1),
                    ('SUMIF', '{1,ERR()},' + source, source_error),
                    ('AVERAGEIF', '{1,ERR()},' + source + ',{10,20}', 20),
                    ('SUMIFS', '{10,20},{1,ERR()},' + source, 20),
                    ('AVERAGEIFS', '{10,20},{1,ERR()},' + source, 20),
                    ('MAXIFS', '{10,20},{1,ERR()},' + source, 20),
                ):
                    expression = name + '(' + args + ')'
                    with self.subTest(expression=expression, error=str(source_error)):
                        result = ({'result': None, 'error': str(expected)}
                                  if isinstance(expected, error.XLError)
                                  else {'result': expected, 'error': None})
                        self.assertEqual(p.parse(expression), result)
                        fallback = 99 if isinstance(expected, error.XLError) else expected
                        self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                         {'result': fallback, 'error': None})
                        na_result = ({'result': 77, 'error': None}
                                     if expected is error.NOT_AVAILABLE else result)
                        self.assertEqual(p.parse('IFNA(' + expression + ',77)'), na_result)

    def test_typed_error_criteria_without_matching_cells(self):
        p = Parser()
        for source_error in (error.DIV_ZERO, error.NOT_AVAILABLE, error.NUM):
            for name, args, expected in (
                ('COUNTIF', '{1,2},', 0), ('SUMIF', '{1,2},', 0),
                ('AVERAGEIF', '{1,2},', error.DIV_ZERO),
                ('SUMIFS', '{10,20},{1,2},', 0),
                ('AVERAGEIFS', '{10,20},{1,2},', error.DIV_ZERO),
                ('MAXIFS', '{10,20},{1,2},', 0),
            ):
                expression = name + '(' + args + str(source_error) + ')'
                with self.subTest(expression=expression):
                    result = ({'result': None, 'error': str(expected)}
                              if isinstance(expected, error.XLError)
                              else {'result': expected, 'error': None})
                    self.assertEqual(p.parse(expression), result)

    def test_multiple_criteria_exclude_error_cells_in_either_order(self):
        p = Parser()
        for name, expected in (('SUMIFS', 50), ('AVERAGEIFS', 25), ('MAXIFS', 40)):
            for criteria in ('{1,#DIV/0!,#N/A,2},">0",{1,0,0,1},1',
                             '{1,0,0,1},1,{1,#DIV/0!,#N/A,2},">0"'):
                expression = name + '({10,20,30,40},' + criteria + ')'
                with self.subTest(expression=expression):
                    self.assertEqual(p.parse(expression), {'result': expected, 'error': None})
            expression = name + '({10,20},{1,2},">99",{3,#N/A},#N/A)'
            result = error.DIV_ZERO if name == 'AVERAGEIFS' else 0
            with self.subTest(expression=expression):
                expected = ({'result': None, 'error': str(result)}
                            if isinstance(result, error.XLError)
                            else {'result': result, 'error': None})
                self.assertEqual(p.parse(expression), expected)

    def test_averageif_preserves_only_selected_aggregate_errors(self):
        p = Parser()
        for expression, expected in (
            ('AVERAGEIF({1,#DIV/0!,#N/A,2},">0")', 1.5),
            ('AVERAGEIF({1,#DIV/0!,#N/A,2},"#DIV/0!")', error.DIV_ZERO),
            ('AVERAGEIF({1,#DIV/0!,#N/A,2},"#N/A")', error.NOT_AVAILABLE),
            ('AVERAGEIF({1,#DIV/0!,#N/A,2},"<>1")', error.DIV_ZERO),
        ):
            with self.subTest(expression=expression):
                result = ({'result': None, 'error': str(expected)}
                          if isinstance(expected, error.XLError)
                          else {'result': expected, 'error': None})
                self.assertEqual(p.parse(expression), result)
                fallback = 99 if isinstance(expected, error.XLError) else expected
                self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                 {'result': fallback, 'error': None})

    def test_numeric_consumers_preserve_errors_in_every_argument(self):
        p = Parser()
        for name, valid_args in (
            ('SLOPE', ['6', '1', '2', '4']),
            ('HEX2DEC', ['"A5"']),
            ('COMPLEX', ['3', '5']),
            ('DELTA', ['5', '5']),
            ('SIGN', ['2']),
            ('ISEVEN', ['2']),
            ('ISODD', ['3']),
            ('ROUND', ['23.7825', '2']),
            ('ROUNDUP', ['23.7825', '2']),
            ('ROUNDDOWN', ['23.7825', '2']),
            ('POWER', ['2', '3']),
            ('PV', ['0.1', '3', '-10']),
            ('PV', ['0.1', '3', '-10', '5', '1']),
            ('LOG', ['100']),
            ('LOG', ['100', '10']),
            ('CEILING', ['2.5']),
            ('CEILING', ['2.5', '1']),
            ('CEILING.MATH', ['2.5']),
            ('CEILING.MATH', ['2.5', '1']),
            ('CEILING.PRECISE', ['2.5']),
            ('CEILING.PRECISE', ['2.5', '1']),
            ('FLOOR', ['2.5']),
            ('FLOOR', ['2.5', '1']),
            ('FLOOR.MATH', ['2.5']),
            ('FLOOR.MATH', ['2.5', '1']),
            ('FLOOR.PRECISE', ['2.5']),
            ('FLOOR.PRECISE', ['2.5', '1']),
            ('QUOTIENT', ['5', '2']),
            ('INT', ['2.5']),
            ('RANDBETWEEN', ['1', '5']),
            ('ROMAN', ['14']),
            ('ROMAN', ['14', '0']),
            ('ARABIC', ['"XIV"']),
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

    def test_numeric_consumers_preserve_first_error_order(self):
        p = Parser()
        for name in ('ROUND', 'ROUNDUP', 'ROUNDDOWN', 'POWER', 'PV', 'LOG',
                     'CEILING', 'CEILING.MATH', 'CEILING.PRECISE',
                     'FLOOR', 'FLOOR.MATH', 'FLOOR.PRECISE',
                     'QUOTIENT', 'RANDBETWEEN', 'ROMAN', 'COMPLEX', 'DELTA',
                     'SLOPE'):
            for first, second in ((error.NOT_AVAILABLE, error.DIV_ZERO),
                                   (error.DIV_ZERO, error.NOT_AVAILABLE)):
                args = [str(first), str(second)]
                if name == 'PV':
                    args.append('1')
                expression = name + '(' + ','.join(args) + ')'
                with self.subTest(expression=expression):
                    self.assertEqual(p.parse(expression), {'result': None, 'error': str(first)})

    def test_numeric_consumers_keep_conversion_checks_and_valid_results(self):
        p = Parser()
        for expression, expected in (
            ('HEX2DEC("A5")', 165),
            ('COMPLEX("3","5")', complex(3, 5)),
            ('DELTA("5","5")', 1),
            ('ROUND(23.7825,2)', 23.78),
            ('ROUNDUP(23.7825,2)', 23.79),
            ('ROUNDDOWN(-23.7895,2)', -23.78),
            ('POWER("2","3")', 8),
            ('PV(0,2,10)', -20),
            ('PV(0,2,10,5)', -25),
            ('PV(0,2,10,5,1)', -25),
            ('PV(0,2,10,NULL,NULL)', -20),
            ('LOG(100)', 2),
            ('LOG(8,2)', 3),
            ('QUOTIENT(-10,3)', -3),
            ('INT(2.9)', 2),
            ('INT(-2.9)', -3),
            ('RANDBETWEEN(7,7)', 7),
            ('ROMAN(14)', 'XIV'),
            ('ARABIC("xiv")', 14),
        ):
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': expected, 'error': None})
        for name, valid_args in (
            ('HEX2DEC', ['"A5"']),
            ('COMPLEX', ['3', '5']), ('DELTA', ['5', '5']),
            ('SIGN', ['2']), ('ISEVEN', ['2']), ('ISODD', ['3']),
            ('ROUND', ['2', '1']), ('ROUNDUP', ['2', '1']),
            ('ROUNDDOWN', ['2', '1']), ('POWER', ['2', '3']),
            ('PV', ['0', '2', '10', '5', '1']),
            ('LOG', ['100', '10']),
            ('CEILING', ['2.5', '1']), ('CEILING.MATH', ['2.5', '1']),
            ('CEILING.PRECISE', ['2.5', '1']),
            ('FLOOR', ['2.5', '1']), ('FLOOR.MATH', ['2.5', '1']),
            ('FLOOR.PRECISE', ['2.5', '1']),
            ('QUOTIENT', ['5', '2']), ('INT', ['2.5']),
            ('RANDBETWEEN', ['1', '5']), ('ROMAN', ['14', '0']),
            ('ARABIC', ['"XIV"']),
        ):
            for position in range(len(valid_args)):
                args = valid_args.copy()
                args[position] = '"invalid"'
                expression = name + '(' + ','.join(args) + ')'
                with self.subTest(expression=expression):
                    self.assertEqual(p.parse(expression), {'result': None, 'error': '#VALUE!'})

    def test_math_aliases_keep_defaults_and_domain_checks(self):
        p = Parser()
        for name, expected in (('CEILING', 3), ('CEILING.MATH', 3),
                               ('CEILING.PRECISE', 3), ('FLOOR', 2),
                               ('FLOOR.MATH', 2), ('FLOOR.PRECISE', 2)):
            with self.subTest(name=name):
                self.assertEqual(p.parse(name + '(2.5)'), {'result': expected, 'error': None})
                self.assertEqual(p.parse(name + '(2.5,0)'), {'result': 0, 'error': None})
        for expression, code in (('QUOTIENT(1,0)', '#DIV/0!'),
                                  ('FLOOR(2.5,-1)', '#NUM!'),
                                  ('ROMAN(4000)', '#VALUE!'),
                                  ('ROMAN(14,5)', '#VALUE!'),
                                  ('ARABIC("invalid")', '#VALUE!')):
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': None, 'error': code})

    def test_conditional_aggregates_preserve_selected_errors(self):
        p = Parser()
        for name in ('SUMIFS', 'AVERAGEIFS', 'MAXIFS'):
            for source_error in (error.DIV_ZERO, error.NOT_AVAILABLE, error.NUM):
                for values, criteria in (
                    ([10, source_error], [1, 2]),
                    ([[10, source_error]], [[1, 2]]),
                    ([[10], [source_error]], [[1], [2]]),
                ):
                    p.set_function('DATA', lambda: values)
                    p.set_function('CRITERIA', lambda: criteria)
                    expressions = (name + '(DATA(),CRITERIA(),">0")',
                                   name + '({10,' + str(source_error) + '},{1,2},">0")')
                    for expression in expressions:
                        with self.subTest(expression=expression, values=values):
                            self.assertEqual(p.parse(expression),
                                             {'result': None, 'error': str(source_error)})
                            self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                             {'result': 99, 'error': None})
                            expected = ({'result': 77, 'error': None}
                                        if source_error is error.NOT_AVAILABLE
                                        else {'result': None, 'error': str(source_error)})
                            self.assertEqual(p.parse('IFNA(' + expression + ',77)'), expected)

    def test_conditional_aggregates_ignore_unselected_errors(self):
        p = Parser()
        p.set_function('DATA', lambda: [[error.DIV_ZERO, 10], [20, error.NOT_AVAILABLE]])
        p.set_function('FIRST', lambda: [[0, 1], [2, 3]])
        p.set_function('SECOND', lambda: [['x', 'x'], ['y', 'y']])
        for name in ('SUMIFS', 'AVERAGEIFS', 'MAXIFS'):
            expression = name + '(DATA(),FIRST(),">0",SECOND(),"x")'
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': 10, 'error': None})
            expression = name + '(DATA(),FIRST(),">9")'
            expected = ({'result': None, 'error': '#DIV/0!'} if name == 'AVERAGEIFS'
                        else {'result': 0, 'error': None})
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), expected)

    def test_conditional_aggregates_preserve_first_selected_error(self):
        p = Parser()
        p.set_function('CRITERIA', lambda: [[1, 2], [3, 4]])
        for first, second in ((error.DIV_ZERO, error.NOT_AVAILABLE),
                               (error.NOT_AVAILABLE, error.DIV_ZERO)):
            p.set_function('DATA', lambda: [[10, first], [second, 20]])
            for name in ('SUMIFS', 'AVERAGEIFS', 'MAXIFS'):
                expression = name + '(DATA(),CRITERIA(),">0")'
                with self.subTest(expression=expression, first=str(first)):
                    self.assertEqual(p.parse(expression), {'result': None, 'error': str(first)})

    def test_error_decorator_checks_direct_arguments_and_forwards_valid_values(self):
        calls = []

        @utils.propagate_errors()
        def echo(value):
            calls.append(value)
            return value

        self.assertIs(echo(error.NOT_AVAILABLE), error.NOT_AVAILABLE)
        self.assertIs(echo(value=error.DIV_ZERO), error.DIV_ZERO)
        self.assertEqual(calls, [])
        self.assertEqual(echo(value=7), 7)
        values = [error.NOT_AVAILABLE]
        self.assertIs(echo(values), values)
        self.assertEqual(calls, [7, values])
        with self.assertRaises(TypeError):
            echo()

    def test_error_decorator_checks_nested_arguments_before_calling_consumer(self):
        calls = []

        @utils.propagate_errors(nested=True)
        def consume(values):
            calls.append(values)
            return all(utils.iflatten(values))

        values = [False, (error.NOT_AVAILABLE, error.DIV_ZERO)]
        self.assertIs(consume(values), error.NOT_AVAILABLE)
        self.assertIs(consume(values=[False, [error.DIV_ZERO]]), error.DIV_ZERO)
        self.assertEqual(calls, [])
        self.assertIs(consume(values=[True, (1, 2)]), True)
        self.assertEqual(calls, [[True, (1, 2)]])

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

    def test_returned_and_raised_excel_errors_reach_consumers_identically(self):
        p = Parser()
        for source_error in (error.ERROR, error.DIV_ZERO, error.NAME,
                             error.NOT_AVAILABLE, error.NULL, error.NUM,
                             error.REF, error.VALUE, error.DATA):
            def return_error():
                return source_error

            def raise_error():
                raise source_error

            for implementation in (return_error, raise_error):
                p.set_function('FAIL', implementation)
                cases = [
                    ('FAIL()', None, str(source_error)),
                    ('IFERROR(FAIL(),99)', 99, None),
                    ('ISERROR(FAIL())', True, None),
                    ('COUNT(FAIL())', 0, None),
                    ('COUNTA(FAIL())', 1, None),
                ]
                cases.append(('IFNA(FAIL(),77)', 77, None)
                             if source_error is error.NOT_AVAILABLE
                             else ('IFNA(FAIL(),77)', None, str(source_error)))
                with self.subTest(error=str(source_error),
                                  implementation=implementation.__name__):
                    self.assertIs(p.call_function('FAIL'), source_error)
                    for formula, result, code in cases:
                        with self.subTest(formula=formula):
                            self.assertEqual(p.parse(formula),
                                             {'result': result, 'error': code})

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
        p = Parser()
        for exception_type in (ValueError, TypeError):
            def fail():
                raise exception_type('callback bug')

            p.set_function('FAIL', fail)
            with self.subTest(exception_type=exception_type):
                with self.assertRaises(exception_type):
                    p.call_function('FAIL')
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
