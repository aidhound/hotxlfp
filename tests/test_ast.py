# -*- coding: utf-8 -*-
import json
import datetime
import unittest
from hotxlfp import Parser
from hotxlfp.formulas import utils
from hotxlfp.formulas.dateandtime import YEAR, MONTH, DAY, DAYS, EDATE, DATE


def make_parser():
    """ A parser with the kind of custom functions the consumer registers. """
    p = Parser()
    p.set_function('F', lambda x=0: x * 2)
    p.set_function('C', lambda *args: 'C')
    return p


# Formulas that parse successfully (non-None AST). Covers numbers, strings,
# nested calls, every operator, unary minus, percent, arrays, error literals,
# variables (TRUE/FALSE/NULL) and custom registered functions.
CORPUS = [
    # numbers
    '0', '42', '1.5', '.5', '50%', '10%+5', '2^3', '2^10',
    # strings
    '"hello"', '""', '"a,b)"', '"with \\" quote"',
    # arithmetic operators
    '1+2', '5-3', '4*2', '8/4', '1+2*3', '(1+2)*3', '2&3', '"a"&"b"&"c"',
    # logic operators
    '1<2', '2>1', '2<=2', '2>=3', '1=1', '1<>2', '3<>3',
    # unary minus / percent / nesting
    '-5', '-(1+2)', '--3', '-2^2', '-.5',
    # arrays
    '{1,2,3}', '{1;2;3}', '{1,2;3,4}', '{1\\2\\3}', '{1,2,3}/2', '2/{1;2;4}',
    # error literals
    '#REF!', '#N/A', '#DIV/0!', '#VALUE!', '#NAME?', '#NULL!', '#NUM!',
    # variables
    'TRUE', 'FALSE', 'NULL', 'TRUE=TRUE', 'IF(TRUE,1,2)', 'IF(FALSE,1,2)',
    # builtin functions, nested
    'SUM(1,2,3)', 'SUM(1;2;{4;5};"aa")', 'MAX(1,2,3)', 'MIN(3,4)',
    'SUM(MAX(1,2),MIN(3,4))', 'CONCATENATE("a","b","c")', 'ROUND(3.14159,2)',
    'AND(TRUE,FALSE)', 'NOT(TRUE)', 'LEN("hello")', 'IF(AND(TRUE,TRUE),"x","y")',
    # empty arguments
    'INDEX({1,2,3},,2)', 'INDEX({1;2;3};2;)', 'INDEX({1,2,3;4,5,6};;2)',
    'INDEX({1\\2\\3\\4;5\\6\\7\\8};2;1)',
    # custom registered functions
    'F(5)', 'F(F(3))', 'C(1,2,3)', 'C()', 'F(5)+C(1)', 'SUM(F(1),F(2))',
    # things that evaluate to errors but parse fine
    '1/0', 'MY_UNDEFINED', 'NOPE(1)',
]


# Pinned current ``parse()`` outputs so behaviour cannot drift.
REGRESSION_CASES = [
    ('1+2', 3, None),
    ('2*3-4/2', 4.0, None),
    ('2^3', 8, None),
    ('50%', 0.5, None),
    ('-5', -5, None),
    ('.5', 0.5, None),
    ('1.5', 1.5, None),
    ('"a"&"b"', 'ab', None),
    ('"x"&5', 'x5', None),
    ('1<2', True, None),
    ('2<=2', True, None),
    ('3>=4', False, None),
    ('3>2', True, None),
    ('1=1', True, None),
    ('3<>3', False, None),
    ('SUM(1,2,3)', 6, None),
    ('SUM(1;2;{4;5};"aa")', 12, None),
    ('IF(TRUE,1,2)', 1, None),
    ('IF(FALSE,1,2)', 2, None),
    ('TRUE', True, None),
    ('FALSE', False, None),
    ('NULL', None, None),
    ('#REF!', None, '#REF!'),
    ('1/0', None, '#DIV/0!'),
    ('MY_UNDEFINED', None, '#NAME?'),
    ('(1+2)*3', 9, None),
    ('ROUND(3.14159,2)', 3.14, None),
    ('CONCATENATE("a","b","c")', 'abc', None),
    ('F(21)', 42, None),
    ('C(1,2)', 'C', None),
    ('NOT(TRUE)', False, None),
    ('AND(TRUE,FALSE)', False, None),
    ('-2^2', -4, None),
    ('--5', 5, None),
    ('10%+1', 1.1, None),
    ('2&3', '23', None),
    ('{1,2,3}', [1, 2, 3], None),
    ('MAX(1,2,3)', 3, None),
    ('AVERAGE(2,4,6)', 4, None),
    ('LEN("hello")', 5, None),
    ('F(F(2))', 8, None),
]


class TestASTEquivalence(unittest.TestCase):

    def test_evaluate_ast_matches_parse(self):
        """ evaluate_ast(parse_to_ast(f)) must equal parse(f) for the corpus. """
        p = make_parser()
        for f in CORPUS:
            ast_result = p.parse_to_ast(f)
            self.assertIsNone(ast_result['error'], 'unexpected parse error for %r' % f)
            self.assertIsNotNone(ast_result['ast'], 'no AST produced for %r' % f)
            via_ast = p.evaluate_ast(ast_result['ast'])
            direct = p.parse(f)
            self.assertEqual(via_ast, direct, 'mismatch for %r: %r != %r' % (f, via_ast, direct))

    def test_evaluate_ast_matches_parse_with_cells(self):
        """ Equivalence holds for cell / range references resolved via callbacks. """
        table = [[0, 10], [1, 11], [2, 12], [3, 13], [4, 14]]

        def cellvalue(cell, valsetter):
            valsetter(table[cell.row.index][cell.col.index])

        def rangevalue(start, end, valsetter):
            result = []
            for i in range(start.row.index, end.row.index + 1):
                result.append(table[i][start.col.index:end.col.index + 1])
            valsetter(result)

        p = make_parser()
        p.on('callCellValue', cellvalue)
        p.on('callRangeValue', rangevalue)
        for f in ['A1', 'B3', 'A1+B1', 'SUM(A1:A5)', 'SUM(A1:B2)', 'A1:A5']:
            ast_result = p.parse_to_ast(f)
            via_ast = p.evaluate_ast(ast_result['ast'])
            direct = p.parse(f)
            self.assertEqual(via_ast, direct, 'cell mismatch for %r' % f)

    def test_json_round_trip(self):
        """ Every corpus AST must survive a JSON dump/load unchanged. """
        p = make_parser()
        for f in CORPUS:
            ast = p.parse_to_ast(f)['ast']
            self.assertEqual(json.loads(json.dumps(ast)), ast, 'json round-trip failed for %r' % f)

    def test_parse_regression(self):
        """ Pinned parse() outputs must not drift. """
        p = make_parser()
        for f, result, error in REGRESSION_CASES:
            ret = p.parse(f)
            self.assertEqual(ret['result'], result, 'result drift for %r' % f)
            self.assertEqual(ret['error'], error, 'error drift for %r' % f)


class TestASTShape(unittest.TestCase):

    def setUp(self):
        self.p = make_parser()

    def ast(self, f):
        return self.p.parse_to_ast(f)['ast']

    def test_node_shapes(self):
        self.assertEqual(self.ast('42'), ['num', 42])
        self.assertEqual(self.ast('1.5'), ['num', 1.5])
        self.assertEqual(self.ast('"hi"'), ['str', 'hi'])
        self.assertEqual(self.ast('#REF!'), ['err', '#REF!'])
        self.assertEqual(self.ast('TRUE'), ['var', 'TRUE'])
        self.assertEqual(self.ast('1+2'), ['binop', '+', ['num', 1], ['num', 2]])
        self.assertEqual(self.ast('"a"&"b"'), ['binop', '&', ['str', 'a'], ['str', 'b']])
        self.assertEqual(self.ast('1<=2'), ['binop', '<=', ['num', 1], ['num', 2]])
        self.assertEqual(self.ast('2^3'), ['binop', '^', ['num', 2], ['num', 3]])
        self.assertEqual(self.ast('-5'), ['unary', '-', ['num', 5]])
        self.assertEqual(self.ast('50%'), ['unary', '%', ['num', 50]])
        self.assertEqual(self.ast('{1,2}'), ['array', [['num', 1], ['num', 2]]])
        self.assertEqual(self.ast('SUM(1,2)'), ['call', 'SUM', [['num', 1], ['num', 2]]])
        self.assertEqual(self.ast('F()'), ['call', 'F', []])

    def test_empty_argument_node(self):
        # The added "empty" tag represents an omitted argument.
        self.assertEqual(
            self.ast('INDEX({1,2,3},,2)'),
            ['call', 'INDEX', [['array', [['num', 1], ['num', 2], ['num', 3]]], ['empty'], ['num', 2]]]
        )

    def test_paren_is_structural(self):
        # Parentheses only affect grouping; no dedicated node.
        self.assertEqual(self.ast('(1+2)*3'),
                         ['binop', '*', ['binop', '+', ['num', 1], ['num', 2]], ['num', 3]])

    def test_cell_and_range_nodes(self):
        self.assertEqual(self.ast('A1'), ['cell', 'A1'])
        self.assertEqual(self.ast('A1:B2'), ['range', 'A1', 'B2'])


class TestValidate(unittest.TestCase):

    def setUp(self):
        self.p = make_parser()

    def test_valid_formula(self):
        self.assertEqual(self.p.validate('SUM(1,2,3)'), [])
        self.assertEqual(self.p.validate('IF(TRUE, F(1), C(2))'), [])
        self.assertEqual(self.p.validate('(1+2)*3 - 4/2'), [])

    def test_unbalanced_parens(self):
        errors = self.p.validate('(1+2')
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]['kind'], 'syntax')
        self.assertEqual(errors[0]['position'], 4)

    def test_extra_close_paren_position(self):
        errors = self.p.validate('1+2)')
        self.assertEqual(errors[0]['kind'], 'syntax')
        self.assertEqual(errors[0]['position'], 3)
        self.assertEqual(errors[0]['token'], ')')

    def test_trailing_operator(self):
        errors = self.p.validate('1+')
        self.assertEqual(errors[0]['kind'], 'syntax')
        self.assertEqual(errors[0]['position'], 2)

    def test_bad_token(self):
        errors = self.p.validate('1 @ 2')
        self.assertEqual(errors[0]['kind'], 'syntax')
        self.assertEqual(errors[0]['position'], 2)
        self.assertEqual(errors[0]['token'], '@')

    def test_unknown_function(self):
        errors = self.p.validate('NOPE(1) + 2')
        kinds = [(e['kind'], e['function']) for e in errors]
        self.assertIn(('unknown_function', 'NOPE'), kinds)

    def test_registered_functions_not_flagged(self):
        # F and C are registered, so they must not be reported as unknown.
        self.assertEqual(self.p.validate('F(1) + C(2,3)'), [])

    def test_nested_unknown_function(self):
        errors = self.p.validate('SUM(1, BOGUS(2))')
        functions = [e['function'] for e in errors if e['kind'] == 'unknown_function']
        self.assertEqual(functions, ['BOGUS'])

    def test_arity_too_few(self):
        # DAYS requires two arguments.
        errors = self.p.validate('DAYS(1)')
        kinds = [e['kind'] for e in errors]
        self.assertIn('arity', kinds)

    def test_arity_ok(self):
        self.assertEqual(self.p.validate('DAYS(1, 2)'), [])

    def test_validate_does_not_raise_on_garbage(self):
        for f in ['', ')(', '*/', '1++', '{', '@@@', 'SUM(', ',,,']:
            # must return a list, never raise
            self.assertIsInstance(self.p.validate(f), list)

    def test_validate_does_not_evaluate(self):
        # A formula that would error on evaluation is still syntactically valid.
        self.assertEqual(self.p.validate('1/0'), [])


class TestDateInput(unittest.TestCase):

    def test_parse_date_accepts_date(self):
        self.assertEqual(utils.parse_date(datetime.date(2020, 1, 1)),
                         datetime.datetime(2020, 1, 1))

    def test_parse_date_datetime_keeps_time(self):
        dt = datetime.datetime(2020, 1, 1, 13, 30, 15)
        self.assertEqual(utils.parse_date(dt), dt)

    def test_year_month_day_with_date(self):
        d = datetime.date(2020, 5, 15)
        self.assertEqual(YEAR(d), 2020)
        self.assertEqual(MONTH(d), 5)
        self.assertEqual(DAY(d), 15)

    def test_days_with_date(self):
        self.assertEqual(DAYS(datetime.date(2020, 1, 2), datetime.date(2020, 1, 1)), 1)

    def test_edate_with_date(self):
        self.assertEqual(EDATE(datetime.date(2020, 1, 15), 1),
                         datetime.datetime(2020, 2, 15))

    def test_existing_inputs_unchanged(self):
        # serial number, datetime and string inputs behave exactly as before.
        serial = utils.serialize_date(datetime.datetime(2020, 1, 1))
        self.assertEqual(utils.parse_date(serial), datetime.datetime(2020, 1, 1))
        self.assertEqual(YEAR('2020-05-15'), 2020)
        self.assertEqual(DAYS(DATE(2020, 1, 2), DATE(2020, 1, 1)), 1)

    def test_date_via_parser_variable(self):
        self.p = make_parser()
        self.p.set_variable('d', datetime.date(2021, 7, 4))
        self.assertEqual(self.p.parse('YEAR(d)'), {'result': 2021, 'error': None})


if __name__ == '__main__':
    unittest.main()
