import weakref
import logging
import threading
import traceback
import collections

finlock = threading.RLock()
logger  = logging.getLogger(__name__)

from synapse.common import *

class EventBus:
    '''
    A synapse EventBus provides an easy way manage callbacks.
    '''
    def __init__(self):
        self.isfini = False
        self.finlock = finlock
        self.finievt = threading.Event()

        self._syn_funcs = collections.defaultdict(list)
        self._syn_weaks = collections.defaultdict(weakref.WeakSet)

        self._syn_links = []
        self._syn_weak_links = weakref.WeakSet()

        self._syn_queues = {}

        self._fini_funcs = []
        self._fini_weaks = weakref.WeakSet()

    def link(self, func, weak=False):
        '''
        Add a callback function to receive *all* events.

        Example:

            bus1 = EventBus()
            bus2 = EventBus()

            bus1.link( bus2.dist )

            # all events on bus1 are also propigated on bus2

        '''
        if not callable(func):
            raise Exception('link() func not callable: %r' % (func,))

        if weak:
            return self._syn_weak_links.add(func)

        self._syn_links.append(func)

    def unlink(self, func):
        '''
        Remove a callback function previously added with link()

        Example:

            bus.unlink( callback )

        '''
        self._syn_weak_links.discard(func)
        if func in self._syn_links:
            self._syn_links.remove(func)

    def on(self, name, func, weak=False):
        '''
        Add a callback func to the SynCallBacker.

        Example:

            def baz(event):
                x = event[1].get('x')
                y = event[1].get('y')
                return x + y

            d.on('woot',baz)

            d.fire('foo', x=10, y=20)

        Notes:

            * Use weak=True to hold a weak reference to the func.

        '''
        if not callable(func):
            raise Exception('on() func not callable: %r' % (func,))

        if weak:
            self._syn_weaks[name].add(func)
            return

        self._syn_funcs[name].append(func)

    def off(self, name, func):
        '''
        Remove a previously registered event handler function.

        Example:

            bus.off( 'foo', onFooFunc )

        '''
        funcs = self._syn_funcs.get(name)
        if funcs != None:

            if func in funcs:
                funcs.remove(func)

            if not funcs:
                self._syn_funcs.pop(name,None)

        weaks = self._syn_weaks.get(name)
        if weaks != None:

            if func in weaks:
                weaks.remove(func)

            if not weaks:
                self._syn_weaks.pop(name,None)

    def fire(self, evtname, **info):
        '''
        Fire the given event name on the EventBus.
        Returns a list of the return values of each callback.

        Example:

            for ret in d.fire('woot',foo='asdf'):
                print('got: %r' % (ret,))

        '''
        event = (evtname,info)
        self.dist(event)
        return event

    def dist(self, event):
        '''
        Distribute an existing event tuple.
        '''
        ret = []
        name = event[0]
        funcs = self._syn_funcs.get(name)
        if funcs != None:
            for func in funcs:
                try:
                    ret.append( func( event ) )
                except Exception as e:
                    logger.exception(e)

        weaks = self._syn_weaks.get(name)
        if weaks != None:
            for func in weaks:
                try:
                    ret.append( func( event ) )
                except Exception as e:
                    logger.exception(e)

        for func in self._syn_links:
            try:
                ret.append( func(event) )
            except Exception as e:
                logger.exception(e)

        for func in self._syn_weak_links:
            try:
                ret.append( func(event) )
            except Exception as e:
                logger.exception(e)

        return ret

    def fini(self):
        '''
        Fire the 'fini' handlers and set self.isfini.

        Example:

            d.fini()

        '''
        with finlock:

            if self.isfini:
                return

            self.isfini = True

        for func in self._fini_funcs:
            try:
                func()
            except Exception as e:
                traceback.print_exc()

        for func in self._fini_weaks:
            try:
                func()
            except Exception as e:
                traceback.print_exc()

        self.finievt.set()

    def onfini(self, func, weak=False):
        '''
        Register a handler to fire when this EventBus shuts down.
        '''
        if weak:
            return self._fini_weaks.add(func)
        self._fini_funcs.append(func)

    def waitfini(self, timeout=None):
        '''
        Wait for the event bus to fini()

        Example:

            bus.waitfini(timeout=30)

        '''
        return self.finievt.wait(timeout=timeout)

    def distall(self, events):
        '''
        Distribute multiple events on the event bus.
        '''
        [self.dist(evt) for evt in events]
    
    @firethread
    def consume(self, gtor):
        '''
        Feed the event bus from a generator.

        Example:

            bus.consume( getAllEvents() )

        '''
        for e in gtor:
            if e == None:
                break

            self.dist(e)
