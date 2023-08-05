#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
filesystem is a package you can use to manipulate with file system.
"""

from .filesystem import (
    WinFile, WinDir, FileCollection, FileFilter, string_SizeInBytes)
from .winzip import (
    zip_a_folder, zip_everything_in_a_folder, zip_many_files,
    write_gzip, read_gzip)