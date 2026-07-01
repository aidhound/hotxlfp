# -*- coding: utf-8 -*-
from .tinyemitter import Emitter
from . import formulas
from .formulas import error as formulaserror
from .formulas import operators
from .grammarparser.parser import FormulaParser
from .helper.cell import extract_label, to_label, Cell
import inspect
import traceback


class Parser(Emitter):

    def __init__(self, debug=False):
        super(Parser, self).__init__()
        self.variables = {'TRUE': True, 'FALSE': False, 'NULL': None}
        self.functions = {}
        self.debug = debug
        self.parser = FormulaParser(call_function=self.call_function,
                                    call_variable=self.call_variable,
                                    call_cell_value=self.call_cell_value,
                                    call_range_value=self.call_range_value,
                                    throw_error=self._throw_error
                                    )

    def parse(self, expression):
        if expression == '':
            return {'result': '', 'error': None}
        ast_result = self.parse_to_ast(expression)
        if ast_result['error'] is not None:
            return {'result': None, 'error': ast_result['error']}
        return self.evaluate_ast(ast_result['ast'])

    def parse_to_ast(self, expression):
        """ Parse ``expression`` into a JSON-serializable AST without evaluating it.

        Returns ``{'ast': <Node|None>, 'error': <str|None>}``. On a syntax or
        lexing error ``ast`` is ``None`` and ``error`` holds the Excel error
        string (the same string ``parse`` would return for that input).
        """
        if expression == '':
            # Mirrors parse()'s empty-input shortcut so evaluate_ast(ast) == parse('').
            return {'ast': ['str', ''], 'error': None}
        ast = None
        error = None
        try:
            ast = self.parser.parse(expression)
        except Exception as e:
            if self.debug:
                traceback.print_exc()
            error = str(formulaserror.from_message(e))
        return {'ast': ast, 'error': error}

    def evaluate_ast(self, ast):
        """ Evaluate an AST produced by :meth:`parse_to_ast`.

        Uses the same registered functions/variables, cell callbacks and
        operator implementations as :meth:`parse`, so the returned
        ``{'result': ..., 'error': ...}`` matches ``parse`` exactly.
        """
        result = None
        error = None
        try:
            if ast is not None:
                result = self._eval_node(ast)
        except Exception as e:
            if self.debug:
                traceback.print_exc()
            error = str(formulaserror.from_message(e))
        if isinstance(result, formulaserror.XLError):
            error = str(result)
            result = None
        return {'result': result, 'error': error}

    def _eval_node(self, node):
        tag = node[0]
        if tag == 'num':
            return node[1]
        if tag == 'str':
            return node[1]
        if tag == 'empty':
            return None
        if tag == 'err':
            raise formulaserror.from_message(node[1])
        if tag == 'var':
            return self.call_variable(node[1])
        if tag == 'cell':
            return self.call_cell_value(node[1])
        if tag == 'range':
            return self.call_range_value(node[1], node[2])
        if tag == 'array':
            return self._eval_seq(node[1])
        if tag == 'call':
            return self.call_function(node[1], self._eval_seq(node[2]))
        if tag == 'binop':
            op = node[1]
            left = self._eval_node(node[2])
            right = self._eval_node(node[3])
            if op == '&':
                return str(left) + str(right)
            if op == '^':
                return left ** right
            if op in ('+', '-', '*', '/'):
                return operators.evaluate_arithmetic(op, left, right)
            return operators.evaluate_logic(op, left, right)
        if tag == 'unary':
            op = node[1]
            operand = self._eval_node(node[2])
            if op == '-':
                return -operand
            if op == '%':
                return operand * 0.01
        raise formulaserror.ERROR

    def _eval_seq(self, seq):
        """ Evaluate a sequence (function arguments or array contents).

        Items are AST nodes (tagged lists whose first element is a string) or,
        for bidimensional arrays, nested lists of nodes. Every node tag is a
        non-empty string (see the tags handled by _eval_node), while a nested
        row is a plain list whose first element is itself a list (a node) --
        that difference is what isinstance(item[0], str) distinguishes.
        """
        result = []
        for item in seq:
            if isinstance(item, list) and item and isinstance(item[0], str):
                result.append(self._eval_node(item))
            else:
                result.append(self._eval_seq(item))
        return result

    def validate(self, expression):
        """ Structurally validate ``expression`` without evaluating it.

        Returns a list of error dicts (empty list means valid). Each error has
        the keys ``kind`` ('syntax', 'unknown_function' or 'arity'),
        ``position``, ``length``, ``token``, ``function`` and ``message``.
        Never raises and never evaluates the formula.
        """
        if expression == '':
            # parse('') succeeds (empty result), so it is a valid formula.
            return []
        errors = []
        try:
            ast = self.parser.parse(expression)
        except Exception:
            last_error = getattr(self.parser, 'last_error', None)
            if last_error is not None:
                errors.append({
                    'kind': 'syntax',
                    'position': last_error.get('position'),
                    'length': last_error.get('length'),
                    'token': last_error.get('token'),
                    'function': None,
                    'message': last_error.get('message', 'Syntax error')
                })
            else:
                pos = getattr(self.parser.lex, 'error_pos', None)
                token = getattr(self.parser.lex, 'error_value', None)
                errors.append({
                    'kind': 'syntax',
                    'position': pos,
                    'length': 1 if pos is not None else None,
                    'token': token,
                    'function': None,
                    'message': "Invalid character '%s'" % token if token else 'Syntax error'
                })
            return errors
        try:
            self._validate_node(ast, errors)
        except Exception:
            pass
        return errors

    def _validate_node(self, node, errors):
        if not isinstance(node, list) or not node:
            return
        tag = node[0]
        if not isinstance(tag, str):
            # node is actually a plain sequence (e.g. an array row), not a
            # tagged AST node -- see _eval_seq for the same distinction.
            for item in node:
                self._validate_node(item, errors)
            return
        if tag == 'call':
            name = node[1]
            args = node[2]
            fn = self.functions.get(name)
            if fn is None and not formulas.is_supported(name):
                errors.append({
                    'kind': 'unknown_function',
                    'position': None,
                    'length': None,
                    'token': name,
                    'function': name,
                    'message': "Unknown function '%s'" % name
                })
            else:
                if fn is None:
                    fn = formulas.get_for(name)
                nargs = len(args)
                if self._arity_error(fn, nargs):
                    errors.append({
                        'kind': 'arity',
                        'position': None,
                        'length': None,
                        'token': name,
                        'function': name,
                        'message': "Function '%s' called with %d argument(s)" % (name, nargs)
                    })
            for item in args:
                self._validate_node(item, errors)
            return
        for item in node[1:]:
            self._validate_node(item, errors)

    @staticmethod
    def _arity_error(fn, nargs):
        """ Best-effort arity check: True when calling ``fn`` with ``nargs``
        positional arguments would raise a ``TypeError`` for arg count. """
        try:
            sig = inspect.signature(fn)
        except (ValueError, TypeError):
            return False
        try:
            sig.bind(*([None] * nargs))
            return False
        except TypeError:
            return True

    def set_function(self, name, f):
        self.functions[name] = f
        return self

    def get_function(self, name):
        return self.functions[name]

    def call_function(self, name, args=None):
        if args is None:
            args = []

        fn = self.functions.get(name)
        result = {'value': None}  # get around 2.7 not having nonlocal
        if fn is None:
            fn = formulas.get_for(name)
        if fn is None:
            raise formulaserror.NAME
        result['value'] = fn(*args)

        def valsetter(new_value):
            if new_value is not None:
                result['value'] = new_value

        self.emit('callFunction', name, args, valsetter)
        return result['value']

    def set_variable(self, name, v):
        self.variables[name] = v
        return self

    def get_variable(self, name):
        return self.variables[name]

    def call_variable(self, name):
        not_found = lambda : 0
        value = self.variables.get(name, not_found)
        result = {'value': value}  # get around 2.7 not having nonlocal

        def valsetter(new_value):
            if new_value is not None:
                result['value'] = new_value
        self.emit('callVariable', name, valsetter)
        if result['value'] is not_found:
            raise formulaserror.NAME
        return result['value']

    def call_cell_value(self, label):
        label = label.upper()
        row, col = extract_label(label)
        result = {'value': None}  # get around 2.7 not having nonlocal

        def valsetter(new_value):
            if new_value is not None:
                result['value'] = new_value

        self.emit('callCellValue', Cell(label, row, col), valsetter)
        return result['value']

    def call_range_value(self, start_label, end_label):
        if start_label is None or end_label is None:
            return []
        start_label = start_label.upper()
        end_label = end_label.upper()

        start_row, start_col = extract_label(start_label)
        end_row, end_col = extract_label(end_label)
        start_cell = Cell(start_label)
        end_cell = Cell(end_label)

        if start_row.index <= end_row.index:
            start_cell.row = start_row
            end_cell.row = end_row
        else:
            end_cell.row = start_row
            start_cell.row = end_row

        if start_col.index <= end_col.index:
            start_cell.col = start_col
            end_cell.col = end_col
        else:
            end_cell.col = start_col
            start_cell.col = end_col

        result = {'value': None}  # get around 2.7 not having nonlocal

        def valsetter(new_value):
            if new_value is not None:
                result['value'] = new_value

        self.emit('callRangeValue', start_cell, end_cell, valsetter)
        return result['value']

    def _throw_error(self, error_name):
        raise formulaserror.from_message(error_name)
