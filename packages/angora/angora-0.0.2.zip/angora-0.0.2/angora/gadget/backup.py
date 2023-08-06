#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""    
Copyright (c) 2016 by Sanhe Hu
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Author: Sanhe Hu
- Email: husanhe@gmail.com
- Lisence: MIT


Module description
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A file backup tool. Inspired by github, .gitignore file.

Usage example, backup installed site-packages:

.. code-block:: python
    
    >>> # back up files in root_dir
    >>> root_dir = "C:\Python33\Lib\site-packages"
    
    >>> # ignore files and folder
    >>> ignore = ["requests"] # ignore requests
    
    >>> # ignore files with extension name .xxx
    >>> ignore_ext = [".pyc"]
    
    >>> # ignore file or folder with pattern
    >>> ignore_pattern = ["__init__"] # ignore __init__.py file
    
    >>> # name the backup file name
    >>> # the backup file name would be "site-packages <timestamp>.zip"
    >>> backup_filename = "site-packages"
    
    >>> # run backup
    >>> run_backup(backup_filename, root_dir, ignore, ignore_ext, ignore_pattern)
    Perform backup 'C:\Python33\lib\site-packages'...
      1. Calculate files...
        Done, got XX files, total size is xxx.xx MB.
      2. Backup files...
        Write to 'site-packages 2016-01-23 15h-40m-43s.zip'...
      Complete!


Compatibility
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- Python2: Yes for non-ascii char in file system, but recommend using in 
    python3 only
- Python3: Yes


Prerequisites
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- None


Class, method, function, exception
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from __future__ import print_function

import os
from datetime import datetime
from zipfile import ZipFile

try:
    from ..filesystem import *
except:
    from angora.filesystem import *


def run_backup(filename, root_dir, ignore=[], ignore_ext=[], ignore_pattern=[]):
    """The backup utility method.

    :param root_dir: the directory you want to backup
    :param ignore: file or directory defined in this list will be ignored.
    :param ignore_ext: file with extensions defined in this list will be ignored.
    :param ignore_pattern: any file or directory that contains this pattern
      will be ignored.
    """
    tab = "  "
    # Step 1, calculate files to backup
    print("Perform backup '%s'..." % root_dir)
    print(tab + "1. Calculate files...")

    total_size_in_bytes = 0

    init_mode = WinFile.init_mode
    WinFile.use_regular_init()
    fc = FileCollection.from_path_except(
        root_dir, ignore, ignore_ext, ignore_pattern)
    WinFile.set_initialize_mode(complexity=init_mode)

    for winfile in fc.iterfiles():
        total_size_in_bytes += winfile.size_on_disk

    # Step 2, write files to zip archive
    print(tab * 2 + "Done, got %s files, total size is %s." % (
        len(fc), string_SizeInBytes(total_size_in_bytes)))
    print(tab + "2. Backup files...")

    filename = "%s %s.zip" % (
        filename, datetime.now().strftime("%Y-%m-%d %Hh-%Mm-%Ss"))

    print(tab * 2 + "Write to '%s'..." % filename)
    current_dir = os.getcwd()
    with ZipFile(filename, "w") as f:
        os.chdir(root_dir)
        for winfile in fc.iterfiles():
            relpath = os.path.relpath(winfile.abspath, root_dir)
            f.write(relpath)
    os.chdir(current_dir)

    print(tab + "Complete!")


#--- Unittest ---
if __name__ == "__main__":
    import site

    def test():
        root_dir = os.path.join(site.getsitepackages()[1], "angora")
        ignore = ["zzz_manual_install.py"]
        ignore_ext = [".pyc"]
        ignore_pattern = ["__init__"]
        backup_filename = "angora-backup"
        run_backup(
            backup_filename, root_dir, ignore, ignore_ext, ignore_pattern)

    test()
