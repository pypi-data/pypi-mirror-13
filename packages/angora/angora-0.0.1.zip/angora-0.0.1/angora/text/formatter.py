#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module description
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A special text formatter.


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

_function_words = set([
    "a", "an", "the", 
    "and", "or", "not", 
    "in", "on", "at",
    "with", "within", "as", "of",
    "to", "from", "by",
])

def fmt_title(text):
    """Article title formatter.
    
    Except functional words, first letter uppercase. Example:
    "Google Killing Annoying Browsing Feature"
    
    **中文文档**
    
    文章标题的格式, 除了虚词, 每个英文单词的第一个字母大写。
    """
    if len(text) == 0: # if empty string, return it
        return text
    else: 
        text = text.lower() # lower all char
        # delete redundant empty space 
        chunks = [chunk for chunk in text.split(" ") if len(chunk) >= 1]
        
        new_chunks = list()
        for chunk in chunks:
            if chunk not in _function_words:
                chunk = chunk[0].upper() + chunk[1:]
            new_chunks.append(chunk)
            
        new_chunks[0] = new_chunks[0][0].upper() + new_chunks[0][1:]
        
        return " ".join(new_chunks)

def fmt_sentence(text):
    """English sentence formatter. 
    
    First letter is always upper case. Example:
    "Do you want to build a snow man?"
    
    **中文文档**
    
    句子格式。每句话的第一个单词第一个字母大写。
    """
    if len(text) == 0: # if empty string, return it
        return text
    else:
        text = text.lower() # lower all char
        # delete redundant empty space 
        chunks = [chunk for chunk in text.split(" ") if len(chunk) >= 1]
        chunks[0] = chunks[0][0].upper() + chunks[0][1:]
        return " ".join(chunks)
        
def fmt_name(text):
    """Person name formatter. 
    
    For all words first letter uppercase. The rests lowercase. Single empty
    space separator. Example: "James Bond"
    
    **中文文档**
    
    人名格式。每个单词的第一个字母大写。
    """
    if len(text) == 0: # if empty string, return it
        return text
    else:
        text = text.lower() # lower all char
        # delete redundant empty space 
        chunks = [chunk[0].upper() + chunk[1:] for chunk in text.split(" ") if len(chunk) >= 1]
        return " ".join(chunks)

#-----------------------------------------------------------------------------#
#                                  Unittest                                   #
#-----------------------------------------------------------------------------#

if __name__ == "__main__":
    import unittest
    
    class Unittest(unittest.TestCase):
        def test_fmt_title(self):
            title = " google   killing annoying  browsing   feature   "
            self.assertEqual(fmt_title(title), 
                             "Google Killing Annoying Browsing Feature")
            
        def test_fmt_sentence(self):
            sentence = " do you want   to build  a snow man?   "
            self.assertEqual(fmt_sentence(sentence), 
                             "Do you want to build a snow man?")
            
        def test_fmt_name(self):
            name = " michael   jackson  "
            self.assertEqual(fmt_name(name), "Michael Jackson")
            
    unittest.main()