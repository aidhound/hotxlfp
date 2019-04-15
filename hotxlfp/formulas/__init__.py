# -*- coding: utf-8 -*-


class Dispatcher(object):

    def __init__(self):
        self._registry_ = {}

    def register_for(self, *fnames):
        def wrap(dispatch_fn):
            for fname in fnames:
                self._registry_[fname] = dispatch_fn
            return dispatch_fn
        return wrap

    def get_for(self, fname):
        try:
            return self._registry_[fname]
        except KeyError:
            raise SyntaxError('Function not found for %s' % fname)

    def __iter__(self):
        return iter(registry.values())


dispatcher = Dispatcher()


def get_for(fname):
    return dispatcher.get_for(fname)


def supported():
    """ Get a list of supported formulas """
    return sorted(dispatcher._registry_.keys())


def is_supported(fname):
    return fname in dispatcher._registry_


from . import error
from . import information
from . import logic
from . import statistical
from . import mathtrig
from . import text
from . import dateandtime
from . import engineering
from . import financial
from . import lookupandreference

