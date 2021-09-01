#!/usr/bin/env python3

from __future__ import print_function
import threading
import asyncio
import traceback

Log = print

#==================================================================================================

''' Run specified function in a new async loop
    @param [in] f   - Function to run
'''
def asyncLoop(f):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(f)
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()


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
    '''
    def __init__(self, f, p=(), start=True):

        self.msgs = []
        self.msgcnt = 0
        self.msgwait = 0
        self.run = True
        self.loops = 0
        self.lock = threading.Lock()
        self.cond = threading.Condition(self.lock)

        # Thread
        self.thread = threading.Thread(target=self.threadLoop, args=(f, p,))
        if start:
            self.thread.start()


    ''' Destructor
    '''
    def __del__(self):
        self.join()


    ''' Static function that handles thread
    '''
    @staticmethod
    async def threadRun(ctx, f, p):

        # Insert a pointer to our object
        pp = list(p)
        pp.insert(0, ctx)
        p = tuple(pp)

        # While run flag is set
        while ctx.wantRun():

            try:
                delay = await f(*p)
            except Exception as e:
                Log(traceback.format_exc())
                ctx.run = False
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
            await f(*p)
        except Exception as e:
            Log(traceback.format_exc())


    ''' Sets up the async loop for the thread
    '''
    def threadLoop(self, f, p):
        asyncLoop(self.threadRun(self, f, p))


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
        self.thread.join()


    ''' Adds a message to the threads queue
    '''
    def addMsg(self, msg):
        self.cond.acquire()
        self.msgs.insert(0, msg)
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


    ''' Returns True if the thread should keep running
    '''
    def wantRun(self):
        return self.run
