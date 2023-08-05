#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module description
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module is to make regular expression easier to use.
With some built-in compiled pattern, we can use human language-like syntax to 
generate re pattern.


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
import re

class ReParser(object):
    """An re-parser extract text using many useful built-in patterns.
    """
    
    @staticmethod
    def extract_by_prefix_surfix(prefix, surfix, maxlen, text):
        """Extract the text in between a prefix and surfix.
        
        :param prefix: the prefix
        :type prefix: str
        
        :param surfix: the surfix
        :type surfix: str
        
        :param maxlen: the max matched string length
        :type maxlen: int
        
        :param text: text body
        :type text: str
        """
        pattern = r"""(?<=%s)[\s\S]{1,%s}(?=%s)""" % (prefix, maxlen, surfix)
        return re.findall(pattern, text)

#-----------------------------------------------------------------------------#
#                                  Unittest                                   #
#-----------------------------------------------------------------------------#

if __name__ == "__main__":
    import unittest
    
    class ReParserUnittest(unittest.TestCase):
        def test_extract_by_prefix_surfix(self):
            self.assertEqual(
                ReParser.extract_by_prefix_surfix(
                    "<div>", 
                    "</div>", 
                    100, 
                    "<a>中文<div>some text</div>英文</a>"),     
                ["some text",]
            )
            
    unittest.main()
