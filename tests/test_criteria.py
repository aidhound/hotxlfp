# -*- coding: utf-8 -*-
import unittest
from hotxlfp import Parser
from hotxlfp.formulas import error, utils


class TestCriteria(unittest.TestCase):

    def test_numeric_text_equality_keeps_ordering_and_inequality_distinct(self):
        values = ['1', '1.0', '+1', '01', '1e0', ' 1 ', '0', '0.0',
                  'NaN', '1e309', '1x', True, False, 1, 0]
        for criterion, positions in (
            (1, [0, 1, 2, 3, 4, 5, 13]), (0, [6, 7, 14]),
            ('=1', [0, 1, 2, 3, 4, 5, 13]),
            ('<>1', list(range(13)) + [14]),
            ('>0', [13]), ('>=1', [13]), ('<2', [13, 14]), ('<=1', [13, 14]),
        ):
            with self.subTest(criterion=criterion):
                predicate = utils.parse_criteria(criterion)
                self.assertEqual([i for i, value in enumerate(values) if predicate(value)],
                                 positions)

    def test_countif_numeric_equality_on_isolated_cell_types(self):
        p = Parser()
        for value, one_count, zero_count in (
            ('1', 1, 0), ('1.0', 1, 0), ('+1', 1, 0), ('01', 1, 0),
            ('1e0', 1, 0), (' 1 ', 1, 0), ('0', 0, 1), ('0.0', 0, 1),
            (1, 1, 0), (0, 0, 1), (True, 0, 0), (False, 0, 0),
            ('NaN', 0, 0), ('1e309', 0, 0), ('1x', 0, 0),
        ):
            p.set_function('DATA', lambda value=value: [value])
            for criterion, expected in (
                ('1', one_count), ('"=1"', one_count),
                ('0', zero_count), ('"=0"', zero_count),
            ):
                expression = 'COUNTIF(DATA(),' + criterion + ')'
                with self.subTest(value=value, expression=expression):
                    self.assertEqual(p.parse(expression),
                                     {'result': expected, 'error': None})

    def test_numeric_text_masks_select_values_without_boolean_or_nonfinite_rows(self):
        p = Parser()
        p.set_function('VALUES', lambda: [10, 20, error.NOT_AVAILABLE, error.DIV_ZERO])
        p.set_function('FLAGS', lambda: ['1', '2', True, 'NaN'])
        for name in ('SUMIFS', 'AVERAGEIFS'):
            expression = name + '(VALUES(),FLAGS(),1)'
            with self.subTest(expression=expression):
                self.assertEqual(p.parse(expression), {'result': 10, 'error': None})
                self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                 {'result': 10, 'error': None})

    def test_logical_criteria_match_boolean_cells_and_preserve_categories(self):
        values = [True, False, 'TRUE', 'FALSE', 1, 0, None, '', error.NOT_AVAILABLE]
        for criterion, positions in (
            (True, [0]), (False, [1]), ('true', [0]), ('False', [1]),
            ('=TrUe', [0]), ('<>TRUE', list(range(1, 9))),
            ('<>FALSE', [0, 2, 3, 4, 5, 6, 7, 8]),
            ('>TRUE', []), ('>=TRUE', [0]), ('<TRUE', [1]), ('<=TRUE', [0, 1]),
            ('>FALSE', [0]), ('>=FALSE', [0, 1]), ('<FALSE', []), ('<=FALSE', [1]),
            ('TRUE*', [2]),
        ):
            with self.subTest(criterion=criterion):
                predicate = utils.parse_criteria(criterion)
                self.assertEqual([i for i, value in enumerate(values) if predicate(value)],
                                 positions)

    def test_countif_logical_criteria_on_isolated_cell_types(self):
        p = Parser()
        for value, true_count, false_count in (
            (True, 1, 0), (False, 0, 1), (1, 0, 0), (0, 0, 0),
            ('TRUE', 0, 0), ('FALSE', 0, 0), (None, 0, 0), ('', 0, 0),
            (error.NOT_AVAILABLE, 0, 0),
        ):
            p.set_function('DATA', lambda value=value: [value])
            for criterion, expected in (
                ('TRUE()', true_count), ('FALSE()', false_count),
                ('"TRUE"', true_count), ('"false"', false_count),
            ):
                expression = 'COUNTIF(DATA(),' + criterion + ')'
                with self.subTest(value=value, expression=expression):
                    self.assertEqual(p.parse(expression),
                                     {'result': expected, 'error': None})

    def test_logical_criteria_exclude_error_rows_with_numeric_or_text_masks(self):
        p = Parser()
        p.set_function('VALUES', lambda: [10, error.NOT_AVAILABLE, error.DIV_ZERO,
                                         20, error.NOT_AVAILABLE, error.DIV_ZERO])
        p.set_function('FLAGS', lambda: [True, 1, 'TRUE', False, 0, 'FALSE'])
        for name in ('SUMIFS', 'AVERAGEIFS'):
            for criterion, expected in (
                ('TRUE()', 10), ('"TRUE"', 10),
                ('FALSE()', 20), ('"FALSE"', 20),
            ):
                expression = name + '(VALUES(),FLAGS(),' + criterion + ')'
                with self.subTest(expression=expression):
                    self.assertEqual(p.parse(expression),
                                     {'result': expected, 'error': None})
                    self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                     {'result': expected, 'error': None})

    def test_numeric_criteria_keep_boolean_cells_separate(self):
        values = [True, False, -1, 0, 1, 2]
        for criterion, positions in (
            (1, [4]), (0, [3]), ('1', [4]), ('=0', [3]),
            ('<>1', [0, 1, 2, 3, 5]), ('<>0', [0, 1, 2, 4, 5]),
            ('>0', [4, 5]), ('>=0', [3, 4, 5]),
            ('<1', [2, 3]), ('<=1', [2, 3, 4]),
        ):
            with self.subTest(criterion=criterion):
                predicate = utils.parse_criteria(criterion)
                self.assertEqual([i for i, value in enumerate(values) if predicate(value)],
                                 positions)

    def test_countif_numeric_criteria_on_isolated_boolean_cells(self):
        p = Parser()
        for value in (True, False):
            p.set_function('DATA', lambda value=value: [value])
            for criterion, expected in (
                ('1', 0), ('0', 0), ('"=1"', 0), ('"=0"', 0),
                ('"<>1"', 1), ('"<>0"', 1), ('">0"', 0),
                ('">=0"', 0), ('"<1"', 0), ('"<=1"', 0),
            ):
                expression = 'COUNTIF(DATA(),' + criterion + ')'
                with self.subTest(value=value, expression=expression):
                    self.assertEqual(p.parse(expression),
                                     {'result': expected, 'error': None})

    def test_numeric_criteria_exclude_errors_in_boolean_mask_rows(self):
        p = Parser()
        p.set_function('VALUES', lambda: [error.NOT_AVAILABLE, error.DIV_ZERO, 7])
        p.set_function('FLAGS', lambda: [True, False, 1])
        for name in ('SUMIFS', 'AVERAGEIFS'):
            for criterion in ('1', '">0"'):
                expression = name + '(VALUES(),FLAGS(),' + criterion + ')'
                with self.subTest(expression=expression):
                    self.assertEqual(p.parse(expression), {'result': 7, 'error': None})
                    self.assertEqual(p.parse('IFERROR(' + expression + ',99)'),
                                     {'result': 7, 'error': None})

    def test_wildcard_escapes_match_literal_characters(self):
        values = ['*', '?', 'a*b', 'a?b', '~*', '~?', '~', '~~', 'a~',
                  'a', 'A', '~a', 'a~b', '1', '~1', 'abc', '[ab]',
                  None, 1, error.NOT_AVAILABLE]
        for criterion, positions in (
            ('~*', [0]), ('~?', [1]), ('a~*b', [2]), ('a~?b', [3]),
            ('~~~*', [4]), ('~~~?', [5]), ('*~~', [6, 7, 8]),
            ('*~', list(range(17))),
            ('*~a*', [2, 3, 8, 9, 10, 11, 12, 15, 16]),
            ('*~1*', [13, 14]), ('~~', [7]), ('~a', [11]), ('~', [6]),
        ):
            for op in ('', '=', '<>'):
                expected = ([i for i in range(len(values)) if i not in positions]
                            if op == '<>' else positions)
                with self.subTest(criterion=op + criterion):
                    predicate = utils.parse_criteria(op + criterion)
                    self.assertEqual([i for i, value in enumerate(values) if predicate(value)],
                                     expected)

    def test_wildcards_keep_brackets_and_regex_characters_literal(self):
        values = ['[ab]', 'abc', '[AB]tail', 'abctail', 'a[bc]x', 'abcx',
                  '[!a]', 'a', '[', 'x]', 'a.b', 'a+b', 'a(b)', 'a|b', 'a\\b', 'a/b']
        for criterion, positions in (
            ('[ab]*', [0, 2]), ('*[ab]', [0]), ('a[bc]*', [4]), ('[!a]*', [6]),
            ('*[*', [0, 2, 4, 6, 8]), ('*]*', [0, 2, 4, 6, 9]),
            ('a.b*', [10]), ('a+b*', [11]), ('a(b)*', [12]), ('a|b*', [13]),
            ('a\\b*', [14]), ('a/b*', [15]),
        ):
            for op in ('', '=', '<>'):
                expected = ([i for i in range(len(values)) if i not in positions]
                            if op == '<>' else positions)
                with self.subTest(criterion=op + criterion):
                    predicate = utils.parse_criteria(op + criterion)
                    self.assertEqual([i for i, value in enumerate(values) if predicate(value)],
                                     expected)

    def test_text_equality_and_inequality_ignore_case(self):
        values = ['Alpha', 'alpha', 'ALPHA', 'beta', 'BETA', 'Beta ',
                  'áRvOrE', 'ÁRVORE', 1, None, False, error.NOT_AVAILABLE]
        for criterion, expected in (
            ('ALPHA', [0, 1, 2]), ('=aLpHa', [0, 1, 2]),
            ('<>ALPHA', list(range(3, len(values)))),
            ('ÁRVORE', [6, 7]), ('=beta', [3, 4]), ('beta ', [5]),
        ):
            with self.subTest(criterion=criterion):
                predicate = utils.parse_criteria(criterion)
                self.assertEqual([i for i, value in enumerate(values) if predicate(value)],
                                 expected)

    def test_text_ordering_ignores_case_and_excludes_nontext_values(self):
        values = ['Alpha', 'alpha', 'ALPHA', 'beta', 'BETA', 'gamma', 'GAMMA',
                  1, None, error.DIV_ZERO]
        for criterion, expected in (
            ('>BETA', [5, 6]), ('>=BeTa', [3, 4, 5, 6]),
            ('<BETA', [0, 1, 2]), ('<=bEtA', [0, 1, 2, 3, 4]),
        ):
            with self.subTest(criterion=criterion):
                predicate = utils.parse_criteria(criterion)
                self.assertEqual([i for i, value in enumerate(values) if predicate(value)],
                                 expected)

    def test_parse_criteria_matches_error_codes_without_matching_error_text(self):
        values = [error.NULL, error.DIV_ZERO, error.VALUE, error.REF,
                  error.NAME, error.NUM, error.NOT_AVAILABLE,
                  '#DIV/0!', '#N/A', 1, None]
        for criterion, positions in (
            ('#DIV/0!', [1]), ('=#N/A', [6]), (error.NOT_AVAILABLE, [6]),
            (error.XLError('#N/A'), [6]), ('<>#N/A', [0, 1, 2, 3, 4, 5, 7, 8, 9, 10]),
            ('<#REF!', [0, 1, 2]), ('<=#REF!', [0, 1, 2, 3]),
            ('>#REF!', [4, 5, 6]), ('>=#REF!', [3, 4, 5, 6]),
            ('>0', [9]), ('1', [9]), (1, [9]),
        ):
            with self.subTest(criterion=criterion):
                predicate = utils.parse_criteria(criterion)
                self.assertEqual([i for i, value in enumerate(values) if predicate(value)],
                                 positions)

    def test_wildcard_criteria_are_case_insensitive_and_keep_slashes_literal(self):
        values = ['folder/file', 'folder\\file', 'FOLDER/FILE', 'FOLDER\\FILE',
                  'Alpha', 'alpha', 'AB', 'ab', '', None, 1, False, error.NOT_AVAILABLE]
        for criterion, positions in (
            ('folder/*', [0, 2]), ('folder\\*', [1, 3]),
            ('a*', [4, 5, 6, 7]), ('=A?', [6, 7]),
            ('*', list(range(9))),
        ):
            for negative in (False, True):
                text = criterion.removeprefix('=')
                expression = '<>' + text if negative else criterion
                expected = ([i for i in range(len(values)) if i not in positions]
                            if negative else positions)
                with self.subTest(criterion=expression):
                    predicate = utils.parse_criteria(expression)
                    self.assertEqual([i for i, value in enumerate(values) if predicate(value)],
                                     expected)
