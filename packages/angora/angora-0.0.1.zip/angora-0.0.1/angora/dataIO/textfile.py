#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module description
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module is a wrapper for text file read/write. Using auto encoding detect
if chardet is installed.


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
try:
    import chardet
except ImportError as e:
    print("[Failed to do 'import chardet']: %s" % e)

def read(path, encoding="utf-8"):
    """Auto-decoding string reader.

    Usage::

        >>> from angora.dataIO import textfile
        or
        >>> from angora.dataIO import *
        >>> textfile.read("test.txt")
    """
    with open(path, "rb") as f:
        content = f.read()
        try:
            text = content.decode(encoding)
        except:
            res = chardet.detect(content)
            text = content.decode(res["encoding"])
    return text

def write(text, path):
    """Writer text to file with utf-8 encoding.

    Usage::

        >>> from angora.dataIO import textfile
        or
        >>> from angora.dataIO import *
        >>> textfile.write("hello world!", "test.txt")

    """
    with open(path, "wb") as f:
        f.write(text.encode("utf-8"))

#-----------------------------------------------------------------------------#
#                                  Unittest                                   #
#-----------------------------------------------------------------------------#

if __name__ == "__main__":
    import unittest
    import os

    class textfileIOUnittest(unittest.TestCase):
        def test_read(self):
            print(read(r"testdata\multilanguage.txt"))
        
        def test_write(self):
            text = r"中\文, 台/湾, グー\グル, eng/lish"
            write(text, "test.txt")
            self.assertEqual(read("test.txt"), text)
            
        def tearDown(self):
            try:
                os.remove("test.txt")
            except:
                pass
            
    unittest.main()