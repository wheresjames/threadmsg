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

    if 5 > g_value:
        g_value += 1
        Log(g_value)
        return .1

    return -1


def test_2():

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
# Test 3

g_testMsg = "Hello thread"

async def msgThread(ctx):

    global g_value

    if not ctx.run:
        Log('Thread is exiting')

    msg = ctx.getMsgData()
    if not msg:
        return

    g_value = 1
    Log(msg)

    assert msg== g_testMsg


def test_3():

    global g_value

    g_value = 0
    t1 = tm.ThreadMsg(msgThread)

    t1.addMsg(g_testMsg)

    time.sleep(1)

    t1.join()

    assert g_value == 1


#------------------------------------------------------------------------------
# Test 4

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


def test_4():

    ctx = funThread()

    def checkReturn(ctx, r, e):
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
    test_4()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        Log(e)
