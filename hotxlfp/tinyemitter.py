# -*- coding: utf-8 -*-
"""
A python version of tiny-emitter
https://github.com/scottcorgan/tiny-emitter
"""
from collections import defaultdict, namedtuple


Listener = namedtuple('Listener', ['fn', 'ctx'])


class Emitter(object):

    def __init__(self):
        self._e = defaultdict(list)

    def on(self, name, callback, ctx=None):
        if ctx is None:
            ctx = {}
        self._e[name].append(Listener(fn=callback, ctx=ctx))
        return self

    def once(self, name, callback, ctx=None):
        if ctx is None:
            ctx = {}
        def onetime_listener(*args, **ctx):
            self.off(name, onetime_listener)
            callback(*args, **ctx)
        onetime_listener._ = callback
        return self.on(name, onetime_listener, ctx)

    def emit(self, name, *args):
        listeners = self._e[name][:]
        for listener in listeners:
            listener.fn(*args, **listener.ctx)
        return self

    def off(self, name, callback=None):
        events = self._e[name]
        live_events = []
        if events and callback:
            for event in events:
                if event.fn != callback and ((not hasattr(event.fn, '_')) or event.fn._ != callback):
                    live_events.append(event)

        if live_events:
            self._e[name] = live_events
        else:
            del self._e[name]
        return self
