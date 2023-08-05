#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module description
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**中文文档**

Log是一个简单的日志文件夹和日志文件的管理小工具, 能捕获到的异常和自定义错误信息
写入到本地日志文秘口岸中, 并在屏幕上以自定义的缩进形式将错误信息打印出来。用户
可以设定写入日志时是否同时打印到屏幕上, 并可以自定义缩进大小。

建议在用到try, except语法时, 在except语法块中使用::

    Log.write(message, index, indent, enable_verbose)


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
import datetime
import os

class Log(object):
    """
    
    **中文文档**
    
    当初始化Log类的时候, 会自动在脚本运行所在目录创建一个叫log的目录(用户也可以
    自定义这个目录)。每当 ``try, except``时, 在人类能预计错误的情况下, 可以用:
    ``Log.write(index, message)`` 方法把日志写入名为 ``%Y-%m-%d %H_%M_%S.txt`` 的
    日志文件中。(index和message由用户自己定义了)
    
    而在无法预知错误的情况下, 可以用::
    
        import sys
        Log.write(index=sys.exc_info()[0], message=sys.exc_info()[1])
        
    把捕获到的异常写入日志。
    """
    def __init__(self, log_dir="log"):
        self.fname = "%s.txt" % datetime.datetime.strftime(
            datetime.datetime.now(), "%Y-%m-%d %H_%M_%S")
        self.log_dir = os.path.abspath(log_dir)
        if not os.path.exists(self.log_dir):
            os.mkdir(self.log_dir)

    def write(self, message, index="unknown", indent=1, enable_verbose=True):
        """Write line to local log file. And automatically print log info.
        
        log line format: <#datetime><#index><#message>
    
        :param message: log text message
        :type message: string
        
        :param index: type of this log
        :type index: string

        :param indent: how many indent added to the message head when printing
        :type indent: int
        
        :param enable_verbose: print message while writing to log or not
        :type enable_verbose: boolean
        
        **中文文档**
        
        把异常信息写入日志，并自动打印出来
        """
        line = "<%s><%s><%s>\n" % (datetime.datetime.now(),
                                   index,
                                   message)
        with open(os.path.join(self.log_dir, self.fname), "a") as f:
            f.write(line)
        if enable_verbose:
            print("%s<%s><%s>" % ("\t" * indent, index, message) ) # print log info
    
if __name__ == "__main__":
    import unittest
    class LogUnittest(unittest.TestCase):
        def test_all(self):
            log = Log()
            log.write("Hey processor dictionary error", "Key Error")
            
    unittest.main() # 测试完毕后请手动删除Log目录