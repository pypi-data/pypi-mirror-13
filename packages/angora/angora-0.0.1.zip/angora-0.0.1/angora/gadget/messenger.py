#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module description
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Messenger is an utility to easily disable or enable all your ``print()`` function.


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

class Messenger(object):
    """Messenger is an utility to easily disable or enable all your ``print()`` 
    function.

    Sometime you may have a lots of ``print("something")`` in your script. But 
    how about if you want to disable them all or part of them? Usually we have 
    to comment them all. 
    
    Now you can call ``Messenger.off()`` to disable all ``print("your message")``.
    Similarly, you can call ``Messenger.on()`` to enable print function.
    
    Usage guide:
    
    - create an instance: ``messenger = Messenger()``
    - replace all your print("your message") with messenger.show("your message)
    - call ``messenger.off()`` to disable all ``messenger.show()``
    - call ``messenger.on()`` to enable all ``messenger.show()``
            
    **中文文档**
    
    在Python程序中为了调试方便, 我们通常会有大量的 ``print()``。但如果我们想要一次
    性禁用大量的打印功能, 我们就需要很麻烦的注释掉许多print()。
    
    Messenger解决这一问题的思路是:
    
    每当我们想要用 ``print()`` 的时候, 我们可以使用Messenger.show("your message")
    
    我们只需要调用Messenger.off()即可禁用之后所有的打印功能。同样如果需要恢复
    打印功能, 我们只需要调用Messenger.on()即可。
    """
    def __init__(self, enable_verbose=True):
        """echo=False to disable all Messenger.show()
        """
        self.enable_verbose = enable_verbose
        if self.enable_verbose:
            self.show = self._print_screen
        else:
            self.show = self._not_print_screen
            
    def _print_screen(self, text):
        print(text)
        
    def _not_print_screen(self, text):
        pass

    def on(self):
        """enable Messenger.show()"""
        self.show = self._print_screen
        
    def off(self):
        """disable Messenger.show()"""
        self.show = self._not_print_screen

messenger = Messenger()

if __name__ == "__main__":
    import unittest
    
    class MessengerUnittest(unittest.TestCase):
        def test_all(self):
            messenger = Messenger()
            messenger.show("hello world 1")
            messenger.off()
            messenger.show("hello world 2")
            messenger.on()
            messenger.show("hello world 3")
            
    unittest.main()