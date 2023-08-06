#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
**中文文档**

按键精灵脚本生成器。
"""

__all__ = ["BoardKey", "Script"]

class BoardKey(object):
    Alt = "Alt"
    Ctrl = "Ctrl"
    Shift = "Shift"
    Tab = "Tab"
    Space = "Space"
    Enter = "Enter"
    
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"
    G = "G"
    H = "H"
    I = "I"
    J = "J"
    K = "K"
    L = "L"
    M = "M"
    N = "N"
    O = "O"
    P = "P"
    Q = "Q"
    R = "R"
    S = "S"
    T = "T"
    U = "U"
    V = "V"
    W = "W"
    X = "X"
    Y = "Y"
    Z = "Z"

    _1 = "1"
    _2 = "2"
    _3 = "3"
    _4 = "4"
    _5 = "5"
    _6 = "6"
    _7 = "7"
    _8 = "8"
    _9 = "9"
    _0 = "0"
    
    
class Command(object):
    """
    """
    def __init__(self, name, code):
        self.name = name
        self.code = code
        
    def __str__(self):
        return self.code


class Script(object):
    """
    """
    default_delay = 0
    
    def __init__(self):
        self.lines = list()
            
    def add(self, command):
        self.lines.append(command)
    
    def to_script(self):
        return "\n".join([str(command) for command in self.lines])
    
    def to_file(self, abspath):
        with open(abspath, "wb") as f:
            f.write(self.to_script().encode("utf-8"))
    
    def set_default_delay(self, ms):
        self.default_delay = ms
    
    def _delay(self, ms):
        """Implement default delay mechanism.
        """
        if ms:
            self.Delay(ms)
        else:
            if self.default_delay:
                self.Delay(self.default_delay)
        
    # Method
    def Delay(self, ms):
        """Sleep for <ms> milliseconds.
        
        :param ms: milliseconds
        """        
        cmd = Command("Delay", "Delay %s" % ms)
        self.add(cmd)

    def SayString(self, text, delay=0):
        """Enter some text.
        
        :param text: the text you want to enter.
        """
        self._delay(delay)
        cmd = Command("SayString", 'SayString "%s"' % text)
        self.add(cmd)
    
    # Key press, down and up
    def KeyPress(self, key, n=1, delay=0):
        """Press key for n times.
        
        :param key:
        :param n: press key for n times
        """
        self._delay(delay)
        cmd = Command("KeyPress", 'KeyPress "%s", %s' % (key, n))
        self.add(cmd)
    
    def KeyDown(self, key, n=1, delay=0):
        """Press down a key.
        
        :param key:
        :param n: press down key for n times
        """
        self._delay(delay)
        cmd = Command("KeyDown", 'KeyDown "%s", %s' % (key, n))
        self.add(cmd)
            
    def KeyUp(self, key, n=1, delay=0):
        """Release a key.
        
        :param key:
        :param n: release key for n times
        """
        self._delay(delay)
        cmd = Command("KeyUp", 'KeyUp "%s", %s' % (key, n))
        self.add(cmd)
      
    def Alt(self, n=1, delay=0):
        """
        """
        self._delay(delay)
        self.add(Command("KeyPress", 'KeyPress "%s", %s' % (BoardKey.Alt, n)))
    
    def Ctrl(self, n=1, delay=0):
        """
        """
        self._delay(delay)
        self.add(Command("KeyPress", 'KeyPress "%s", %s' % (BoardKey.Ctrl, n)))
    
    def Shift(self, n=1, delay=0):
        """
        """
        self._delay(delay)
        self.add(Command("KeyPress", 'KeyPress "%s", %s' % (BoardKey.Shift, n)))
    
    def Tab(self, n=1, delay=0):
        """
        """
        self._delay(delay)
        self.add(Command("KeyPress", 'KeyPress "%s", %s' % (BoardKey.Tab, n)))

    def Space(self, n=1, delay=0):
        """
        """
        self._delay(delay)
        self.add(Command("KeyPress", 'KeyPress "%s", %s' % (BoardKey.Space, n)))
        
    def Enter(self, n=1, delay=0):
        """
        """
        self._delay(delay)
        self.add(Command("KeyPress", 'KeyPress "%s", %s' % (BoardKey.Enter, n)))
    # Combo
    def AltTab(self, n=1, delay=0):
        """Press down Alt, then press n times Tab, then release Alt.
        """
        self._delay(delay)
        self.add(Command("KeyDown", 'KeyDown "%s", %s' % (BoardKey.Alt, 1)))
        for i in range(n):
            self.add(Command("KeyPress", 'KeyPress "%s", %s' % (BoardKey.Tab, 1)))
        self.add(Command("KeyUp", 'KeyUp "%s", %s' % (BoardKey.Alt, 1)))
    
    def Ctrl_C(self, delay=0):
        """Ctrl + C shortcut.
        """
        self._delay(delay)
        self.add(Command("KeyDown", 'KeyDown "%s", %s' % (BoardKey.Ctrl, 1)))
        self.add(Command("KeyPress", 'KeyPress "%s", %s' % (BoardKey.C, 1)))
        self.add(Command("KeyUp", 'KeyUp "%s", %s' % (BoardKey.Ctrl, 1)))

    def Ctrl_V(self, delay=0):
        """Ctrl + V shortcut.
        """
        self._delay(delay)
        self.add(Command("KeyDown", 'KeyDown "%s", %s' % (BoardKey.Ctrl, 1)))
        self.add(Command("KeyPress", 'KeyPress "%s", %s' % (BoardKey.V, 1)))
        self.add(Command("KeyUp", 'KeyUp "%s", %s' % (BoardKey.Ctrl, 1)))

    def Ctrl_W(self, delay=0):
        """Ctrl + W shortcut.
        """
        self._delay(delay)
        self.add(Command("KeyDown", 'KeyDown "%s", %s' % (BoardKey.Ctrl, 1)))
        self.add(Command("KeyPress", 'KeyPress "%s", %s' % (BoardKey.W, 1)))
        self.add(Command("KeyUp", 'KeyUp "%s", %s' % (BoardKey.Ctrl, 1)))
          
if __name__ == "__main__":
    script = Script()
    script.set_default_delay(50)
    script.Delay(1000)
    script.SayString("Hello World")
    #
    script.KeyPress(BoardKey.Enter)
    script.KeyDown(BoardKey.Alt)
    script.KeyUp(BoardKey.Alt)
    
    # 
    script.AltTab()
    script.Ctrl_C()
    script.Ctrl_V()
    script.Ctrl_W()
    
    #
    script.to_file("anjian_script.txt")