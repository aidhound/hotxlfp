# -*- coding: utf-8 -*-
from .tinyemitter import Emitter
from . import formulas
from .formulas import error as formulaserror
from .grammarparser.parser import FormulaParser
from .helper.cell import extract_label, to_label, Cell
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
        result = None
        error = None
        try:
            if expression == '':
                result = ''
            else:
                result = self.parser.parse(expression)
        except Exception as e:
            if self.debug:
                traceback.print_exc()
            error = str(formulaserror.from_message(e))

        if isinstance(result, formulaserror.XLError):
            error = str(result)
            result = None
        return {'result': result, 'error': error}

    def set_function(self, name, f):
        self.functions[name.upper()] = f
        return self

    def get_function(self, name):
        return self.functions[name.upper()]

    def call_function(self, name, args=None):
        if args is None:
            args = []

        fn = self.functions.get(name.upper())
        result = None
        try:
            if fn is None:
                fn = formulas.get_for(name.upper())
            result = fn(*args)
        except formulaserror.XLError as exc:
            # Let enclosing formula functions handle semantic Excel errors.
            result = exc

        def valsetter(new_value):
            nonlocal result
            if new_value is not None:
                result = new_value

        self.emit('callFunction', name, args, valsetter)
        return result

    def set_variable(self, name, v):
        self.variables[name] = v
        return self

    def get_variable(self, name):
        return self.variables[name]

    def call_variable(self, name):
        not_found = lambda : 0
        result = self.variables.get(name, not_found)

        def valsetter(new_value):
            nonlocal result
            if new_value is not None:
                result = new_value

        self.emit('callVariable', name, valsetter)
        if result is not_found:
            return formulaserror.NAME
        return result

    def call_cell_value(self, label):
        label = label.upper()
        row, col = extract_label(label)
        result = None

        def valsetter(new_value):
            nonlocal result
            if new_value is not None:
                result = new_value

        self.emit('callCellValue', Cell(label, row, col), valsetter)
        return result

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

        result = None

        def valsetter(new_value):
            nonlocal result
            if new_value is not None:
                result = new_value

        self.emit('callRangeValue', start_cell, end_cell, valsetter)
        return result

    def _throw_error(self, error_name):
        raise formulaserror.from_message(error_name)
