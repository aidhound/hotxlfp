
setup-python:
  python3 -m venv env

install-python-deps:
  pip install pytest
  pip install -r requirements.txt

test:
  python -m pytest tests/test_formula_parser.py
