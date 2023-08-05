#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module description
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
configuration is a simple configuration language file read and write tools.

features:

1. UTF-8 encoding, support non-ASCII character! (new feature!)
2. smartly detect value type
3. Yes, No, True, False, None is case-insensitive.
    
what is Configuration Language? Here's an example::

    [DEFAULT]
    key1 = value1
    key2 = value2...
    
    [section name]
    key1 = integer_value # 整数
    key2 = real_value # 实数
    key3 = string_value # 普通字符串
    key4 = 'special_string' # or "special_string", 特殊字符串, 即不管内容是什么, 都解释为字符串
    key5 = list_of_integer_or_real_or_string_or_bool # 整数, 实数, 字符串或是布尔值的列表
    key6 = boolean_value # 布尔值, 可以自动解释 yes, no, true, false, none, 大小写不敏感
    key7 =  # 空字符串则会被解释为None
    ...
    '#' 符号以后的内容会被解释为注释

    
Compatibility
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- Python2: No (because this is designed to handle unicode stuff)
- Python3: Yes
    

Prerequisites
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- None


Class, method, function, exception
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from __future__ import print_function, unicode_literals
from collections import OrderedDict
import copy
import sys

if sys.version_info[0] == 3:
    _str_type = str
else:
    _str_type = basestring
    
class SectionNameError0(Exception):
    def __str__(self):
        return "Section name has to be string"
    
class SectionNameError1(Exception):
    def __str__(self):
        return "Section name can only have capital letter, _ and numbers."

class SectionNameError2(Exception):
    def __str__(self):
        return "Section name cannot start with numbers."
    
class Section(object):
    """Section class.
    """
    def __init__(self, section_name):
        if not isinstance(section_name, str):
            raise SectionNameError0
        
        for char in section_name:
            if char not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789":
                raise SectionNameError1
        if section_name[0].isdigit():
            raise SectionNameError2
        
        self.name = section_name
        self.data = OrderedDict()
        
    def __getitem__(self, key):
        return self.data[key]
    
    def __setitem__(self, key, value):
        self.data[key] = value

    def items(self):
        """Generator method
        """
        for key, value in self.data.items():
            yield key, value
    
    ########################################################################
    # _value_is_str() and _value_is_list() is for serving __str__() method #
    ########################################################################
    def _value_is_str(self, key, value):
        try:
            return "%s = '%s'" % (key, int(value))
        except:
            try:
                return "%s = '%s'" % (key, float(value))
            except:
                if value.lower() in ["true", "yes"]:
                    return "%s = 'True'" % key
                elif value.lower() in ["false", "no"]:
                    return "%s = 'False'" % key
                else:
                    return "%s = %s" % (key, value)

    def _value_is_list(self, key, value):
        if len(value) == 0: # empty list
            return "%s = ," % key
        else:
            if isinstance(value[0], _str_type): # 只要是字符串, 则在两边加'号
                return "%s = %s" % (key, ", ".join(["'%s'" % s for s in value]))
            else: # 否则直接调用__str__()
                return "%s = %s" % (key, ", ".join([str(i) for i in value]))
                
    def __str__(self):
        pairs_list = ["[%s]" % self.name]
        for key, value in self.data.items():
            if isinstance(value, list):
                pairs_list.append(self._value_is_list(key, value))
            else: # 是单个值
                if isinstance(value, str): # 是字符串
                    pairs_list.append(self._value_is_str(key, value))
                else:
                    pairs_list.append("%s = %s" % (key, value))

        return "\n".join(pairs_list)
    
    @staticmethod
    def from_text(text):
        def detect_bool_str(text):
            if text.lower() in ["true", "yes"]:
                return True
            elif text.lower() in ["false", "no"]:
                return False
            else:
                raise Exception("%s is not one of True, False, Yes, No (case-insensitive)" % text)
        
        ########################################################
        # step1, process lines which has the following pattern #
        #     "# some comment", drop it                        #
        #     "   # some comment", drop it                     #
        #     "     ", drop it                                 #
        #     " key = value    # some comment", delete comment #
        #     "[section_name]"                                 #
        ########################################################
        
        lines = list()
        for line in text.split("\n"):
            if not line.startswith("#"):
                if line.strip(): # 只要不是空格栏
                    if "#" in line:
                        line = line[:line.find("#")]
                        if line.strip(): # 只要去掉#之后还不是空栏
                            lines.append(line.strip())
                    else:
                        lines.append(line.strip())
    
        section_name = lines[0][1:-1] # section_name is the first valid line
        section = Section(section_name)
        
        ###############################################
        # step2, split key, value, and process value. #
        #     automatically detect datatype           #
        ###############################################
        
        for line in lines[1:]:
            key, value = line.split("=")
            key = key.strip()
            value = value.strip()
            
            # 从字符串中解析value, 跟 _value_is_str, _value_is_list 是相反的过程
            if "," in value: # 说明是list, 可能是 布尔值list, 整数list, 小数list, 字符串list
                values = [s.strip() for s in value.split(",") if s.strip()]
                try: # 尝试整数list
                    values = [int(s) for s in values]
                except:
                    try: # 尝试小数list
                        values = [float(s) for s in values]
                    except:
                        try: # 尝试布尔值list
                            values = [detect_bool_str(s) for s in values]
                        except: # 一定是字符串list
                            values = [s.replace("'", "").replace('"', '') for s in values]
                section[key] = values
                    
            else: # 说明是单个项目, 可能是 布尔值, 整数, 小数, 字符串
                if value.lower() in ["true", "yes"]:
                    section[key] = True
                elif value.lower() in ["false", "no"]:
                    section[key] = False
                else: # 整数, 小数, 字符串
                    try: # 整数
                        section[key] = int(value)
                    except:
                        try: # 小数
                            section[key] = float(value)
                        except: # 字符串
                            section[key] = value.replace("'", "").replace('"', '')
        
        return section
        
        
class Configuration(object):
    """Configuration class implements a basic configuration language.
    """
    def __init__(self):
        self._sections = OrderedDict()
        self._sections["DEFAULT"] = Section("DEFAULT")
    
    def __getattr__(self, attr):
        try:
            return self._sections[attr]
        except KeyError:
            raise Exception("Cannot find section name '%s'." % attr)
        
    def add_section(self, section_name):
        """Add an empty section.
        """
        if section_name == "DEFAULT":
            raise Exception("'DEFAULT' is reserved section name.")
        
        if section_name in self._sections:
            raise Exception("Error! %s is already one of the sections" % section_name)
        else:
            self._sections[section_name] = Section(section_name)
            
    def remove_section(self, section_name):
        """Remove a section, it cannot be the DEFAULT section.
        """
        if section_name == "DEFAULT":
            raise Exception("'DEFAULT' is reserved section name.")
        
        if section_name in self._sections:
            del self._sections[section_name]
        else:
            raise Exception("Error! cannot find section '%s'.")
    
    def set_section(self, section):
        """Set a section. If section already exists, overwrite the old one.
        """
        if not isinstance(section, Section):
            raise Exception("You")
        
        try:
            self.remove_section(section.name)
        except:
            pass
        
        self._sections[section.name] = copy.deepcopy(section)
        
    def sections(self):
        """Return a list of section name.
        """
        return list(self._sections.keys())
    
    def __str__(self):
        section_text_list = list()
        for section in self._sections.values():
            section_text_list.append(str(section))
        return "\n\n".join(section_text_list)
    
    def dump(self, path):
        """Save config to file.
        """
        with open(path, "wb") as f:
            f.write(str(self).encode("utf-8"))
    
    def load(self, path):
        """Read configuration from file.
        """
        with open(path, "rb") as f:
            content = f.read().decode("utf-8") 
        
        section_text_list = list()
        
        lines = list()
        for line in content.split("\n"):
            if line.startswith("["):
                section_text_list.append("\n".join(lines))
                lines = list()
                lines.append(line)
            else:
                lines.append(line)
        
        section_text_list.append("\n".join(lines))
        
        self._sections = OrderedDict()
        for text in section_text_list[1:]:
            section = Section.from_text(text)
            self._sections[section.name] = section


if __name__ == "__main__":
    import unittest
    class SectionUnittest(unittest.TestCase):
        def test_str(self):
            """测试__str__()方法是否能返回正确的字符串
            """
            section = Section("DEFAULT")
            section["key1"] = 100 # key1 = 100
            section["key2"] = 123.456 # key2 = 123.456
            section["key3"] = "True" # key3 = 'True'
            section["key4"] = "123" # key4 ='123'
            section["key5"] = r"C:\test\nope\red\中文\英文.jpg" # key5 = C:\test\nope\red\中文\英文.jpg
            section["key6"] = False # key6 = False
            section["key7"] = [1, -2, 3] # key7 = 1, -2, 3
            section["key8"] = [1.1, -2.2, 3.3] # key8 = 1.1, -2.2, 3.3
            section["key9"] = ["1", "1.1", "True", "helloworld"] # key9 = '1', '1.1', 'True', 'helloworld'
            section["key10"] = ["C:\windows", r"C:\中文"] # key10 = 'C:\windows', 'C:\中文'
            section["key11"] = [True, False, True, False] # key11 = True, False, True, False
            section["key12"] = [] # key12 = ,
            right_result = "\n".join([
                "[DEFAULT]",
                "key1 = 100",
                "key2 = 123.456",
                "key3 = 'True'",
                "key4 = '123'",
                r"key5 = C:\test\nope\red\中文\英文.jpg",
                "key6 = False",
                "key7 = 1, -2, 3",
                "key8 = 1.1, -2.2, 3.3",
                "key9 = '1', '1.1', 'True', 'helloworld'",
                r"key10 = 'C:\windows', 'C:\中文'",
                "key11 = True, False, True, False",
                "key12 = ,",
                ])
            
            self.assertEqual(str(section), right_result)
        
        def test_from_text(self):
            """测试from_text()方法能否将字符串解析成section
            """
            text = r"""
            [DEFAULT]
            localhost = 192.168.0.1 # IP地址, 默认 192.168.0.1
            port = 8080 # 端口号
            ### 下面的是尝试连接的最长时间
             
            connection_timeout = 60 # 单位是秒, 默认60
            
            # Test是用来测试各种数据类型是否能被成功解析的
            # 用Configuration.load()看看会不会成功吧
             
            """.strip()
            section = Section.from_text(text)
            self.assertEqual(section["localhost"], "192.168.0.1")
            self.assertEqual(section["port"], 8080)
            self.assertEqual(section["connection_timeout"], 60)

            text = r"""
            [TEST]
            key1 = 100
            key2 = 123.456
            key3 = 'True'
            key4 = '123'
            key5 = C:\test\nope\red\中文\英文.jpg
            key6 = False
            key7 = 1, -2, 3
            key8 = 1.1, -2.2, 3.3
            key9 = '1', '1.1', 'True', 'helloworld'
            key10 = 'C:\windows', 'C:\中文'
            key11 = True, False, True, False
            key12 = ,
            """.strip()
            section = Section.from_text(text)
            self.assertEqual(section["key1"], 100)
            self.assertEqual(section["key2"], 123.456)
            self.assertEqual(section["key3"], "True")
            self.assertEqual(section["key4"], "123")
            self.assertEqual(section["key5"], r"C:\test\nope\red\中文\英文.jpg")
            self.assertEqual(section["key6"], False)
            self.assertListEqual(section["key7"], [1, -2, 3])
            self.assertListEqual(section["key8"], [1.1, -2.2, 3.3])
            self.assertListEqual(section["key9"], ["1", "1.1", "True", "helloworld"])
            self.assertListEqual(section["key10"], ["C:\windows", r"C:\中文"])
            self.assertListEqual(section["key11"], [True, False, True, False])
            self.assertListEqual(section["key12"], [])

    class ConfigurationUnittest(unittest.TestCase):
        def setUp(self):
            """从config dump到本地文件, 以供检视
            """
            config = Configuration()
            config.DEFAULT["localhost"] = "192.168.0.1"
            config.DEFAULT["port"] = 8080
            config.DEFAULT["connection_timeout"] = 60 # seconds
            
            config.add_section("TEST")
            config.TEST["key1"] = 100 # key1 = 100
            config.TEST["key2"] = 123.456 # key2 = 123.456
            config.TEST["key3"] = "True" # key3 = 'True'
            config.TEST["key4"] = "123" # key4 ='123'
            config.TEST["key5"] = r"C:\test\nope\red\中文\英文.jpg" # key5 = C:\test\nope\red\中文\英文.jpg
            config.TEST["key6"] = False # key6 = False
            config.TEST["key7"] = [1, -2, 3] # key7 = 1, -2, 3
            config.TEST["key8"] = [1.1, -2.2, 3.3] # key8 = 1.1, -2.2, 3.3
            config.TEST["key9"] = ["1", "1.1", "True", "helloworld"] # key9 = '1', '1.1', 'True', 'helloworld'
            config.TEST["key10"] = ["C:\windows", r"C:\中文"] # key10 = 'C:\windows', 'C:\中文'
            config.TEST["key11"] = [True, False, True, False] # key11 = True, False, True, False
            config.TEST["key12"] = [] # key12 = ,
            
            config.dump("config.txt") # <=== Uncomment this to view the file
            
        def test_load(self):
            """测试Configuration.load()方法
            """
            config = Configuration()
            config.load(r"testdata\config.txt") # read test data
            
            self.assertListEqual(config.sections(), ["DEFAULT", "TEST"])
            self.assertEqual(config.DEFAULT["localhost"], "192.168.0.1")
            self.assertEqual(config.DEFAULT["port"], 8080)
            self.assertEqual(config.DEFAULT["connection_timeout"], 60)

            self.assertEqual(config.TEST["key1"], 100)
            self.assertEqual(config.TEST["key2"], 123.456)
            self.assertEqual(config.TEST["key3"], "True")
            self.assertEqual(config.TEST["key4"], "123")
            self.assertEqual(config.TEST["key5"], r"C:\test\nope\red\中文\英文.jpg")
            self.assertEqual(config.TEST["key6"], False)
            self.assertListEqual(config.TEST["key7"], [1, -2, 3])
            self.assertListEqual(config.TEST["key8"], [1.1, -2.2, 3.3])
            self.assertListEqual(config.TEST["key9"], ["1", "1.1", "True", "helloworld"])
            self.assertListEqual(config.TEST["key10"], ["C:\windows", r"C:\中文"])
            self.assertListEqual(config.TEST["key11"], [True, False, True, False])
            self.assertListEqual(config.TEST["key12"], [])

    unittest.main()