#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Usage example::

    >>> from angora.baseclass.classtree import gencode
    >>> gencode(data, "example.py")

"""

from __future__ import print_function
import datetime
import sys
import os

try:
    from . import  nameddict
except SystemError:
    from angora.baseclass import nameddict

if sys.version_info[0] == 3:
    _str_type = str
    _int_type = (int,)
else:
    _str_type = basestring
    _int_type = (int, long)

class Base(nameddict.Base):
    """
    """
    def _getattr_by_key_value(self, key):
        def getattr_by_key_value(value):
            return getattr(self, "%s____%s" % (key, value))
        return getattr_by_key_value

    def __getattr__(self, attr):
        if attr.startswith("getattr_by_"):
            key = attr.replace("getattr_by_", "")
            return self._getattr_by_key_value(key)                
        else:
            return object.__getattribute__(self, attr)

    def keys(self):
        return [key for key, value in self.items()]

    def values(self):
        return [value for key, value in self.items()]

    def items(self):
        items = list()
        for attr, value in self.__dict__.items():
            if "____" not in attr:
                items.append((attr, value))
        return sorted(items, key=lambda x: x[0])

    def to_dict(self):
        return self.__dict__

    def serialize(self):
        d = {"classname": self.__class__.__name__, "metadata": dict()}
        uuid_set = set()
        for attr, value in self.items():
            if "____" not in attr:
                d["metadata"][attr] = value
            else:
                _id = id(value)
                if _id not in uuid_set:                    
                    try:
                        d["subclass"].append(value.serialize())
                    except:
                        d["subclass"] = [value.serialize(),]
                    uuid_set.add(_id)
        return d
                
class CodeGenerator(object):
    """Worker class
    """
    def __init__(self, tab="    ", indent=0):
        self.Tab = tab
        self.Tab2 = tab * 2
        self.indent = indent
        self.basename = "classtree.Base"
        self._classes = dict()
        self.classes = set()
        self.lines = [
            "#!/usr/bin/env python",
            "# -*- coding: utf-8 -*-",
            "",
            "import datetime", 
            "from angora.baseclass import classtree",
        ]
        
    def reset(self):
        self._classes = dict()
        self.classes = set()
        self.lines = [
            "#!/usr/bin/env python",
            "# -*- coding: utf-8 -*-",
            "", 
            "import datetime",
            "from angora.baseclass import classtree",
        ]
    
    def pre_process(self, class_data):
        classname = self.formatted_classname(class_data["classname"])
        self._classes[classname] = set()
        for key in class_data.get("metadata", dict()):
            self._classes[classname].add(key)
        for subclass_data in class_data.get("subclass", list()):
            self.pre_process(subclass_data)
    
    def sort_metadata(self):
        for k, v in self._classes.items():
            self._classes[k] = list(v)
            self._classes[k].sort()
            
    @property
    def code(self):
        return "\n".join([self.Tab * self.indent + line for line in self.lines])
    
    def formatted_classname(self, text):
        return text[0].upper() + text[1:]
    
    def formatted_instancename(self, text):
        return text[0].lower() + text[1:]
    
    def sorted_dict(self, d):
        return sorted(d.items(), key=lambda x: x[0], reverse=False)
    
    def repr_def_class(self, class_data):
        """Create code like this::
        
            class Person(Base):
                def __init__(self, person_id=None, name=None):
                    self.person_id = person_id
                    self.name = name
        """
        classname = self.formatted_classname(class_data["classname"])
        if classname not in self.classes:
            self.lines.append("")
            self.lines.append("class %s(%s):" % (classname, self.basename))
            
            kwargs = list()
            setattr_arguments = list()
            for attr in self._classes[classname]:
                kwargs.append("%s=None" % attr)
                setattr_arguments.append(
                    self.Tab2 + "self.%s = %s" % (attr, attr))
            if len(kwargs):
                line = self.Tab + "def __init__(self, %s):" % ", ".join(kwargs)
            else:
                line = self.Tab + "def __init__(self):"
            self.lines.append(line)
            for setattr_argument in setattr_arguments:
                self.lines.append(setattr_argument)
            if len(setattr_arguments):
                self.lines.append("")
            self.classes.add(classname)
    
    def repr_new_instance(self, class_data):
        """Create code like this::
        
            person = Person(name='Jack', person_id=1)
        """
        classname = self.formatted_classname(class_data["classname"])
        instancename = self.formatted_instancename(class_data["classname"])
        arguments = list()
        for key, value in self.sorted_dict(class_data.get("metadata", dict())):
            arguments.append("%s=%r" % (key, value))
        return "%s = %s(%s)" % (
            instancename, classname, ", ".join(arguments))
    
    def repr_setattr(self, class_data):
        """Create code like this::
        
                person = Person(name='Jack', person_id=1)
                self.name____Jack = person
                self.person_id____1 = person
                
                person = Person(name='Paul', person_id=2)
                self.name____Paul = person
                self.person_id____2 = person
        """
        def get_indexable_attributes(class_data):
            def isvalid(text):
                for char in r"""~`!#%^&*()+=[]{}|\:;"'/.,<> """:
                    if char in text:
                        return False
                return True
            
            indexable_attributes = list()
            for key, value in class_data.get("metadata", dict()).items():
                if isinstance(value, _int_type):
                    indexable_attributes.append(key)
                elif isinstance(value, _str_type):
                    if isvalid(value):
                         indexable_attributes.append(key)
                        
            return indexable_attributes
        
        if "subclass" in class_data:
            for subclass_data in class_data["subclass"]:
                instancename = self.formatted_instancename(subclass_data["classname"])
                self.lines.append(self.Tab2 + self.repr_new_instance(subclass_data))
                indexable_attributes = get_indexable_attributes(subclass_data)
                for key, value in self.sorted_dict(subclass_data.get("metadata", dict())):
                    if key in indexable_attributes:
                        if isinstance(value, _int_type):
                            if value < 0:
                                self.lines.append(self.Tab2 + "self.%s____neg%s = %s" % (
                                    key, -value, instancename))
                            else:
                                self.lines.append(self.Tab2 + "self.%s____%s = %s" % (
                                    key, value, instancename))
                        else:
                            self.lines.append(self.Tab2 + "self.%s____%s = %s" % (
                                key, value, instancename))
                self.lines.append(self.Tab2)
                
    def repr_class_data(self, class_data):
        """Create code like this::
        
            class Person(classtree.Base):
                def __init__(self, name=None, person_id=None):
                    self.name = name
                    self.person_id = person_id
            
            
            class PersonCollection(classtree.Base):
                def __init__(self, collection_id=None, create_date=None, name=None):
                    self.collection_id = collection_id
                    self.create_date = create_date
                    self.name = name
            
                    person = Person(name='Jack', person_id=1)
                    self.name____Jack = person
                    self.person_id____1 = person
                    
                    person = Person(name='Paul', person_id=2)
                    self.name____Paul = person
                    self.person_id____2 = person
        """
        if "subclass" in class_data:
            for subclass_data in class_data["subclass"]:
                self.repr_class_data(subclass_data)
        self.repr_def_class(class_data)
        self.repr_setattr(class_data)
                
        
def gencode(data, output=None, tab="    ", indent=0, overwrite=False):
    """Generate code.
    
    :param data: must be list of class data, see a valid data example below
    :param output: default None, the python script file name you want to create
    :param tab: default "    "
    :param indent: global indent setting
    :param overwrite: if True, silently overwrite the output file    
    
    ::
    
        data = [
            {
                "classname": "Database",
                "metadata": {"db_id": 1, "name": "Database"},
                "subclass": [
                    {
                        "classname": "PersonCollection",
                        "metadata": {"collection_id": 1, "name": "Person", "create_date": datetime.date(2016, 1, 8)},
                        "subclass": [
                            {
                                "classname": "Person", 
                                "metadata": {"person_id": 1, "name": "Jack"},
                            },
                            {
                                "classname": "Person", 
                                "metadata": {"person_id": 2, "name": "Paul"},
                            },
                        ],
                    },
                    {
                        "classname": "DepartmentCollection",
                        "metadata": {"collection_id": 2, "name": "Department", "create_date": datetime.date(2016, 1, 1)},
                        "subclass": [
                            {
                                "classname": "Department", 
                                "metadata": {"department_id": 1, "name": "IT"},
                            },
                            {    
                                "classname": "Department", 
                                "metadata": {"department_id": 2, "name": "HR"},
                            },
                        ]
                    },
                ],
            },   
        ]
    """
    codegen = CodeGenerator(tab=tab, indent=indent)
    
    if isinstance(data, list):
        for class_data in data:
            codegen.pre_process(class_data)
            codegen.sort_metadata()
            codegen.repr_class_data(class_data)
            
        for class_data in data:            
            codegen.lines.append("")
            codegen.lines.append("%s" % codegen.repr_new_instance(class_data))
    elif isinstance(data, dict):
        codegen.pre_process(data)
        codegen.repr_class_data(data)
        codegen.lines.append("")
        codegen.lines.append("%s" % codegen.repr_new_instance(data))

    if output:
        if not overwrite:
            if os.path.exists(output):
                raise FileExistsError("%r" % output)
        with open(output, "wb") as f:
            f.write(codegen.code.encode("utf-8"))
    else:
        print(codegen.code)
        
if __name__ == "__main__":
    import unittest
    from pprint import pprint as ppt
    
    data = [
        {
            "classname": "Database",
            "metadata": {"db_id": 1, "name": "Database"},
            "subclass": [
                {
                    "classname": "PersonCollection",
                    "metadata": {"collection_id": 1, "name": "Person", "create_date": datetime.date(2016, 1, 8)},
                    "subclass": [
                        {
                            "classname": "Person", 
                            "metadata": {"person_id": 1, "name": "Jack"},
                        },
                        {
                            "classname": "Person", 
                            "metadata": {"person_id": 2, "name": "Paul"},
                        },
                    ],
                },
                {
                    "classname": "DepartmentCollection",
                    "metadata": {"collection_id": 2, "name": "Department", "create_date": datetime.date(2016, 1, 1)},
                    "subclass": [
                        {
                            "classname": "Department", 
                            "metadata": {"department_id": 1, "name": "IT"},
                        },
                        {    
                            "classname": "Department", 
                            "metadata": {"department_id": 2, "name": "HR"},
                        },
                    ]
                },
            ],
        },   
    ]
    
    gencode(data[0]["subclass"][0], indent=0, overwrite=True)
    
    class Unittest(unittest.TestCase):
        def test_all(self):
            #!/usr/bin/env python
            # -*- coding: utf-8 -*-
            
            import datetime
            from angora.baseclass import classtree
            
            class Person(classtree.Base):
                def __init__(self, name=None, person_id=None):
                    self.name = name
                    self.person_id = person_id
            
            
            class PersonCollection(classtree.Base):
                def __init__(self, collection_id=None, create_date=None, name=None):
                    self.collection_id = collection_id
                    self.create_date = create_date
                    self.name = name
            
                    person = Person(name='Jack', person_id=1)
                    self.name____Jack = person
                    self.person_id____1 = person
                    
                    person = Person(name='Paul', person_id=2)
                    self.name____Paul = person
                    self.person_id____2 = person
                    
            
            class Department(classtree.Base):
                def __init__(self, department_id=None, name=None):
                    self.department_id = department_id
                    self.name = name
            
            
            class DepartmentCollection(classtree.Base):
                def __init__(self, collection_id=None, create_date=None, name=None):
                    self.collection_id = collection_id
                    self.create_date = create_date
                    self.name = name
            
                    department = Department(department_id=1, name='IT')
                    self.department_id____1 = department
                    self.name____IT = department
                    
                    department = Department(department_id=2, name='HR')
                    self.department_id____2 = department
                    self.name____HR = department
                    
            
            class Database(classtree.Base):
                def __init__(self, db_id=None, name=None):
                    self.db_id = db_id
                    self.name = name
            
                    personCollection = PersonCollection(collection_id=1, create_date=datetime.date(2016, 1, 8), name='Person')
                    self.collection_id____1 = personCollection
                    self.name____Person = personCollection
                    
                    departmentCollection = DepartmentCollection(collection_id=2, create_date=datetime.date(2016, 1, 1), name='Department')
                    self.collection_id____2 = departmentCollection
                    self.name____Department = departmentCollection
                    
            
            database = Database(db_id=1, name='Database')
            
#             ppt(database.serialize())
            
            # Test IDLE auto-complete support
#             self.assertEqual(database.collection_id____1.collection_id, 1)
#             self.assertEqual(database.collection_id____2.collection_id, 2)
#             self.assertEqual(database.name____Person.name, "Person")
#             self.assertEqual(database.name____Department.name, "Department")
#              
#             self.assertEqual(database.collection_id____1.person_id____1.person_id, 1)
#             self.assertEqual(database.collection_id____1.person_id____2.person_id, 2)
#             self.assertEqual(database.collection_id____1.name____Jack.name, "Jack")
#             self.assertEqual(database.collection_id____1.name____Paul.name, "Paul")
#             
#             # Test getattr_by method
#             self.assertEqual(database.getattr_by_collection_id(1).collection_id, 1)
#             self.assertEqual(database.getattr_by_name("Person").name, "Person")
            
    unittest.main()