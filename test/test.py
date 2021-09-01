#!/usr/bin/env python3

import time
import threadmsg as tm

try:
    import sparen
    Log = sparen.log
except:
    Log = print


g_value = 0
async def countThread(ctx, v1, v2):

    global g_value

    assert 5 == v1
    assert 6 == v2

    if not ctx.loops:
        Log('First call')

    if not ctx.run:
        Log('Thread is exiting')

    if 5 > g_value:
        g_value += 1
        Log(g_value)
        return .1

    return -1


def test_1():

    global g_value

    assert g_value == 0

    Log('Starting thread')
    t1 = tm.ThreadMsg(countThread, (5, 6), False)

    t1.start()

    time.sleep(2)
    assert g_value == 5

    t1.stop()

    t1.join()
    Log('Thread has exited')


async def msgThread(ctx):

    global g_value

    if not ctx.run:
        Log('Thread is exiting')

    msg = ctx.getMsg()
    if not msg:
        return

    g_value = 1
    Log(msg)


def test_2():

    global g_value

    g_value = 0
    t1 = tm.ThreadMsg(msgThread)

    t1.addMsg("Hello thread")

    time.sleep(1)

    t1.join()

    assert g_value == 1



def main():
    test_1()
    test_2()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        Log(e)
