#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2015 by Sanhe Hu
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- Author: Sanhe Hu
- Email: husanhe@gmail.com
- Lisence: MIT


Module description
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A tool can programmatically generate reConstructed Text snippet.

ref: Quick reStructuredText, 
  http://docutils.sourceforge.net/docs/user/rst/quickref.html


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

from __future__ import unicode_literals
try: # ResConstructor.table method requires 'prettytable' extension.
    from prettytable import PrettyTable
except ImportError:
    pass

class RstConstructor(object):
    """reConstructed Text snippet constructor.
    """
    def header(self, title, level, key, width=80):
        """Example::
        
            .. _header_2:
                
            Header 2
            -------------------------------------------------------------------
        
        **中文文档**
        """
        linestyle_code = {1: "=", 2: "-", 3: "~"}
        if level not in linestyle_code:
            raise Exception("'level' argument has to be 1, 2 or 3")
        else:
            linestyle = linestyle_code[level]
            
        if key:
            return "\n".join([".. _%s" % key, "", title, linestyle * width])
        else:
            return "\n".join([title, "=" * width])
         
    def reference(self, text, key):
        """Example::
        
            `Go to section 2 <section_2_>`_
        """
        return "`{text} <{key}_>`_".format(text=text, key=key)
    
    def urllink(self, text, url):
        """Example::
        
            `Google Homepage <https://www.google.com/>`_
        """
        return "`{text} <{url}>`_".format(text=text, url=url)
    
    def bullet_list(self, text):
        """Example::
        
            - item
        """
        return "- {text}".format(text=text)
    
    def enumerated_list(self, nth, text):
        """Example::
        
            1. item
        """
        if not isinstance(nth, int):
            raise Exception("'nth' argument has to be an integer!")
        return "{nth}. {text}".format(nth=nth, text=text)

    def code_block(self, code, language, indent=0):
        """Example::
        
            .. code-block:: python
            
                from __future__ import print_function
                import math
            
                print(math.sqrt(10.0))
        """
        if language not in [None, "console", "python", "ruby", "c"]:
            raise
        prefix = "\t" * indent
        code_prefix = "\t" * (indent + 1)
        lines = list()
        lines.append(prefix + ".. code-block:: %s" % language)
        lines.append(prefix)
        for line in code.split("\n"):
            lines.append(code_prefix + line.strip())
        return "\n".join(lines)
    
    def table(self, data, header=None):
        """Example::
        
            +----------+------------+
            | CityName | Population |
            +----------+------------+
            | Adelaide |  1158259   |
            +----------+------------+
            |  Darwin  |   120900   |
            +----------+------------+
        """
        if header:
            x = PrettyTable(header)
        else:
            x = PrettyTable()
        
        # construct ascii text table, split header and body    
        for row in data:
            x.add_row(row)
        s = x.get_string(border=True)
        lines = s.split("\n")
        header_ = lines[:2]
        body = lines[2:]
        n_body = len(body)
        ruler = body[0]
        
        # add more rulers between each rows
        new_body = list()
        counter = 0
        for line in body:
            counter += 1
            new_body.append(line)
            if (2 <= counter) and (counter < (n_body - 1)):
                new_body.append(ruler)
                
        if header:
            return "\n".join(header_ + new_body)
        else:
            return "\n".join(new_body)
            
rst_constructor = RstConstructor()

if __name__ == "__main__":
    rst = RstConstructor()
    
    def test_header():
        print(rst.header(title="Chapter 1", level=1, key="chapter_1"))
        print(rst.header(title="Section 1", level=2, key="section_1"))
        print(rst.header(title="Story 1", level=3, key="story_1"))
        
#     test_header()
    
    def test_reference():
        print(rst.reference("Go to Chapter 1", "chapter_1"))
    
#     test_reference()

    def test_urllink():
        print(rst.urllink("Download Python33", 
                          "https://www.python.org/downloads/release/python-335/"))
        
#     test_urllink()
    
    def test_bullet_list():
        print(rst.bullet_list("Topic 1"))
        
#     test_bullet_list()

    def test_enumerated_list():
        print(rst.enumerated_list(1, "Item 1"))
        
#     test_enumerated_list()
    
    def test_code_block():
        with open("rst.py", "rb") as f:
            code = f.read().decode("utf-8")
            print(rst.code_block(code, "python"))
    
#     test_code_block()

    def test_table():
        header = ["CityName", "Population"]
        data = [["Adelaide", 1158259], ["Darwin", 120900]]
        print(rst.table(data, header))
    
#     test_table()