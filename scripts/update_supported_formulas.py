# -*- coding: utf-8 -*-
"""
Run from root directory
python -m "scripts.update_supported_formulas"
"""
from hotxlfp import formulas
import os
from io import open
path = os.path.dirname(__file__)
allpath = os.path.join(path, 'allformulas.txt')
fpath = os.path.join(path, os.pardir, 'SUPPORTED_FORMULAS.md')


functions_to_support = []
with open(allpath, 'r', encoding='utf-8', newline='\n') as f:
    functions_to_support = (l.strip() for l in f.readlines())

with open(fpath, 'w', encoding='utf-8', newline='\n') as f:
    supported = formulas.supported()
    f.write(u'# Supported Formulas - %d\n\n' % len(supported))
    for formula in supported:
        f.write(u'* ' + formula + u'\n')
    supported = set(supported)
    unsupported = [fn for fn in functions_to_support if fn not in supported]
    f.write(u'\n\n# Not Yet Supported Formulas - %d\n\n' % len(unsupported))
    for formula in unsupported:
        f.write(u'* ' + formula + u'\n')


