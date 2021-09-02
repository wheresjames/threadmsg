#!/usr/bin/env python3

import time
import threadmsg as tm

try:
    import sparen
    Log = sparen.log
except:
    Log = print


#------------------------------------------------------------------------------
# Test 1

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


#------------------------------------------------------------------------------
# Test 2

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


#------------------------------------------------------------------------------
# Test 3

class funThread(tm.ThreadMsg):

    def __init__(self):
        super().__init__(self.msgThread, deffk='_funName')
        self.callMap = {
                'fun1': self.fun1,
                'fun2': self.fun2
            }

    @staticmethod
    async def msgThread(ctx):
        while msg := ctx.getMsg():
            ctx.mapMsg(None, ctx.callMap, msg)

    def fun1(self, a, b):
        Log('fun1()')
        assert a == 1
        assert b == 2
        return a + b

    def fun2(self, a, b):
        Log('fun2()')
        assert a == 1
        assert b == 2
        return a + b


def test_3():

    ctx = funThread()

    def checkReturn(r, e):
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

    ctx.join()


#------------------------------------------------------------------------------

def main():
    test_1()
    test_2()
    test_3()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        Log(e)
