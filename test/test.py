#!/usr/bin/env python3

import time
import asyncio
import threadmsg as tm

try:
    import sparen
    Log = sparen.log
except:
    Log = print


#------------------------------------------------------------------------------
# Test 1

def test_1():

    def f1():
        Log('f1()')
        return 55

    a = [11, 21, 'hi', [1,2,3], 31, {'a':'b'}, 41, f1]
    Log(a)

    Log(tm.ThreadMsg.findByType(0, int, None, a))
    assert 11 == tm.ThreadMsg.findByType(0, int, 0, a)
    assert 21 == tm.ThreadMsg.findByType(1, int, 0, a)
    assert 31 == tm.ThreadMsg.findByType(2, int, 0, a)
    assert 41 == tm.ThreadMsg.findByType(3, int, 0, a)
    assert 'hi' == tm.ThreadMsg.findByType(0, str, '', a)
    assert 'hi' == tm.ThreadMsg.findByType(2, [str, int], '', a)
    assert 1 == tm.ThreadMsg.findByType(0, list, [], a)[0]
    assert 'b' == tm.ThreadMsg.findByType(0, dict, {}, a)['a']
    assert 55 == tm.ThreadMsg.findByType(1, [list, callable], None, a)()


#------------------------------------------------------------------------------
# Test 2

g_value = 0
async def countThread(ctx, v1, v2):

    global g_value

    assert 5 == v1
    assert 6 == v2

    if not ctx.loops:
        Log('First call')

    if not ctx.run:
        Log('Thread is exiting')

    g_value += 1
    Log(g_value)
    return .5



def test_2():

    global g_value

    assert g_value == 0

    Log('Starting thread')
    t1 = tm.ThreadMsg(countThread, (5, 6), False)

    t1.start()

    time.sleep(2)

    t1.stop()

    t1.join()
    Log('Thread has exited')

    # Count should be about 5
    Log(g_value)
    assert 3 < g_value and 8 > g_value


#------------------------------------------------------------------------------
# Test 3

g_loopCount = 0
g_testMsg = "Hello thread"

async def msgThread(ctx):

    global g_value, g_loopCount

    if not ctx.run:
        Log('Thread is exiting')

    g_loopCount += 1

    msg = ctx.getMsgData()
    if not msg:
        return

    g_value = 1
    Log(msg)

    assert msg == g_testMsg

    return -1


def test_3():

    global g_value, g_loopCount

    g_value = 0
    g_loopCount = 0
    t1 = tm.ThreadMsg(msgThread)

    t1.addMsg(g_testMsg)

    t1.join()

    assert g_value == 1
    assert g_loopCount <= 3

    Log(g_loopCount)


#------------------------------------------------------------------------------
# Test 4

class funThread(tm.ThreadMsg):

    def __init__(self):
        self.count = 0
        self.callMap = {
                'fun1': self.fun1,
                'fun2': self.fun2
            }
        super().__init__(self.msgThread, deffk='_funName')

    @staticmethod
    async def msgThread(ctx):
        while msg := ctx.getMsg():
            await ctx.mapMsgAsync(None, ctx.callMap, msg)

    def fun1(self, a, b):
        Log('fun1()')
        assert a == 1
        assert b == 2
        return a + b

    async def fun2(self, a, b):
        Log('fun2()')
        assert a == 1
        assert b == 2
        return a + b


async def test_4():

    ctx = funThread()

    def checkReturn(ctx, p, r, e):
        if e:
            Log(e)
        else:
            Log(r)
            assert 3 == r

    # Queue function calls
    ctx.call(checkReturn, 'fun1', a=1, b=2)
    ctx.call(checkReturn, _funName='fun1', a=1, b=2)
    ctx.call(checkReturn, {'_funName':'fun2', 'a':1}, b=2)
    ctx.addMsg({'_funName': 'fun1', 'a': 1, 'b': 2})
    ctx.addMsg({'_funName': 'fun2', 'a': 1, 'b': 2})

    reply = ctx.call('fun1', a=1, b=2)
    assert await reply.wait(5)
    assert reply.getData() == 3

    ctx.join(True)


#------------------------------------------------------------------------------
# Test 5

async def waitThread(ctx, tmr):

    time.sleep(1)

    tmr.setData(True)

def test_5():

    # Check reply object without event loop
    tmr = tm.ThreadMsg.ThreadMsgReply(None)

    t1 = tm.ThreadMsg(waitThread, (tmr,))

    mx = 5
    while 0 < mx and not tmr.isData():
        Log('.')
        mx -= 1
        time.sleep(.25)

    assert tmr.isData()

    t1.join(True)


#------------------------------------------------------------------------------

async def run():
    test_1()
    test_2()
    test_3()
    await test_4()
    test_5()


def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run())


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        Log(e)
