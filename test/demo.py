#!/usr/bin/env python3

import threadmsg as tm

#--------------------------------------------------------------------
# Example 1

async def msgThread(ctx):

    # Check for message
    msg = ctx.getMsg()
    if not msg:
        return

    print(msg)


# Create a thread
t1 = tm.ThreadMsg(msgThread)

# Send message to thread
t1.addMsg("Hello thread")

# Signal thread to quit and wait for thread to exit
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

    # Check if thread is exiting
    if not ctx.run:
        print('Thread is exiting')

    # Exit thread
    return -1


# Create a thread, but don't start it
t1 = tm.ThreadMsg(myThread, (5, 6), False)

# Start thread
t1.start()

# Signal thread to quit
t1.stop()

# Wait for thread to exit
t1.join()

