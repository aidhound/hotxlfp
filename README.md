# hotxlfp

[![Test](https://github.com/aidhound/hotxlfp/actions/workflows/test.yml/badge.svg)](https://github.com/aidhound/hotxlfp/actions/workflows/test.yml) [![codecov](https://codecov.io/gh/aidhound/hotxlfp/branch/master/graph/badge.svg)](https://codecov.io/gh/aidhound/hotxlfp)

hotxlfp intends to be a python version of the javascript [handsontable excel formula parser](https://github.com/handsontable/formula-parser) differences are acceptable to make it more pythonic or the function implementations more correct.

# Install

You can install using pip

    pip install hotxlfp

# Usage

## Create a Parser

    import hotxlfp
    p = hotxlfp.Parser()

## Parse excel formulas 

    p.parse('SUM(1,2,3)') # returns {'result': 6, 'error': None}

It's also fine to use semi-colons as separators (they're used by excel depending on your locale)

    p.parse('SUM(1;2;3)') # returns {'result': 6, 'error': None}

## Custom functions

Say you have a function called triple:

    def triple(x):
        return x*3

You can teach the parser to use it with set_function

    p.set_function('TRIPLE', triple)
    p.parse('TRIPLE(2)') # returns {'result': 6, 'error': None}

Function names are case-insensitive: `TRIPLE(2)`, `triple(2)` and `Triple(2)` call
the same function. `set_function` and `get_function` also ignore case.

A custom function with the same name as a built-in overrides it for that parser
instance. For example, registering `average` makes both `average(...)` and
`AVERAGE(...)` call your custom function. Registering the name again replaces the
previous custom function, even if you use different capitalization.

String arguments and variable names keep their original case. The `callFunction`
event receives the function name exactly as written in the expression. An unknown
function returns a `#NAME?` formula error.

## Variables

You can also set variables that you can then use in your formulas

    p.set_variable('foo', 33)
    p.parse('foo/3') # returns {'result': 11.0, 'error': None}

# Differences from Excel

## Blank values

hotxlfp treats both `None` and the empty string (`""`) as blank. This preserves
compatibility with applications that use empty strings for unanswered inputs.
Zero, `False`, whitespace-only strings and arrays are not scalar blanks. Strings
are not trimmed before checking whether they are blank.

The following compares an empty-string value in hotxlfp with an Excel reference
to a cell whose formula returns empty text (`=""`):

| Function | hotxlfp | Excel |
| --- | --- | --- |
| ISBLANK | `True` | `FALSE` |
| COUNTA | Not counted | Counted |
| COUNTBLANK | Counted | Counted |

These blank-handling rules are intentional compatibility choices. Excel's
[ISBLANK](https://support.microsoft.com/en-us/excel/functions/is-functions)
and [COUNTA](https://support.microsoft.com/en-us/excel/functions/counta-function)
distinguish empty cells from empty text. Its
[COUNTBLANK](https://support.microsoft.com/en-us/excel/functions/countblank-function)
also counts cells whose formulas return empty text.

## Array-literal orientation

The parser currently represents both `{1,2,3}` and `{1;2;3}` as the same flat
list, `[1, 2, 3]`. Excel distinguishes a horizontal row from a vertical column.
This is a known parser limitation. Callbacks can provide nested arrays such as
`[[1, 2, 3]]` for one row or `[[1], [2], [3]]` for one column when orientation
matters.

# Contributing

Fork the project

## Installing Dependencies  
  
Depends on ply and python-dateutil.  

This project uses [uv](https://docs.astral.sh/uv/) to manage dependencies and the virtual environment. To install dependencies automatically run:

    uv sync

## Updating Dependencies

To upgrade ply/python-dateutil to their latest compatible versions and update `uv.lock` accordingly:

    uv lock --upgrade

Commit the updated `uv.lock` along with your change.

## Testing   

    uv run python -m unittest discover

## Coverage

    uv run coverage run --source hotxlfp -m unittest discover

## Update SUPPORTED_FORMULAS.md

Inside the project directory run:

    uv run python -m "scripts.update_supported_formulas"
