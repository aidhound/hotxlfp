# hotxlfp

[![Build Status](https://travis-ci.org/aidhound/hotxlfp.svg?branch=master)](https://travis-ci.org/aidhound/hotxlfp) [![codecov](https://codecov.io/gh/aidhound/hotxlfp/branch/master/graph/badge.svg)](https://codecov.io/gh/aidhound/hotxlfp)

hotxlfp intends to be a python version of the javascript [handsontable excel formula parser](https://github.com/handsontable/formula-parser) differences are acceptable to make it more pythonic or the function implementations more correct.

# Contributing

Fork the project

## Installing Deppendencies  
  
Depends on ply and python-dateutil.  
   
To install dependencies automatically using pip run:

    pip install -r requirements.txt
  
## Testing   

    python setup.py test

## Coverage

    coverage run --source hotxlfp setup.py test
