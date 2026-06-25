# -*- coding: utf-8 -*-
import ply.yacc as yacc
import ply.lex as lex
from . import lexer
from ..helper.number import to_number
from .._compat import number_types, string_types
from ..formulas import error, operators
import math


class Parser(object):
    """
    Base class for a lexer/parser that has the rules defined as methods
    """
    tokens = lexer.tokens
    precedence = (
        ('left', 'EQUAL'),
        ('left', 'LESSEQ', 'GREATEREQ', 'NOTEQUAL'),
        ('left', 'GREATER', 'LESS'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'MULT', 'DIV'),
        ('left', 'CARET'),
        ('left', 'AMP'),
        ('left', 'PERCENT'),
        ('left', 'UMINUS')
    )

    def __init__(self, debug=False, call_function=None, call_variable=None, call_cell_value=None, call_range_value=None, throw_error=None):
        self.debug = debug
        self.call_function = call_function
        self.call_variable = call_variable
        self.call_cell_value = call_cell_value
        self.call_range_value = call_range_value
        self.throw_error = throw_error
        self.names = {}
        self.input = None
        self.last_error = None
        try:
            modname = os.path.split(os.path.splitext(__file__)[0])[
                1] + "_" + self.__class__.__name__
        except:
            modname = "parser" + "_" + self.__class__.__name__
        self.debugfile = modname + ".dbg"
        self.tabmodule = modname + "_" + "parsetab"

        # Build the lexer and parser
        self.lex = lex.lex(module=lexer, debug=self.debug)
        self.yacc = yacc.yacc(module=self,
                  debug=self.debug,
                  debugfile=self.debugfile,
                  tabmodule=self.tabmodule)

    def parse(self, input):
        self.input = input
        self.last_error = None
        self.lex.error_pos = None
        self.lex.error_value = None
        return self.yacc.parse(input, lexer=self.lex)

    def run(self):
        while 1:
            try:
                s = raw_input('=')
            except EOFError:
                break
            if not s:
                continue
        print(self.parse(s))


class FormulaParser(Parser):

    def p_expressions(self, p):
        'expressions : expression'
        p[0] = p[1]

    def p_expression_arithmetic_operator(self, p):
        """
        expression : expression PLUS expression
                  | expression MINUS expression
                  | expression MULT expression
                  | expression DIV expression
                  | expression AMP expression
        """
        p[0] = ['binop', p[2], p[1], p[3]]

    def p_expression_logical_operator(self, p):
        """
        expression : expression GREATER expression
                   | expression LESS expression
                   | expression GREATEREQ expression
                   | expression LESSEQ expression
                   | expression EQUAL expression
                   | expression NOTEQUAL expression
        """
        p[0] = ['binop', p[2], p[1], p[3]]

    def p_expression_uminus(self, p):
        'expression : MINUS expression %prec UMINUS'
        p[0] = ['unary', '-', p[2]]

    def p_expression_number(self, p):
        """
        expression : NUMBER
                   | DECIMAL NUMBER
                   | NUMBER DECIMAL NUMBER
                   | NUMBER CARET NUMBER
                   | NUMBER PERCENT
        """
        if len(p) == 2:
            p[0] = ['num', to_number(p[1])]
        elif p[1] == '.':
            p[0] = ['num', to_number('0.' + p[2])]
        elif p[2] == '.':
            p[0] = ['num', to_number(p[1] + '.' + p[3])]
        elif p[2] == '^':
            p[0] = ['binop', '^', ['num', to_number(p[1])], ['num', to_number(p[3])]]
        elif p[2] == '%':
            p[0] = ['unary', '%', ['num', to_number(p[1])]]

    def p_expression_string(self, p):
        """
        expression : STRING
        """
        p[0] = ['str', p[1][1:-1]]

    def p_expression_function(self, p):
        """
        expression : FUNCTION LPAREN RPAREN
        """
        p[0] = ['call', p[1], []]

    def p_expression_wargs(self, p):
        """
        expression : FUNCTION LPAREN expseqcomma RPAREN
                   | FUNCTION LPAREN expseqsemicolon RPAREN
                   | FUNCTION LPAREN expseqbackslash RPAREN
        """
        p[0] = ['call', p[1], p[3]]

    def p_expression_array(self, p):
        """
        expression : array
        """
        p[0] = p[1]

    def p_array(self, p):
        """
        array : LBRACKET expseqsemicolon RBRACKET
              | LBRACKET expseqcomma RBRACKET
              | LBRACKET expseqbackslash RBRACKET
        """
        p[0] = ['array', p[2]]

    def p_expseq_semicolon(self, p):
        """
        expseqsemicolon : expression
                        | SEMICOLON SEMICOLON
                        | SEMICOLON expseqsemicolon
                        | expseqsemicolon SEMICOLON
                        | expseqsemicolon SEMICOLON expression
                        | expseqsemicolon SEMICOLON SEMICOLON expression
                        | expseqcomma SEMICOLON expseqcomma
                        | expseqbackslash SEMICOLON expseqbackslash
        """
        if len(p) == 2:
            p[0] = [p[1]]
        elif len(p) == 3:
            if p[1] == ';' and p[2] == ';':
                p[0] = [['empty'], ['empty'], ['empty']]
            elif p[1] == ';':
                p[0] = [['empty']] + p[2]
            else:
                p[0] = p[1] + [['empty']]
        elif p[2] == ';':
            if p[3] == ';':
                p[0] = p[1] + [['empty'], p[4]]
            else:
                if str(p.slice[1]) in ('expseqcomma', 'expseqbackslash'):
                    p[0] = [p[1]] + [p[3]]
                else:
                    p[0] = p[1] + [p[3]]

    def p_expseq_comma(self, p):
        """
        expseqcomma : expression
                    | COMMA COMMA
                    | COMMA expseqcomma
                    | expseqcomma COMMA
                    | expseqcomma COMMA expression
                    | expseqcomma COMMA COMMA expression
        """
        if len(p) == 2:  # expression
            p[0] = [p[1]]
        elif len(p) == 3:
            if p[1] == ',' and p[2] == ',':
                p[0] = [['empty'], ['empty'], ['empty']]
            elif p[1] == ',':
                p[0] = [['empty']] + p[2]
            else:
                p[0] = p[1] + [['empty']]
        elif p[2] == ',':
            # expseqcomma COMMA COMMA expression
            if p[3] == ',':  # e.g. an empty function argument
                p[0] = p[1] + [['empty'], p[4]]
            else:
                p[0] = p[1] + [p[3]]

    def p_expseq_backslash(self, p):
        """
        expseqbackslash : expression
                        | BACKSLASH BACKSLASH
                        | BACKSLASH expseqbackslash
                        | expseqbackslash BACKSLASH
                        | expseqbackslash BACKSLASH expression
                        | expseqbackslash BACKSLASH BACKSLASH expression
        """
        if len(p) == 2:
            p[0] = [p[1]]
        elif len(p) == 3:
            if p[1] == '\\' and p[2] == '\\':
                p[0] = [['empty'], ['empty'], ['empty']]
            elif p[1] == '\\':
                p[0] = [['empty']] + p[2]
            else:
                p[0] = p[1] + [['empty']]
        elif p[2] == '\\':
            if p[3] == '\\':
                p[0] = p[1] + [['empty'], p[4]]
            else:
                p[0] = p[1] + [p[3]]

    def p_xlerror(self, p):
        """
        expression : XLERROR
        """
        p[0] = ['err', p[1]]

    def p_error(self, p):
        """
        SyntaxError
        """
        if p is None:
            position = len(self.input) if self.input is not None else None
            self.last_error = {
                'position': position,
                'length': 0,
                'token': None,
                'type': None,
                'message': 'Unexpected end of input'
            }
        else:
            self.last_error = {
                'position': p.lexpos,
                'length': len(str(p.value)),
                'token': str(p.value),
                'type': p.type,
                'message': "Unexpected token '%s'" % (p.value,)
            }
        raise error.ERROR

    def p_expression_paren(self, p):
        """
        expression : LPAREN expression RPAREN
        """
        p[0] = p[2]

    def p_expression_varseq(self, p):
        """
        expression : variable_sequence
        """
        p[0] = ['var', p[1][0]]

    def p_variable(self, p):
        """
        variable_sequence : VARIABLE
        """
        p[0] = [p[1]]

    def p_variable_seq(self, p):
        """
        variable_sequence : variable_sequence DECIMAL VARIABLE
        """
        p[0] = p[1] if isinstance(p[1], list) else [p[1]]
        p[0].append(p[3])

    def p_expression_cell(self, p):
        """
        expression :  cell
        """
        p[0] = p[1]

    def p_cell(self, p):
        """
        cell : ABSOLUTE_CELL
             | RELATIVE_CELL
             | MIXED_CELL
             | ABSOLUTE_CELL COLON ABSOLUTE_CELL
             | ABSOLUTE_CELL COLON RELATIVE_CELL
             | ABSOLUTE_CELL COLON MIXED_CELL
             | RELATIVE_CELL COLON ABSOLUTE_CELL
             | RELATIVE_CELL COLON RELATIVE_CELL
             | RELATIVE_CELL COLON MIXED_CELL
             | MIXED_CELL COLON ABSOLUTE_CELL
             | MIXED_CELL COLON RELATIVE_CELL
             | MIXED_CELL COLON MIXED_CELL
        """
        if len(p) == 2:
            p[0] = ['cell', p[1]]
        else:
            p[0] = ['range', p[1], p[3]]
