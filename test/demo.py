#!/usr/bin/env python3

import asyncio
import threadmsg as tm

async def run():

    #--------------------------------------------------------------------
    # Example 1

    async def msgThread(ctx):

        # Check for message
        msg = ctx.getMsg()
        if not msg:
            return

        print(msg)

        # Return a negative number to exit thread
        return -1

        # Return a positive number and this function will be
        # called again after that number of seconds
        return 3.5

        # Return zero this function will be called again immediately
        return 0

        # Return nothing for inifinite wait, this function will only
        # be called again if a message is posted or quit is requested
        return


    # Create a thread
    t1 = tm.ThreadMsg(msgThread)

    # Send message to thread
    t1.addMsg("Hello thread")

    # Wait for thread to exit
    t1.join()


    #--------------------------------------------------------------------
    # Example 2

    async def myThread(ctx, v1, v2):

        # Verify parameters
        assert 5 == v1
        assert 6 == v2

        # Check if this is the first run
        if not ctx.loops:
            print('First call')
            return 0

        # Check if thread is exiting
        if not ctx.run:
            print('Thread is exiting')
            return

        print('Second call')

        # Exit thread
        return -1


    # Create a thread, but don't start it
    t1 = tm.ThreadMsg(myThread, (5, 6), False)

    # Start thread
    t1.start()

    # Wait for thread to exit
    t1.join()


    #--------------------------------------------------------------------
    # Example 3

    class funThread(tm.ThreadMsg):

        def __init__(self, start=True):
            super().__init__(self.msgThread, deffk='_funName', start=start)
            self.callMap = {
                    'add': self.add
                }

        @staticmethod
        async def msgThread(ctx):
            while msg := ctx.getMsg():
                await ctx.mapMsgAsync(None, ctx.callMap, msg)
            # return nothing so this function is only
            # called again when there is a message

        def add(self, a, b):
            return a + b


    # Create the thread
    t1 = funThread()

    def showReturn(ctx, params, retval, err):
        print(params, retval, err)

    # Call add function with callback
    t1.call(showReturn, 'add', a=1, b=2)

    # Wait for reply from add function
    reply = t1.call('add', a=1, b=2)
    await reply.wait(3)
    print(reply.getData())

    # Signal thread to quit
    t1.stop()

    # Wait for thread to exit
    t1.join()

    # Or call join with True to both signal quit and wait for exit
    # tw.join(True)


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run())
