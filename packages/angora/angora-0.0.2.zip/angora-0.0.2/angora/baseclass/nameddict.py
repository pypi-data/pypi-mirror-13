#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
**中文文档**

和 ``collections.namedtuple`` 类似, ``nameddict`` 是一种数据容器类。提供了方便的方法
对属性, 值的遍历, 以及与dict之间的交互。
"""


class Base(object):
    """nameddict base class.
    
    if you really care about performance, use collections.namedtuple.
    """

    def __init__(self, **kwargs):
        for attr, value in kwargs.items():
            object.__setattr__(self, attr, value)

    def __repr__(self):
        kwargs = list()
        for attr, value in self.items():
            kwargs.append("%s=%r" % (attr, value))
        return "%s(%s)" % (self.__class__.__name__, ", ".join(kwargs))

    @classmethod
    def _make(cls, d):
        return cls(**d)

    def keys(self):
        return [key for key, value in self.items()]

    def values(self):
        return [value for key, value in self.items()]

    def items(self):
        return sorted(self.__dict__.items(), key=lambda x: x[0])

    def to_dict(self):
        return self.__dict__


if __name__ == "__main__":
    import unittest


    class Person(Base):
        def __init__(self, id, name):
            self.id = id
            self.name = name


    class Unittest(unittest.TestCase):
        def test_all(self):
            person = Person(id=1, name="Jack")
            self.assertEqual(str(person), "Person(id=1, name='Jack')")
            self.assertDictEqual(person.to_dict(), {"id": 1, "name": "Jack"})

            person = Person._make({"id": 1, "name": "Jack"})
            self.assertEqual(str(person), "Person(id=1, name='Jack')")
            self.assertDictEqual(person.to_dict(), {"id": 1, "name": "Jack"})
            
            print(person.keys())
            print(person.values())

    unittest.main()