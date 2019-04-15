# hotxlfp

[![Build Status][travis-image]][travis-url] [![codecov.io](https://codecov.io/github/aidhound/hotxlfp?/coverage.svg?branch=master)](https://codecov.io/github/aidhound/hotxlfp?branch=master)

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
