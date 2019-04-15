# -*- coding: utf-8 -*-
import unittest
from hotxlfp.tinyemitter import Emitter


class TestEmitter(unittest.TestCase):

    def test_subscribes(self):
        """ Subscribes to an event """
        emitter = Emitter()
        emitter.on('test', lambda: None)
        self.assertEqual(len(emitter._e['test']), 1)

    def test_subscribes_with_context(self):
        """ Subscribes to an event and context is passed """
        emitter = Emitter()
        context = {'context_value': True}

        def ctxfunc(context_value=None):
            self.assertTrue(context_value)

        emitter.on('test', ctxfunc, context)
        emitter.emit('test')

    def test_only_once(self):
        """ Subscribes to an event only once"""
        emitter = Emitter()

        def callmeonce():
            self.assertNotIn('test', emitter._e)

        emitter.once('test', callmeonce)
        emitter.emit('test')

    def test_only_once_context(self):
        """ Subscribing to an event only once keeps context """
        emitter = Emitter()
        context = {'context_value': True}

        def callmeonce(context_value=None):
            self.assertTrue(context_value)
            self.assertNotIn('test', emitter._e)

        emitter.once('test', callmeonce, context)
        emitter.emit('test')

    def test_emit(self):
        """ Emits an event """
        emitter = Emitter()
        function_called = {'value': False}

        def wasicalled():
            function_called['value'] = True

        emitter.on('test', wasicalled)
        emitter.emit('test')
        self.assertTrue(function_called['value'])

    def test_args(self):
        """ Passes all arguments to event listener """
        emitter = Emitter()
        function_called = {'value': False}

        def twoargs(arg1, arg2):
            self.assertEqual(arg1, 'arg1')
            self.assertEqual(arg2, 'arg2')

        emitter.on('test', twoargs)
        emitter.emit('test', 'arg1', 'arg2')

    def test_unsubscribe(self):
        """ Unsubscribes all listeners for events with name """
        emitter = Emitter()

        def dontcallme(arg1, arg2):
            self.fail('Called an unsubscribed function')

        emitter.on('test', dontcallme)
        emitter.off('test')
        emitter.emit('test')

    def test_unsubscribe_single(self):
        """ Unsubscribes one listener for events with name """
        emitter = Emitter()
        function_called = {'value': False}

        def dontcallme(arg1, arg2):
            self.fail('Called an unsubscribed function')

        def wasicalled():
            function_called['value'] = True

        emitter.on('test', dontcallme)
        emitter.on('test', wasicalled)
        emitter.off('test', dontcallme)
        emitter.emit('test')
        self.assertTrue(function_called['value'])

    def test_remove_inside_event(self):
        """ Removes an event inside another event """
        emitter = Emitter()

        def callme():
            self.assertEqual(len(emitter._e['test']), 1, 'event is still in the list')
            emitter.off('test')
            self.assertNotIn('test', emitter._e)

        emitter.on('test', callme)
        emitter.emit('test')
