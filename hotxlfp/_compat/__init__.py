# -*- coding: utf-8 -*-
import sys

PY2 = sys.version_info[0] == 2

if PY2:
    from .py3 import statistics
    number_types = (int, long, float, complex)
    integer_types = (int, long)
    string_types = (str, unicode)
else:
    import statistics
    number_types = (int, float, complex)
    integer_types = (int,)
    string_types = (str,)
