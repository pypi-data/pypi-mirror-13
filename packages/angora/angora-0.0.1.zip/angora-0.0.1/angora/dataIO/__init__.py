#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This package includes some utility function of dataIO. Supported data format:

- json
- pickle
- textfile
"""

from .js import load_js, dump_js, safe_dump_js, prt_js, js2str
from .pk import (load_pk, dump_pk, safe_dump_pk, 
                 obj2bytestr, bytestr2obj, obj2str, str2obj)
from . import textfile