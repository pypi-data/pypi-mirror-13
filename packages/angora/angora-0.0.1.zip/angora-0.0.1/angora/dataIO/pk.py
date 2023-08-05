#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module description
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module is re-pack of some pickle utility functions.

- :func:`load_pk`: Load Python Object from Pickle file.
            
- :func:`dump_pk`: Dump Picklable Python Object to file.
        
- :func:`safe_dump_pk`: An atomic write version of dump_pk, silently overwrite 
  existing file.

- :func:`obj2bytestr`: Convert arbitrary pickable Python Object to bytestr.

- :func:`bytestr2obj`: Parse Python object from bytestr.

- :func:`obj2str`: convert arbitrary object to database friendly string, using 
  base64encode algorithm.
            
- :func:`str2obj`: Parse object from base64 encoded string.


Highlight
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- :func:`load_pk`, :func:`dump_pk`, :func:`safe_dump_pk` support gzip compress,
  size is **10 - 20 times** smaller in average.


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

from __future__ import print_function, unicode_literals
import pickle, gzip
import base64
import os, shutil
import sys
import time

is_py2 = (sys.version_info[0] == 2)
if is_py2:
    pk_protocol = 2
else:
    pk_protocol = 3

def load_pk(abspath, compress=False, enable_verbose=True):
    """Load Python Object from Pickle file.

    :param abspath: File path. Use absolute path as much as you can. File 
        extension has to be ``.pickle`` or ``.gz``. (for compressed Pickle)
    :type abspath: string

    :param compress: (default False) Load from a gzip compressed Pickle file.
        Check :func:`dump_pk()<dump_pk>` function for more information.
    :type compress: boolean
    
    :param enable_verbose: (default True) Trigger for message.
    :type enable_verbose: boolean

    Usage::

        >>> from weatherlab.lib.dataIO.pk import load_pk
        >>> load_pk("test.pickle") # if you have a Pickle file
        Loading from test.pickle...
            Complete! Elapse 0.000272 sec.
        {'a': 1, 'b': 2}

    **中文文档**

    从Pickle文件中读取数据

    参数列表
    
    :param abspath: 文件路径, 扩展名需为 ``.pickle`` 或 ``.gz``
    :type abspath: ``字符串``
    
    :param compress: (默认 False) 是否从一个gzip压缩过的Pickle文件中读取数据。 请
        参考 :func:`dump_pk()<dump_pk>` 获得更多信息.
    :type compress: ``布尔值``

    :param enable_verbose: (默认 True) 是否打开信息提示开关, 批处理时建议关闭.
    :type enable_verbose: ``布尔值``
    """
    abspath = str(abspath) # try stringlize
    
    if compress: # check extension name
        if os.path.splitext(abspath)[1] != ".gz":
            raise Exception("compressed pickle has to use extension '.gz'!")
    else:
        if os.path.splitext(abspath)[1] != ".pickle":
            raise Exception("file extension are not '.pickle'!")
        
    if enable_verbose:
        print("\nLoading from %s..." % abspath)
        st = time.clock()
        
    if compress:
        with gzip.open(abspath, "rb") as f:
            obj = pickle.loads(f.read())
    else:
        with open(abspath, "rb") as f:
            obj = pickle.load(f)
        
    if enable_verbose:
        print("\tComplete! Elapse %.6f sec" % (time.clock() - st) )
        
    return obj

def dump_pk(obj, abspath, 
            pk_protocol=pk_protocol, replace=False, compress=False, 
            enable_verbose=True):
    """Dump Picklable Python Object to file.
    Provides multiple choice to customize the behavior.
    
    :param obj: Picklable Python Object.
    
    :param abspath: ``save as`` path, file extension has to be ``.pickle`` or 
        ``.gz`` (for compressed Pickle).
    :type abspath: string
    
    :param pk_protocol: (default your python version) use 2, to make a 
        py2.x/3.x compatible pickle file. But 3 is faster.
    :type pk_protocol: int
    
    :param replace: (default False) If ``True``, when you dump Pickle to a 
        existing path, it silently overwrite it. If False, an exception will be 
        raised. Default False setting is to prevent overwrite file by mistake.
    :type replace: boolean
    
    :param compress: (default False) If ``True``, use GNU program gzip to 
        compress the Pickle file. Disk usage can be greatly reduced. But you 
        have to use :func:`load_pk(abspath, compress=True)<load_pk>` in loading.
    :type compress: boolean
    
    :param enable_verbose: (default True) Trigger for message.
    :type enable_verbose: boolean

    Usage::

        >>> from weatherlab.lib.dataIO.pk import dump_pk
        >>> pk = {"a": 1, "b": 2}
        >>> dump_pk(pk, "test.pickle", replace=True)
        Dumping to test.pickle...
            Complete! Elapse 0.001763 sec

    **中文文档**
    
    将Python对象以Pickle的方式序列化, 保存至本地文件。(有些自定义类无法被序列化)
    
    参数列表
    
    :param obj: 可Pickle化的Python对象
    
    :param abspath: 写入文件的路径。扩展名必须为 ``.pickle`` 或 ``.gz``, 其中gz用于被压
        缩的Pickle
    :type abspath: ``字符串``
    
    :param pk_protocol: (默认 等于你Python的大版本号) 使用2可以使得保存的文件能被
        py2.x/3.x都能读取。但是协议3的速度更快, 体积更小, 性能更高。
    :type pk_protocol: ``整数``
    
    :param replace: (默认 False) 当为``True``时, 如果写入路径已经存在, 则会自动覆盖
        原文件。而为``False``时, 则会抛出异常。防止误操作覆盖源文件。
    :type replace: ``布尔值``
    
    :param compress: (默认 False) 当为``True``时, 使用开源压缩标准gzip压缩Pickle文件。
        通常能让文件大小缩小10-20倍不等。如要读取文件, 则需要使用函数
        :func:`load_pk(abspath, compress=True)<load_pk>`.
    :type compress: ``布尔值``
    
    :param enable_verbose: (默认 True) 是否打开信息提示开关, 批处理时建议关闭.
    :type enable_verbose: ``布尔值``
    """
    abspath = str(abspath) # try stringlize
    
    if compress: # check extension name
        root, ext = os.path.splitext(abspath)
        if ext != ".gz":
            if ext != ".tmp":
                raise Exception("compressed pickle has to use extension '.gz'!")
            else:
                _, ext = os.path.splitext(root)
                if ext != ".gz":
                    raise Exception("compressed pickle has to use extension '.gz'!")
    else:
        root, ext = os.path.splitext(abspath)
        if ext != ".pickle":
            if ext != ".tmp":
                raise Exception("file extension are not '.pickle'!")
            else:
                _, ext = os.path.splitext(root)
                if ext != ".pickle":
                    raise Exception("file extension are not '.pickle'!")
                
    if enable_verbose:
        print("\nDumping to %s..." % abspath)
        st = time.clock()
    
    if os.path.exists(abspath): # if exists, check replace option
        if replace: # replace existing file
            if compress:
                with gzip.open(abspath, "wb") as f:
                    f.write(pickle.dumps(obj, protocol=pk_protocol))
            else:
                with open(abspath, "wb") as f:
                    pickle.dump(obj, f, protocol=pk_protocol)
        else: # stop, print error message
            raise Exception("\tCANNOT WRITE to %s, "
                            "it's already exists" % abspath)
    else: # if not exists, just write to it
        if compress:
            with gzip.open(abspath, "wb") as f:
                f.write(pickle.dumps(obj, protocol=pk_protocol))
        else:
            with open(abspath, "wb") as f:
                pickle.dump(obj, f, protocol=pk_protocol)
        
    if enable_verbose:
        print("\tComplete! Elapse %.6f sec" % (time.clock() - st) )

def safe_dump_pk(obj, abspath, pk_protocol=pk_protocol, compress=False,
                 enable_verbose=True):
    """A stable version of dump_pk, silently overwrite existing file.

    When your program been interrupted, you lose nothing. Typically if your
    program is interrupted by any reason, it only leaves a incomplete file.
    If you use replace=True, then you also lose your old file.
    
    So a bettr way is to:
    
    1. dump pickle to a temp file.
    2. when it's done, rename it to #abspath, overwrite the old one.

    This way guarantee atomic write.
    
    :param obj: Picklable Python Object.
    
    :param abspath: ``save as`` path, file extension has to be ``.pickle`` or 
        ``.gz`` (for compressed Pickle).
    :type abspath: string
    
    :param pk_protocol: (default your python version) use 2, to make a 
        py2.x/3.x compatible pickle file. But 3 is faster.
    :type pk_protocol: int
    
    :param compress: (default False) If ``True``, use GNU program gzip to 
        compress the Pickle file. Disk usage can be greatly reduced. But you 
        have to use :func:`load_pk(abspath, compress=True)<load_pk>` in loading.
    :type compress: boolean
    
    :param enable_verbose: (default True) Trigger for message.
    :type enable_verbose: boolean

    Usage::

        >>> from weatherlab.lib.dataIO.pk import safe_dump_pk
        >>> pk = {"a": 1, "b": 2}
        >>> safe_dump_pk(pk, "test.pickle")
        Dumping to test.pickle...
            Complete! Elapse 0.001763 sec

    **中文文档**
    
    在对文件进行写入时, 如果程序中断, 则会留下一个不完整的文件。如果你使用了覆盖式
    写入, 则你同时也丢失了原文件。所以为了保证写操作的原子性(要么全部完成, 要么全部
    都不完成), 更好的方法是: 首先将文件写入一个临时文件中, 完成后再讲文件重命名, 
    覆盖旧文件。这样即使中途程序被中断, 也仅仅是留下了一个未完成的临时文件而已, 不会
    影响原文件。
    
    参数列表
    
    :param obj: 可Pickle化的Python对象
    
    :param abspath: 写入文件的路径。扩展名必须为 ``.pickle`` 或 ``.gz`` , 其中gz用于被压
        缩的Pickle
    :type abspath: ``字符串``
    
    :param pk_protocol: (默认 等于你Python的大版本号) 使用2可以使得保存的文件能被
        py2.x/3.x都能读取。但是协议3的速度更快, 体积更小, 性能更高。
    :type pk_protocol: ``整数``
    
    :param compress: (默认 False) 当为 ``True`` 时, 使用开源压缩标准gzip压缩Pickle文件。
        通常能让文件大小缩小10-20倍不等。如要读取文件, 则需要使用函数
        :func:`load_pk(abspath, compress=True)<load_pk>`.
    :type compress: ``布尔值``
    
    :param enable_verbose: (默认 True) 是否打开信息提示开关, 批处理时建议关闭.
    :type enable_verbose: ``布尔值``
    """
    abspath = str(abspath) # try stringlize
    temp_abspath = "%s.tmp" % abspath
    dump_pk(obj, temp_abspath, pk_protocol=pk_protocol, 
            replace=True, compress=compress, enable_verbose=enable_verbose)
    shutil.move(temp_abspath, abspath)

def obj2bytestr(obj, pk_protocol=pk_protocol):
    """Convert arbitrary pickable Python Object to bytestr.

    Usage::

        >>> from weatherlab.lib.dataIO.pk import obj2bytestr
        >>> data = {"a": 1, "b": 2}
        >>> obj2bytestr(data, pk_protocol=2)
        b'\x80\x02}q\x00(X\x01\x00\x00\x00aq\x01K\x01X\x01\x00\x00\x00bq\x02K\x02u.'

    **中文文档**

    将可Pickle化的Python对象转化为bytestr
    """
    return pickle.dumps(obj, protocol=pk_protocol)

def bytestr2obj(bytestr):
    """Parse Python object from bytestr.

    Usage::

        >>> from weatherlab.lib.dataIO.pk import bytestr2obj
        >>> b = b'\x80\x02}q\x00(X\x01\x00\x00\x00aq\x01K\x01X\x01\x00\x00\x00bq\x02K\x02u.'
        >>> bytestr2obj(b)
        {"a": 1, "b": 2}

    **中文文档**

    从bytestr中恢复Python对象
    """
    return pickle.loads(bytestr)

def obj2str(obj, pk_protocol=pk_protocol):
    """Convert arbitrary object to utf-8 string, using
    base64encode algorithm.

    Usage::

        >>> from weatherlab.lib.dataIO.pk import obj2str
        >>> data = {"a": 1, "b": 2}
        >>> obj2str(data, pk_protocol=2)
        'gAJ9cQAoWAEAAABhcQFLAVgBAAAAYnECSwJ1Lg=='

    **中文文档**

    将可Pickle化的Python对象转化为utf-8编码的"字符串"
    """
    return base64.b64encode(pickle.dumps(
        obj, protocol=pk_protocol)).decode("utf-8")

def str2obj(textstr):
    """Parse object from base64 encoded string.

    Usage::

        >>> from weatherlab.lib.dataIO.pk import str2obj
        >>> str2obj("gAJ9cQAoWAEAAABhcQFLAVgBAAAAYnECSwJ1Lg==")
        {"a": 1, "b": 2}

    **中文文档**

    从"字符串"中恢复Python对象 
    """
    return pickle.loads(base64.b64decode(textstr.encode("utf-8")))

#-----------------------------------------------------------------------------#
#                                  Unittest                                   #
#-----------------------------------------------------------------------------#

if __name__ == "__main__":
    import unittest
    import sqlite3
    
    class PKUnittest(unittest.TestCase):
        def test_write_and_read(self):
            data = {1: [1, 2], 2: ["是", "否"]} 
            safe_dump_pk(data, "data.pickle")
            data = load_pk("data.pickle") # should be a 
            self.assertEqual(data[1][0], 1)
            self.assertEqual(data[2][0], "是")
         
        def test_handle_object(self):
            python_object = {"a": 1}
            self.assertEqual(str2obj(obj2str(python_object)), python_object)
              
        def test_obj2bytestr(self):
            """pickle.dumps的结果是bytes, 而在python2中的sqlite不支持bytes直接
            插入数据库,必须使用base64.encode将bytes编码成字符串之后才能存入数据
            库。而在python3中, 可以直接将pickle.dumps的bytestr存入数据库, 这样
            就省去了base64编码的开销。
                
            注: 在python2中也有通过设定 connect.text_factory 的方法解决该问题, 
            具体内容请google
                
            This test will not pass in Python2, because sqlite python2 API
            doens't support bytes.
            """         
            conn = sqlite3.connect(":memory:")
            c = conn.cursor()
            c.execute("CREATE TABLE test (dictionary BLOB) ") # BLOB is byte
            c.execute("INSERT INTO test VALUES (?)", 
                      (obj2bytestr({1: "a", 2: "你好"}),))
              
            # see what stored in database
            print(c.execute("select * from test").fetchone())
              
            # recovery object from byte str
            self.assertDictEqual(
                bytestr2obj(c.execute("select * from test").fetchone()[0]),
                {1: "a", 2: "你好"},
                )
   
        def test_obj2str(self):
            """如果将任意python对象dump成pickle bytestr, 再通过base64 encode转化
            成ascii字符串, 就可以任意地存入数据库了。
            """
            conn = sqlite3.connect(":memory:")
            c = conn.cursor()
            c.execute("CREATE TABLE test (name TEXT) ")
            c.execute("INSERT INTO test VALUES (?)", 
                      (obj2str({1: "a", 2: "你好"}),))
              
            # see what stored in database
            print(c.execute("select * from test").fetchone())
            # recovery object from text str
            self.assertDictEqual(
                str2obj(c.execute("select * from test").fetchone()[0]),
                {1: "a", 2: "你好"},
                )
         
        def test_compress(self):
            data = {"a": list(range(32)),
                    "b": list(range(32)),}
            safe_dump_pk(data, "data.gz", compress=True)
            print(load_pk("data.gz", compress=True))
            
        def tearDown(self):
            for path in ["data.pickle", "data.gz"]:
                try:
                    os.remove(path)
                except:
                    pass
            
    unittest.main()