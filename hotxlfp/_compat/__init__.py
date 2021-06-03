# -*- coding: utf-8 -*-
import sys
import numpy as np
import torch

PY2 = sys.version_info[0] == 2

if PY2:
    from .py3 import statistics
    number_types = (int, long, float, complex)
    integer_types = (int, long)
    string_types = (str, unicode)
else:
    import statistics
    number_types = (int, float, complex, np.ndarray, torch.Tensor)
    integer_types = (int,)
    string_types = (str,)
