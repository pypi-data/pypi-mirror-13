#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module description
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Provides some programming control flow recipes.


Compatibility
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- Python2: Yes
- Python3: Yes


Prerequisites
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- None


Class, method, function, exception
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from __future__ import print_function

def try_until_succeed(_warning_period, func, *argv, **kwarg):
    """Try a function until it successfully returns.
    
    Print current exception every ``_warning_period`` times try.
    
    **中文文档**
    
    尝试一个函数直到其成功为止。不适用于会出现死循环的函数。
    
    每隔``_warning_period``次失败, 就会打印当前异常和尝试次数。
    """
    if (not isinstance(_warning_period, int)) or (_warning_period < 1):
        raise Exception("'_warning_period' argument has to be int "
                        "and greater than 0")
        
    counter = 1
    while 1:
        try:
            return func(*argv, **kwarg)
        except Exception as e:
            current_exception = e
            counter += 1
            if (counter % _warning_period) == 0:
                print("Warning: this is %sth try, current error is "
                      "%s" % (counter, repr(current_exception)))

def try_ntimes(_howmany, func, *argv, **kwarg):
    """Try a function n times.
    
    Try to execute func(*argv, **kwarg) ``_howmany`` times. If it successfully run 
    one time, then return as normal. If it fails N times, then raise the 
    exception in the last run.
    
    **中文文档**
    
    反复尝试一个函数或方法``_howmany``次。
    
    对func函数使用try, except, pass 若干次, 期间只要有一次成功, 就正常返回。
    如果一次都没有成功, 则行为跟最后一次执行了func(*argv, **kwarg)函数一样。
    
    这个实现利用了python中可以把函数作为一个参数传入另一个函数的特质, 将func
    函数中的参数原封不动地封装到了try_ntimes的参数中。只用一个额外参数``_howmany``
    控制重复次数。
    """
    if (not isinstance(_howmany, int)) or (_howmany < 1):
        raise Exception("'_howmany' argument has to be int and greater than 0")
    
    counter = 1
    while counter <= _howmany:
        try:
            return func(*argv, **kwarg)
        except Exception as e:
            current_exception = e
            counter += 1
    raise current_exception

if __name__ == "__main__":
    import random

    def gamble(bet_on, number_of_choice):
        """throw a dice from 1 - #number_of_choice, if it is #bet_on, you win.
        otherwise, throw an exception.
        """
        if bet_on == random.randint(1, number_of_choice):
            print("it's %s, you win !!" % bet_on)
        else:
            raise Exception("Sorry, you lose!!")

    def usage_try_until_succeed():
        print("\n=== usage example try_until_succeed() ===")
        try_until_succeed(10, gamble, bet_on=3, number_of_choice=50)
    
#     usage_try_until_succeed()
    
    def usage_try_ntimes():
        print("\n=== usage example try_ntimes() ===")
        try_ntimes(5, gamble, bet_on=3, number_of_choice=10)
    
#     usage_try_ntimes()
    
