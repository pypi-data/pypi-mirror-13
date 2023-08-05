#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module description
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
本模组用于调用常用的键盘鼠标宏命令


Compatibility
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- Python2: Yes
- Python3: Yes


Prerequisites
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- pyperclip, 用于将python变量中的字符串拷贝到剪贴板
  https://pypi.python.org/pypi/pyperclip
- PyUserInput, 用于调用windows api模拟鼠标键盘命令
  https://pypi.python.org/pypi/PyUserInput
"""

from __future__ import print_function
try:
    from pymouse import PyMouse
    from pykeyboard import PyKeyboard
except ImportError as e:
    print("[Failed to do 'from pymouse import PyMouse', "
          "please install PyUserInput]: %s" % e)
import time

class Bot():
    def __init__(self):
        self.mouse = PyMouse()
        self.keyboard = PyKeyboard()
    
    def Delay(self, n):
        time.sleep(n)
    
    """ ====== Mouse Macro ====== """
    def Left_click(self, x, y, n = 1, dl = 0):
        """在屏幕某点左键点击若干次
        """
        self.Delay(dl)
        self.mouse.click(x, y, 1, n)
    
    def Right_click(self, x, y, n = 1, dl = 0):
        """在屏幕某点右键点击若干次
        """
        self.Delay(dl)
        self.mouse.click(x, y, 2, n)
    
    def Double_click(self, x, y, dl = 0):
        """在屏幕的某点双击
        """
        self.Delay(dl)
        self.mouse.click(x, y, 1, n = 2)
    
    def Scroll_up(self, n, dl = 0):
        """鼠标滚轮向上n次
        """
        self.Delay(dl)
        self.mouse.scroll(vertical = n)
    
    def Scroll_down(self, n, dl = 0):
        """鼠标滚轮向下n次
        """
        self.Delay(dl)
        self.mouse.scroll(vertical = -n)
    
    def Move_to(self, x, y, dl = 0):
        """鼠标移动到x, y的坐标处
        """
        self.Delay(dl)
        self.mouse.move(x, y)
    
    def Drag_and_release(self, start, end, dl = 0):
        """从start的坐标处鼠标左键单击拖曳到end的坐标处
        start, end是tuple. 格式是(x, y)
        """
        self.Delay(dl)
        self.mouse.press(start[0], start[1], 1)
        self.mouse.drag(end[0], end[1])
        self.Delay(0.1)
        self.mouse.release(end[0], end[1], 1)
    
    def Screen_size(self):
        width, height = self.mouse.screen_size()
        return width, height
    
    def WhereXY(self):
        x_axis, y_axis = self.mouse.position()
        return x_axis, y_axis
    
    """ ====== Keyboard Macro ====== """
    """COMBINATION组合键"""
    """Ctrl系列"""
    
    def Ctrl_c(self, dl = 0):
        """Ctrl + c 复制
        """
        self.Delay(dl)
        self.keyboard.press_key(self.keyboard.control_key)
        self.keyboard.tap_key("c")
        self.keyboard.release_key(self.keyboard.control_key)
    
    def Ctrl_x(self, dl = 0):
        """Ctrl + x 剪切
        """
        self.Delay(dl)
        self.keyboard.press_key(self.keyboard.control_key)
        self.keyboard.tap_key("x")
        self.keyboard.release_key(self.keyboard.control_key)
        
    def Ctrl_v(self, dl = 0):
        """Ctrl + v 粘贴
        """
        self.Delay(dl)
        self.keyboard.press_key(self.keyboard.control_key)
        self.keyboard.tap_key("v")
        self.keyboard.release_key(self.keyboard.control_key)
    
    def Ctrl_z(self, dl = 0):
        """Ctrl + z 撤销上一次操作
        """
        self.Delay(dl)
        self.keyboard.press_key(self.keyboard.control_key)
        self.keyboard.tap_key("z")
        self.keyboard.release_key(self.keyboard.control_key)
        
    def Ctrl_y(self, dl = 0):
        """Ctrl + y 重复上一次操作
        """
        self.Delay(dl)
        self.keyboard.press_key(self.keyboard.control_key)
        self.keyboard.tap_key("y")
        self.keyboard.release_key(self.keyboard.control_key)
    
    def Ctrl_a(self, dl = 0):
        """Ctrl + a 全选
        """
        self.Delay(dl)
        self.keyboard.press_key(self.keyboard.control_key)
        self.keyboard.tap_key("a")
        self.keyboard.release_key(self.keyboard.control_key)
        
    def Ctrl_Fn(self, n, dl = 0):
        """Ctrl + Fn1~12 组合键
        """
        self.Delay(dl)
        self.keyboard.press_key(self.keyboard.control_key)
        self.keyboard.tap_key(self.keyboard.function_keys[n])
        self.keyboard.release_key(self.keyboard.control_key)
    
    """Alt系列"""
    def Alt_Tab(self, dl = 0):
        """Alt + Tab 组合键
        """
        self.Delay(dl)
        self.keyboard.press_key(self.keyboard.alt_key)
        self.keyboard.tap_key(self.keyboard.tab_key)
        self.keyboard.release_key(self.keyboard.alt_key)
    
    def Alt_Fn(self, n, dl = 0):
        """Alt + Fn1~12 组合键
        """
        self.Delay(dl)
        self.keyboard.press_key(self.keyboard.alt_key)
        self.keyboard.tap_key(self.keyboard.function_keys[n])
        self.keyboard.release_key(self.keyboard.alt_key)
    
    """SINGLE KEY单个键盘键"""
    
    def Up(self, n = 1, dl = 0):
        """上方向键n次
        """
        self.Delay(dl)
        self.keyboard.tap_key(self.keyboard.up_key, n)
        
    def Down(self, n = 1, dl = 0):
        """下方向键n次
        """
        self.Delay(dl)
        self.keyboard.tap_key(self.keyboard.down_key, n)
    
    def Left(self, n = 1, dl = 0):
        """左方向键n次
        """
        self.Delay(dl)
        self.keyboard.tap_key(self.keyboard.left_key, n)
        
    def Right(self, n = 1, dl = 0):
        """右方向键n次
        """
        self.Delay(dl)
        self.keyboard.tap_key(self.keyboard.right_key, n)
    
    def Enter(self, n = 1, dl = 0):
        """回车键/换行键n次
        """
        self.Delay(dl)
        self.keyboard.tap_key(self.keyboard.enter_key, n)
    
    def Delete(self, n = 1, dl = 0):
        """删除键n次
        """
        self.Delay(dl)
        self.keyboard.tap_key(self.keyboard.delete_key, n)
    
    def Back(self, n = 1, dl = 0):
        """退格键n次
        """
        self.Delay(dl)
        self.keyboard.tap_key(self.keyboard.backspace_key, n)
        
    def Space(self, n = 1, dl = 0):
        """空格键n次
        """
        self.Delay(dl)
        self.keyboard.tap_key(" ", n)
    
    def Fn(self, n, dl = 0):
        """功能键n次
        """
        self.Delay(dl)
        self.keyboard.tap_key(self.keyboard.function_keys[n])
        
    def Char(self, char, n = 1, dl = 0):
        """输入任意单字符n次，只要能在键盘上打出来的字符都可以
        """
        if len(char) == 1:
            self.Delay(dl)
            self.keyboard.tap_key(char)
        else:
            raise Exception("""method "Char()" can only take one character.""")
    
    def Type_string(self, text, interval = 0, dl = 0):
        """键盘输入字符串，interval是字符间输入时间间隔，单位"秒"
        """
        self.Delay(dl)
        self.keyboard.type_string(text, interval)


if __name__ == "__main__":
    bot = Bot()
    def unittest1():
        """测试键盘命令"""
        bot.Up(dl = 1)
        bot.Down(dl = 1)
        bot.Left(dl = 1)
        bot.Right(dl = 1)

    unittest1()
    
    def unittest2():
        """测试鼠标命令"""
        print( bot.Screen_size() )
        print( bot.WhereXY() )
        
    unittest2()