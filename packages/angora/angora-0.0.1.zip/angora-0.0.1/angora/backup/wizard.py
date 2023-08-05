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

A file backup tool. Inspired by github, .gitignore file.

Usage example::
    
    # back up files in root_dir
    root_dir = "C:\Python33\Lib\site-packages"

    # ignore files and folder
    ignore = ["requests"] # ignore C:\Python33\Lib\site-packages\requests
    
    # ignore files with extension name .xxx
    ignore_ext = [".pyc"]
    
    # ignore file or folder with pattern
    ignore_pattern = ["__init__"]
    
    # name the backup file name
    # the backup file name would be "site-packages <timestamp>.zip"
    backup_filename = "site-packages"
    
    # run backup
    wizard = BackupWizard(root_dir, ignore, ignore_ext, ignore_pattern)
    wizard.backup(backup_filename) # run backup


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
try:
    from ..filesystem import *
except:
    from angora.filesystem import *
from datetime import datetime
from zipfile import ZipFile
import os

_tab = "    "

class BackupWizard(object):
    """The backup utility class.
    
    :param root_dir: the directory you want to backup
    :param ignore: file or directory defined in this list will be ignored.
    :param ignore_ext: file with extensions defined in this list will be ignored.
    :param ignore_pattern: any file or directory that contains this pattern
      will be ignored.
    """
    def __init__(self, root_dir, ignore=[], ignore_ext=[], ignore_pattern=[]):
        self.root_dir = os.path.abspath(root_dir)
        self.ignore = ignore
        self.ignore_ext = ignore_ext
        self.ignore_pattern = ignore_pattern
        
    def backup(self, filename):
        """Run backup.
        
        :param filename: the backup file name without file extension. A file 
          ``<filename> <timestamp>.zip`` will be created.
        """
        print("Backup %s..." % self.root_dir)
        print(_tab + "1. Calculate files...")
        
        total_size_in_bytes = 0
        
        ignore = [os.path.join(self.root_dir, i) for i in self.ignore]
        
        file_list = list()
        for winfile in FileCollection.from_path(self.root_dir).iterfiles():
            flag = True
            
            # exclude ignore file
            relpath = os.path.relpath(winfile.abspath, self.root_dir)
            for path in self.ignore:
                if relpath.startswith(path):
                    flag = False
                    break
                
            # exclude ignore extension
            if winfile.ext in self.ignore_ext:
                flag = False

            # exclude ignore pattern
            for pattern in self.ignore_pattern:
                if pattern in winfile.abspath:
                    flag = False
                    break

            if flag:
                file_list.append(winfile)
                total_size_in_bytes += winfile.size_on_disk
                
        filename = "%s %s.zip" % (
            filename, datetime.now().strftime("%Y-%m-%d %Hh-%Mm-%Ss"))
        
        print(_tab * 2 + "Done, got %s files, total size is %s." % (
            len(file_list), string_SizeInBytes(total_size_in_bytes)))
        
        
        print(_tab + "2. Backup files...")
        current_dir = os.getcwd()
        
        with ZipFile(filename, "w") as f:
            os.chdir(self.root_dir)
            for winfile in file_list:
                relpath = os.path.relpath(winfile.abspath, self.root_dir)
                f.write(relpath)
                
        os.chdir(current_dir)
        print(_tab * 2 + "Complete!")

#-----------------------------------------------------------------------------#
#                                  Unittest                                   #
#-----------------------------------------------------------------------------#

if __name__ == "__main__":
    import unittest
    import site
    
    class Unittest(unittest.TestCase):
        def test_backup(self):
            root_dir = os.path.join(site.getsitepackages()[1], "angora")
            ignore = ["zzz_manual_install.py"]
            ignore_ext = [".pyc"]
            ignore_pattern = ["__init__"]
            backup_filename = "angora-backup"
            wizard = BackupWizard(root_dir, ignore, ignore_ext, ignore_pattern)
            wizard.backup(backup_filename)
            
    unittest.main()