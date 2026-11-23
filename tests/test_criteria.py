# -*- coding: utf-8 -*-
import unittest
from hotxlfp.formulas import error, utils


class TestCriteria(unittest.TestCase):

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
