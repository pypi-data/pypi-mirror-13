#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module description
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:class:`StrTemplate` is a formatted string constructor. So you can easily 
produce ascii text easily.


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

class StrTemplate():
    @staticmethod
    def straight_line(title, length=100, linestyle="=", pad=0):
        """Return a fixed-length straight line with some text at the center.
        
        Usage Example::
            
            >>> StringTemplate.straight_line("Hello world!", 20, "-", 1)
            --- Hello world! ---
        """
        text = "{:%s^%s}" % (linestyle, length)
        return text.format("%s%s%s" % (" "*pad, title, " "*pad))

    @staticmethod
    def straight_line_show(title, length=100, linestyle="=", pad=0):
        """Print a formatted straight line.
        """
        print(StrTemplate.straight_line(
            title=title, length=length, linestyle=linestyle, pad=pad))
    
    @staticmethod
    def indented(text, howmany=1):
        """Return the text with ``howmany`` indent at begin.
        
        Usage Example::
        
            >>> StringTemplate.indented("Hello world!", 1)
                Hello world!
        """
        return "%s%s" % ("\t"*howmany, text)
    
    @staticmethod
    def indented_show(text, howmany=1):
        """Print a formatted indented text.
        """
        print(StrTemplate.pad_indent(text=text, howmany=howmany))

    @staticmethod
    def box(text, width=100, height=3, corner="+", horizontal="-", vertical="|"):
        """Return a ascii box, with your text center-aligned.
        
        Usage Example::
        
            >>> StringTemplate.box("Hello world!", 20, 5)
            +------------------+
            |                  |
            |   Hello world!   |
            |                  |
            +------------------+
        """
        if width <= len(text) - 4:
            print("width is not large enough! apply auto-adjust...")
            width = len(text) + 4
        if height <= 2:
            print("height is too small! apply auto-adjust...")
            height = 3
        if (height % 2) == 0:
            print("height has to be odd! apply auto-adjust...")
            height += 1
            
        head = tail = corner + horizontal * (width - 2) + corner
    
        pad = "%s%s%s" % (vertical, " " * (width - 2), vertical)
        pad_number = (height - 3) // 2
        
        pattern = "{: ^%s}" % (width - 2, )
        body = vertical + pattern.format(text) + vertical
        return "\n".join([head,] + [pad,] * pad_number + [body,] + [pad,] * pad_number + [tail,])
        
    @staticmethod
    def box_show(text, width=100, height=3, corner="+", horizontal="-", vertical="|"):
        """Print a formatted ascii text box.
        """
        print(StrTemplate.box(text=text, width=width, height=height,
            corner=corner, horizontal=horizontal, vertical=vertical))

#-----------------------------------------------------------------------------#
#                                  Unittest                                   #
#-----------------------------------------------------------------------------#

if __name__ == "__main__":
    import unittest
    
    class Unittest(unittest.TestCase):
        def test_straight_line(self):
            self.assertEqual(
                StrTemplate.straight_line("Hello world!", 20, "-", 1),
                "--- Hello world! ---",
            )
            
        def test_indented(self):
            self.assertEqual(
                StrTemplate.indented("Hello world!", 1),
                "\tHello world!",
            )
            
        def test_box(self):
            self.assertEqual(
                StrTemplate.box("Hello world!", 20, 5),
                ("+------------------+"
                 "\n|                  |"
                 "\n|   Hello world!   |"
                 "\n|                  |"
                 "\n+------------------+"),
            )
        
    unittest.main()