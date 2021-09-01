
# threadmsg

Thread safe message queue

---------------------------------------------------------------------
## Table of contents

* [Install](#install)
* [Examples](#examples)
* [References](#references)

&nbsp;

---------------------------------------------------------------------
## Install

    $ pip3 install threadmsg

&nbsp;


---------------------------------------------------------------------
## Examples

``` Python

    import threadmsg as tm

    #--------------------------------------------------------------------
    # Example 1

    # Process messages
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


    # Create a thread, but don't start it
    t1 = tm.ThreadMsg(myThread, (5, 6), False)

    # Start thread
    t1.start()

    # Signal thread to quit
    t1.stop()

    # Wait for thread to exit
    t1.join()


```

&nbsp;


---------------------------------------------------------------------
## References

- Python
    - https://www.python.org/

- pip
    - https://pip.pypa.io/en/stable/

