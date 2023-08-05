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
A Python code, comment, docstr line counter utility.


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
import re
import os

class CodeStats(object):
    """A simple Python project code, comment, docstr line counter.
    
    Code stats analyzer should be initiated with the project workspace path and
    the programming language. 
    
    - code: number of code lines, includes docstr.
    - comment: number of comment lines.
    - docstr: number of doc string lines.
    - purecode: code lines not include docstr.
    
    Usage example::

        >>> from weatherlab.lib.gadget import *
        >>> counter = CodeStats(workspace=r"C:\myproject", language="Python")
        >>> counter.run()
        code line: xxx
        comment line: xxx
        docstr line: xxx
        purecode line: xxx
        
    **中文文档**
    
    :class:`CodeStats` 是一个用来统计Python项目中所有文件的代码, 注释和
    文档字符串行数的小工具。下面是对这些名词的说明:
    
    - code (代码): 代码行数, 包括文档字符串。
    - comment (注释): 注释行数。
    - docstr (文档字符串): 文档字符串行数。
    - purecode (纯代码): 纯代码不包括文档字符串。
    
    用例::
        
        >>> from weatherlab.lib.gadget import *
        >>> counter = CodeStats(workspace=r"C:\myproject", language="Python")
        >>> counter.run()
        code line: xxx
        comment line: xxx
        docstr line: xxx
        purecode line: xxx
        
    """
    _ext = {
        "python": ".py"
    }
    def __init__(self, workspace, language="Python"):
        if not os.path.exists(workspace):
            raise FileNotFoundError("%s doesn't exists!" % workspace)
        self.dir = os.path.abspath(workspace)
        self.ext = self._ext[language.lower()]
        
    def run(self):
        """Run analysis.
        
        The basic idea is to recursively find all script files in specific 
        programming language, and analyze each file then sum it up.
        """
        code, comment, docstr = 0, 0, 0
        
        for current_dir, _, filelist in os.walk(self.dir):
            for basename in filelist:
                _, ext = os.path.splitext(basename)
                if ext == self.ext:
                    abspath = os.path.join(current_dir, basename)
                    with open(abspath, "rb") as f:
                        code_text = f.read().decode("utf-8")
                        res = self.analyze_python(code_text)
                        code += res[0]
                        comment += res[1]
                        docstr += res[2]
                        
        purecode = code - docstr
           
        print("code line: %s" % code)
        print("comment line: %s" % comment)
        print("docstr line: %s" % docstr)
        print("purecode line: %s" % purecode)
        
    def analyze_python(self, code_text):
        """Count how many line of code, comment, dosstr, purecode in one 
        Python script file.
        """
        code, comment, docstr = 0, 0, 0
        
        p1 = r"""(?<=%s)[\s\S]*?(?=%s)""" % ('"""', '"""')
        p2 = r"""(?<=%s)[\s\S]*?(?=%s)""" % ("'''", "'''")
        
        # count docstr
        for pattern in [p1, p2]:
            for res in re.findall(pattern, code_text)[::2]:
                lines = [i.strip() for i in res.split("\n") if i.strip()]
                docstr += len(lines)
        
        # count comment line and code
        lines = [i.strip() for i in code_text.split("\n") if i.strip()]
        for line in lines:
            if line.startswith("#"):
                comment += 1
            else:
                code += 1
        purecode = code - docstr # pure code = code - docstr
        return code, comment, docstr, purecode
        
if __name__ == "__main__":
    import site
    
    workspace = os.path.join(site.getsitepackages()[1], "angora")
    counter = CodeStats(workspace)
    counter.run()