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
A Python code, comment, docstr line analysis utility.


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

try:
    from ..filesystem import *
except:
    from angora.filesystem import *


class CodeStats(object):
    """A simple Python project code, comment, docstr line counter.

    Code stats analyzer should be initiated with the project workspace path and
    the programming language. 

    - code: number of code lines, includes docstr.
    - comment: number of comment lines.
    - docstr: number of doc string lines.
    - purecode: code lines not include docstr.

    Usage example::

        >>> from angora.gadget import CodeStats
        >>> analyzer = CodeStats(workspace=r"C:\Python33\lib\site-packages\requests")
        >>> analyzer.run()
        Code statistic result for 'C:\Python33\lib\site-packages\requests'
          79 'Python' files, 80 other files.
            code line: 12362
            comment line: 2025
            docstr line: 1545
            purecode line: 10817

    **中文文档**

    :class:`CodeStats` 是一个用来统计Python项目中所有文件的代码, 注释和
    文档字符串行数的小工具。下面是对这些名词的说明:

    - code (代码): 代码行数, 包括文档字符串。
    - comment (注释): 注释行数。
    - docstr (文档字符串): 文档字符串行数。
    - purecode (纯代码): 纯代码不包括文档字符串。

    用例::

        >>> from angora.gadget import CodeStats
        >>> analyzer = CodeStats(workspace=r"C:\Python33\lib\site-packages\requests")
        >>> analyzer.run()
        Code statistic result for 'C:\Python33\lib\site-packages\requests'
          79 'Python' files, 80 other files.
            code line: 12362
            comment line: 2025
            docstr line: 1545
            purecode line: 10817        
    """

    def __init__(self, workspace, ignore=list()):
        if not os.path.exists(workspace):
            raise FileNotFoundError("%r doesn't exists!" % workspace)
        self.workspace = os.path.abspath(workspace)
        self.ignore = ignore
        self.language = "Python"
        self.analyzer = self.analyzePython
        self.filter = self.filterPython

    def run(self):
        """Run analysis.

        The basic idea is to recursively find all script files in specific 
        programming language, and analyze each file then sum it up.
        """
        n_target_file, n_other_file = 0, 0

        code, comment, docstr, purecode = 0, 0, 0, 0

        fc = FileCollection.from_path_except(self.workspace, self.ignore)

        fc_yes, fc_no = fc.select(self.filter, keepboth=True)
        n_other_file += len(fc_no)

        for abspath in fc_yes:
            try:
                with open(abspath, "rb") as f:
                    code_text = f.read().decode("utf-8")
                    code_, comment_, docstr_, purecode_ = self.analyzer(
                        code_text)
                    code += code_
                    comment += comment_
                    docstr += docstr_
                    purecode += purecode_
                    n_target_file += 1
            except Exception as e:
                n_other_file += 1

        lines = list()
        lines.append("Code statistic result for '%s'" % self.workspace)
        lines.append("  %r %r files, %r other files." %
                     (n_target_file, self.language, n_other_file))
        lines.append("    code line: %s" % code)
        lines.append("    comment line: %s" % comment)
        lines.append("    docstr line: %s" % docstr)
        lines.append("    purecode line: %s" % purecode)
        message = "\n".join(lines)

        print(message)
        return message

    @staticmethod
    def filterPython(winfile):
        if winfile.ext == ".py":
            return True
        else:
            return False

    @staticmethod
    def analyzePython(code_text):
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
        purecode = code - docstr  # pure code = code - docstr
        return code, comment, docstr, purecode

    def forPython(self):
        self.filter = self.filterPython
        self.analyzer = self.analyzePython
        self.language = "Python"

    @staticmethod
    def filterText(winfile):
        return True

    @staticmethod
    def analyzeText(code_text):
        code, commend, docstr = 0, 0, 0
        code = code_text.count("\n") + 1
        comment = 0
        docstr = 0
        purecode = code - docstr  # pure code = code - docstr
        return code, comment, docstr, purecode

    def forText(self):
        self.filter = self.filterText
        self.analyzer = self.analyzeText
        self.language = "Text"


#--- Unittest ---
if __name__ == "__main__":
    import site

    workspace = os.path.join(site.getsitepackages()[1], "angora")

    analyzer = CodeStats(workspace)

    analyzer.forPython()
    analyzer.run()

    analyzer.forText()
    analyzer.run()
