# hotxlfp

[![Build Status](https://travis-ci.org/aidhound/hotxlfp.svg?branch=master)](https://travis-ci.org/aidhound/hotxlfp) [![codecov](https://codecov.io/gh/aidhound/hotxlfp/branch/master/graph/badge.svg)](https://codecov.io/gh/aidhound/hotxlfp)

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

## Variables

You can also set variables that you can then use in your formulas

    p.set_variable('foo', 33)
    p.parse('foo/3') # returns {'result': 11.0, 'error': None}

# Contributing

Fork the project

## Installing Dependencies  
  
Depends on ply and python-dateutil.  
   
To install dependencies automatically using pip run:

    pip install -r requirements.txt
  
## Testing   

    python setup.py test

## Coverage

    coverage run --source hotxlfp setup.py test

## Update SUPPORTED_FORMULAS.md

Inside the project directory run:

    python -m "scripts.update_supported_formulas"
