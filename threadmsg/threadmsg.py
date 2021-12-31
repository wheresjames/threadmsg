#!/usr/bin/env python3

from __future__ import print_function
import threading
import asyncio
import traceback
import inspect

Log = print


#==================================================================================================
''' class ThreadMsg

    Provides a thread safe message queue.

'''
class ThreadMsg():

    ''' Constructor
        @param [in] f       - Pointer to the function to run
                                The function will receive a pointer to this
                                class as the first parameter.
                                The function can return an integer representing
                                the amount of time in seconds to delay before
                                calling the function again.  If a number less than
                                zero is returned, the thread will exit.
        @param [in] p       - Tuple containing other parameters to pass to the function
        @param [in] start   - True if the thread should start right away.
        @param [in] deffk   - Default function key for function mapping
    '''
    def __init__(self, f, p=(), start=True, deffk=None):

        self.msgs = []
        self.msgcnt = 0
        self.msgwait = 0
        self.run = True
        self.loops = 0
        self.lock = threading.Lock()
        self.cond = threading.Condition(self.lock)
        self.defFunKey = deffk

        # Thread
        self.thread = threading.Thread(target=self.threadLoop, args=(f, p,))
        if start:
            self.thread.start()


    ''' Destructor
    '''
    def __del__(self):
        self.join()


    ''' Sets a default function key to use with function mapping
    '''
    def setDefaultFunctionKey(fk):
        self.defFunKey = fk

    ''' Maps a call to set functions

            You can use this message to map messages to a function.

        @param [in] f       - Function or key in the function map
        @param [in] fm      - Map of functions to call
        @param [in] params  - dict containing function parameters to pass to function
        @param [in] kwargs  - keyword arguments to pass to function

        @begincode

            fm = {
                    'open'  : self.open,
                    'close' : self.close
                }

            @staticmethod
            async def mainThread(ctx):
                while msg := ctx.getMsg()
                    ctx.mapCall('_funName', fm, msg['data'])

        @endcode

    '''
    def mapCall(self, _f, _fm, _params={}, **kwargs):

        # Merge arguments
        _params.update(kwargs)

        # Look up function name if not callable
        if not callable(_f):
            if not isinstance(_f, str) or not _f:
                _f = self.defFunKey
            if not isinstance(_f, str) or not _f or _f not in _params:
                raise Exception('Function not found : %s' % _f)
            _f = _params[_f]
            if not isinstance(_f, str) or not _f or _f not in _fm:
                raise Exception('Function map not found : %s' % _f)
            _f = _fm[_f]

        # Map the parameters
        p = []
        sig = inspect.signature(_f).parameters
        for v in sig:
            if v not in _params:
                raise Exception('Function parameter not found : %s' % v)
            p.append(_params[v])

        # Make the call
        return _f(*p)


    ''' Asynchronously maps a call to set functions

            You can use this message to map messages to a function.

        @param [in] f       - Function or key in the function map
        @param [in] fm      - Map of functions to call
        @param [in] params  - dict containing function parameters to pass to function
        @param [in] kwargs  - keyword arguments to pass to function

        @begincode

            fm = {
                    'open'  : self.open,
                    'close' : self.close
                }

            @staticmethod
            async def mainThread(ctx):
                while msg := ctx.getMsg()
                    await ctx.mapCall('_funName', fm, msg['data'])

        @endcode

    '''
    async def mapCallAsync(self, _f, _fm, _params={}, **kwargs):

        # Merge arguments
        _params.update(kwargs)

        # Look up function name if not callable
        if not callable(_f):
            if not isinstance(_f, str) or not _f:
                _f = self.defFunKey
            if not isinstance(_f, str) or not _f or _f not in _params:
                raise Exception('Function not found : %s' % _f)
            _f = _params[_f]
            if not isinstance(_f, str) or not _f or _f not in _fm:
                raise Exception('Function map not found : %s' % _f)
            _f = _fm[_f]

        # Map the parameters
        p = []
        sig = inspect.signature(_f).parameters
        for v in sig:
            if v not in _params:
                raise Exception('Function parameter not found : %s' % v)
            p.append(_params[v])

        # Make the call
        r = _f(*p)
        if inspect.isawaitable(r):
            r = await r
        return r


    ''' Maps a message to set functions

            You can use this message to map a thread message to a function.
            This function will ensure any callback function is called.

        @param [in] f       - Function or key in the function map
        @param [in] fm      - Map of functions to call
        @param [in] msg     - dict containing function parameters to pass to function

        @begincode

            fm = {
                    'open'  : self.open,
                    'close' : self.close
                }

            @staticmethod
            async def mainThread(ctx):
                while msg := ctx.getMsg()
                    ctx.mapMsg('_funName', fm, msg)

        @endcode

    '''
    def mapMsg(self, f, fm, msg):
        try:
            r = self.mapCall(f, fm, msg['data'])
        except Exception as e:
            if callable(msg['cb']):
                msg['cb'](self, None, e)
            else:
                raise e
            return
        if callable(msg['cb']):
            msg['cb'](self, r, None)
        return r


    ''' Asynchronously maps a message to set functions

            You can use this message to map a thread message to a function.
            This function will ensure any callback function is called.

        @param [in] f       - Function or key in the function map
        @param [in] fm      - Map of functions to call
        @param [in] msg     - dict containing function parameters to pass to function

        @begincode

            fm = {
                    'open'  : self.open,
                    'close' : self.close
                }

            @staticmethod
            async def mainThread(ctx):
                while msg := ctx.getMsg()
                    ctx.mapMsg('_funName', fm, msg)

        @endcode

    '''
    async def mapMsgAsync(self, f, fm, msg):
        try:
            r = self.mapCall(f, fm, msg['data'])
            if inspect.isawaitable(r):
                r = await r
        except Exception as e:
            if callable(msg['cb']):
                cbr = msg['cb'](self, None, e)
                if inspect.isawaitable(cbr):
                    cbr = await cbr
            else:
                raise e
            return
        if callable(msg['cb']):
            cbr = msg['cb'](self, r, None)
            if inspect.isawaitable(cbr):
                cbr = await cbr
        return r


    ''' Find argument by type or return default
        @param [in] i       - Index of argument
        @param [in] t       - Type to find or list of types to find
        @param [in] d       - Default value to return if not found
        @param [in] args    - Argument lists to search
    '''
    @staticmethod
    def findByType(i, t, d, args):
        for v in args:
            match = False
            if type(t) == list:
                if (callable in t and callable(v)) or type(v) in t:
                    match = True
            elif (callable == t and callable(v)) or type(v) == t:
                match = True
            if match:
                if not i:
                    return v
                i -= 1
        return d


    ''' Make a call via the thread message loop
        @params [in] args  - In any order
                                fn[0]   - Callback function
                                            cb(returnVal, errorObj)
                                str[0]  - Name of function to call
                                dict[0] - Parameters to pass to function
        @params [in] kwargs - Keyword arguments to pass to function

        Return value will be passed to the callback if specified
    '''
    def call(self, *args, **kwargs):
        cb = self.findByType(0, callable, None, args)
        fn = self.findByType(0, str, '', args)
        params = self.findByType(0, dict, {}, args)
        params.update(kwargs)
        if fn:
            if not self.defFunKey:
                raise Exception('Default function key not set')
            params[self.defFunKey] = fn
        self.addMsg(params, cb)


    ''' Static function that handles thread
    '''
    @staticmethod
    async def threadRun(ctx, f, p):

        # Insert a pointer to our object
        pp = list(p)
        pp.insert(0, ctx)
        p = tuple(pp)

        # Allows the exit thread to keep things alive
        while ctx.wantRun():

            # While run flag is set
            while ctx.wantRun():

                try:
                    delay = f(*p)
                    if inspect.isawaitable(delay):
                        delay = await delay
                except Exception as e:
                    ctx.run = False
                    Log(e)
                    break

                if delay and 0 > delay:
                    ctx.run = False
                    break

                ctx.loops += 1

                # Maximum wait time if user didn't specify
                if None == delay:
                    delay = threading.TIMEOUT_MAX

                if delay:
                    ctx.wait(delay)

            # Run again with the run flag set to false
            try:
                r = f(*p)
                if inspect.isawaitable(r):
                    r = await r
            except Exception as e:
                ctx.run = False
                Log(e)


    ''' Sets up the async loop for the thread
    '''
    def threadLoop(self, f, p):
        asyncio.run(self.threadRun(self, f, p))


    ''' Notify's the thread, i.e. breaks the wait state
    '''
    def notify(self):
        self.cond.acquire()
        self.cond.notify()
        self.cond.release()


    ''' Enters an efficient interruptable wait state for the specified time.
        @param [in] t   - Time in milliseconds to wait.

        If notify is called, the wait state will end.

    '''
    def wait(self, t):
        if not self.run or (len(self.msgs) and self.msgwait != self.msgcnt):
            return
        self.cond.acquire()
        if self.run and (not len(self.msgs) or self.msgwait == self.msgcnt):
            self.cond.wait(t)
        self.msgwait = self.msgcnt
        self.cond.release()


    ''' Notifies the thread it should quit
    '''
    def stop(self):
        self.run = False
        self.notify()


    ''' Start the thread
    '''
    def start(self):
        self.run = True
        self.thread.start()


    ''' Notifies the thread it should quit and waits for the thread to terminate
    '''
    def join(self):
        self.run = False
        self.notify()
        if self.thread.is_alive():
            self.thread.join()


    ''' Adds a message to the threads queue
    '''
    def addMsg(self, msg, cb=None):
        self.cond.acquire()
        self.msgs.insert(0, {'data':msg, 'cb':cb})
        self.msgcnt += 1
        self.cond.notify()
        self.cond.release()


    ''' Returns a message from the threads queue
    '''
    def getMsg(self):
        if not len(self.msgs):
            return None
        self.cond.acquire()
        msg = self.msgs.pop()
        self.cond.release()
        return msg


    ''' Returns message data from the threads queue
    '''
    def getMsgData(self):
        if not len(self.msgs):
            return None
        self.cond.acquire()
        msg = self.msgs.pop()
        self.cond.release()
        return msg['data']


    ''' Returns True if the thread should keep running
    '''
    def wantRun(self):
        return self.run
