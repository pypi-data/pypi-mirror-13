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

This is a programmatic windows explorer behaviors implementation. A lots of 
useful recipe help you easily control file, directory, file name, select,
rename, etc...


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
from collections import OrderedDict
import hashlib
import copy
import os

def string_SizeInBytes(size_in_bytes):
    """Make ``size in bytes`` human readable. 
    Doesn"t support size greater than 1000PB.
    
    Usage::
        
        >>> from __future__ import print_function
        >>> from angora.filesystem.filesystem import string_SizeInBytes
        >>> print(string_SizeInBytes(100))
        100 B
        >>> print(string_SizeInBytes(100*1000))
        97.66 KB
        >>> print(string_SizeInBytes(100*1000**2))
        95.37 MB
        >>> print(string_SizeInBytes(100*1000**3))
        93.13 GB
        >>> print(string_SizeInBytes(100*1000**4))
        90.95 TB
        >>> print(string_SizeInBytes(100*1000**5))
        88.82 PB
    """
    res, by = divmod(size_in_bytes,1024)
    res, kb = divmod(res,1024)
    res, mb = divmod(res,1024)
    res, gb = divmod(res,1024)
    pb, tb = divmod(res,1024)
    if pb != 0:
        human_readable_size = "%.2f PB" % (pb + tb/float(1024) )
    elif tb != 0:
        human_readable_size = "%.2f TB" % (tb + gb/float(1024) )
    elif gb != 0:
        human_readable_size = "%.2f GB" % (gb + mb/float(1024) )
    elif mb != 0:
        human_readable_size = "%.2f MB" % (mb + kb/float(1024) )
    elif kb != 0:
        human_readable_size = "%.2f KB" % (kb + by/float(1024) )
    else:
        human_readable_size = "%s B" % by
    return human_readable_size

def md5file(abspath, nbytes=0):
    """Return md5 hash value of a piece of a file
    
    Estimate processing time on:
    
    :param abspath: the absolute path to the file
    :param nbytes: only has first N bytes of the file. if 0, hash all file
    
    CPU = i7-4600U 2.10GHz - 2.70GHz, RAM = 8.00 GB
    1 second can process 0.25GB data
    
    - 0.59G - 2.43 sec
    - 1.3G - 5.68 sec
    - 1.9G - 7.72 sec
    - 2.5G - 10.32 sec
    - 3.9G - 16.0 sec
    
    ATTENTION:
        if you change the meta data (for example, the title, years 
        information in audio, video) of a multi-media file, then the hash 
        value gonna also change.
    """    
    m = hashlib.md5()
    with open(abspath, "rb") as f:
        if nbytes:
            data = f.read(nbytes)
            if data:
                m.update(data)
        else:
            while True:
                data = f.read(1 << 20)
                if not data:
                    break
                m.update(data)
    return m.hexdigest()


class WinFile(object):
    """Windows file class.
    
    attributes includes:
    
    - self.abspath        absolute path (绝对路径)
    - self.dirname        parents directory name (父目录路径)
    - self.basename       complete file name (文件全名)
    - self.fname          the first part of file name (纯文件名)
    - self.ext            file extension (文件扩展名)
    - self.atime          last access time (文件最后一次被触碰的时间)
    - self.ctime          create time (文件被创建的时间)
    - self.mtime          last modify time (文件最后一次被修改的时间)
    - self.size_on_disk   file size in bytes (文件在硬盘上的大小, 单位bytes)

    Appendix, The difference of (atime, ctime, mtime):
    
    - access time (os.path.getatime)
    - create time (os.path.getctime)
    - modify time (os.path.getmtime)

    - When rename, cut-and-paste, all 3 time stays.
    - When edit the content, atime and mtime change, ctime stays.
    - When copy the file to a new place, atime and ctime change, mtime stays.
    
    **中文文档**
    
    Windows文件对象, 可以通过 .属性名的方式访问 绝对路径, 文件夹路径, 
    文件名, 扩展名, 大小。免去了使用 ``os.path.split`` 等方法的麻烦。
    
    附录, atime, ctime, mtime的区别
    
    - 当文件被改名, 和剪切(剪切跟改名是一个操作), 所有3个时间都不变
    - 当文件内容被修改, atime, mtime变化, ctime不变
    - 当文件被复制到新地方时, atime, ctime变化, mtime不变
    """
    __slots__ = [
        "abspath", "dirname", "basename", "fname", "ext",
        "atime", "ctime", "mtime", "size_on_disk", "md5",        
    ]
    init_mode = 2
    def __init__(self, abspath):
        if os.path.isfile(abspath): # 确保这是一个文件而不是目录
            self.abspath = os.path.abspath(abspath)
            self.initialize()
        else:
            raise FileNotFoundError(
                "%s is not a file or it doesn't exist." % abspath)

    def initialize(self):
        """Internal method. Initialize the value of some attributes.
        """
        self.level2_initialize()
        
    @staticmethod
    def use_fast_init():
        """Set initialization mode to level1_initialize
        """
        WinFile.initialize = WinFile.level1_initialize
        WinFile.init_mode = 1
        
    @staticmethod
    def use_regular_init():
        """Set initialization mode to level2_initialize
        """
        WinFile.initialize = WinFile.level2_initialize
        WinFile.init_mode = 2
        
    @staticmethod
    def use_slow_init():
        """Set initialization mode to level3_initialize
        """
        WinFile.initialize = WinFile.level3_initialize
        WinFile.init_mode = 3
        
    @staticmethod
    def set_initialize_mode(complexity=2):
        """Set initialization mode. Default is slow mode.
        
        **中文文档**
        
        设置WinFile类的全局变量, 指定WinFile.initialize方法所绑定的初始化方式。
        """
        if complexity == 3:
            WinFile.initialize = WinFile.level3_initialize
            WinFile.init_mode = 3
        elif complexity == 2:
            WinFile.initialize = WinFile.level2_initialize
            WinFile.init_mode = 2
        elif complexity == 1:
            WinFile.initialize = WinFile.level1_initialize
            WinFile.init_mode = 1
        else:
            raise ValueError("complexity has to be 3, 2 or 1.")
        
    def level3_initialize(self):
        """Load abspath, dirname, basename, fname, ext, atime, ctime, mtime,
        size_on_disk attributes in initialization.
        
        **中文文档**
        
        比较全面但稍慢的WinFile对象初始化方法, 从绝对路径中取得:
        
        - 绝对路径
        - 父目录路径
        - 文件全名
        - 纯文件名
        - 文件扩展名
        - access time
        - create time
        - modify time
        - 文件占据磁盘大小
        - 文件的哈希值
        """
        self.dirname, self.basename = os.path.split(self.abspath) # 目录名, 文件名
        self.fname, self.ext = os.path.splitext(self.basename) # 纯文件名, 文件扩展名
        self.ext = self.ext.lower()
        
        self.size_on_disk = os.path.getsize(self.abspath)
        self.atime = os.path.getatime(self.abspath) # 接触时间
        self.ctime = os.path.getctime(self.abspath) # 创建时间, 当文件被修改后不变
        self.mtime = os.path.getmtime(self.abspath) # 修改时间
        self.md5 = md5file(self.abspath, nbytes=1 << 20) # 文件的哈希值
        
    def level2_initialize(self):
        """Load abspath, dirname, basename, fname, ext, atime, ctime, mtime,
        size_on_disk attributes in initialization.
        
        **中文文档**
        
        比较全面但稍慢的WinFile对象初始化方法, 从绝对路径中取得:
        
        - 绝对路径
        - 父目录路径
        - 文件全名
        - 纯文件名
        - 文件扩展名
        - access time
        - create time
        - modify time
        - 文件占据磁盘大小
        """
        self.dirname, self.basename = os.path.split(self.abspath) # 目录名, 文件名
        self.fname, self.ext = os.path.splitext(self.basename) # 纯文件名, 文件扩展名
        self.ext = self.ext.lower()
        
        self.size_on_disk = os.path.getsize(self.abspath)
        self.atime = os.path.getatime(self.abspath) # 接触时间
        self.ctime = os.path.getctime(self.abspath) # 创建时间, 当文件被修改后不变
        self.mtime = os.path.getmtime(self.abspath) # 修改时间

    def level1_initialize(self):
        """Load abspath, dirname, basename, fname, ext 
        attributes in initialization.
        
        **中文文档**
        
        快速的WinFile对象初始化方法, 只从绝对路径中取得:

        - 绝对路径
        - 目录路径
        - 文件全名
        - 纯文件名
        - 文件扩展名
        """
        self.dirname, self.basename = os.path.split(self.abspath)
        self.fname, self.ext = os.path.splitext(self.basename)
        self.ext = self.ext.lower()
    
    def __str__(self):
        return self.abspath
    
    def __repr__(self):
        info = ",\n\t".join([
            "abspath='%s'" % self.abspath,
            "dirname='%s'" % self.dirname,
            "basename='%s'" % self.basename,
            "fname='%s'" % self.fname,
            "ext='%s'" % self.ext,
        ])
        return "WinFile(\n\t%s,\n)" % info 
    
    def to_dict(self):
        d = dict()
        for attr in self.__slots__:
            try:
                d[attr] = self.__getattribute__(attr)
            except AttributeError:
                pass
        return d

    def rename(self, new_dirname=None, new_fname=None, new_ext=None):
        """Rename the dirname, fname, extension or their combinations.
        
        **中文文档**
        
        对文件的父目录名, 纯文件名, 扩展名, 或它们的组合进行修改。
        """
        if not new_dirname:
            new_dirname = self.dirname
        else:
            new_dirname = os.path.abspath(new_dirname)
        if not new_fname:
            new_fname = self.fname
        if new_ext: # 检查新文件名的扩展名格式是否
            if not new_ext.startswith("."):
                raise ValueError("File extension must in format .ext, "
                                 "for example: .jpg, .mp3")
        else:
            new_ext = self.ext
        new_basename = new_fname + new_ext
        new_abspath = os.path.join(new_dirname, new_basename)

        os.rename(self.abspath, new_abspath)
        # 如果成功重命名, 则更新文件信息
        self.abspath = new_abspath
        self.dirname = new_dirname
        self.basename = new_basename
        self.fname = new_fname
        self.ext = new_ext 


class WinDir(object):
    """Windows directory class.
    
    **中文文档**
    
    Windows目录对象, 可以通过 .属性名来访问 绝对路径, 目录总大小, 子目录数量, 
    子文件数量。免去了使用os.path.function的麻烦。并提供了prt_detail()方法直接
    打印出文件夹的详细信息。
    
    WinDir的属性:
    
    - self.size_total: 文件夹总大小
    - self.size_current_total: 文件夹一级子文件总大小
    
    - self.num_folder_total: 子文件夹数量
    - self.num_folder_current: 一级子文件夹数量
    
    - self.num_file_total: 子文件数量
    - self.num_file_current: 一级子文件数量
    """
    def __init__(self, abspath):
        if os.path.isdir(abspath): # 确保这是一个目录而不是文件
            self.abspath = os.path.abspath(abspath)
            self.dirname, self.basename = os.path.split(self.abspath)
            self.get_detail()
        else:
            raise ValueError("'%s' is not a file." % abspath)

    def __str__(self):
        return self.abspath
    
    def __repr__(self):
        return self.abspath
    
    def get_detail(self):
        """Get general stats information.
        
        Includes:
        
        - size_total: total size on disk
        - num_folder_total: how many subfolders
        - num_file_total: how many files
        - size_current: total size of files on this folder. file in subfolders 
            doesn't count
        - num_folder_current: how many files, subfolders doens't count
        - num_file_current: how many files, file in subfolders doens't count
        """
        self.size_total = 0
        self.num_folder_total = 0
        self.num_file_total = 0
        
        self.size_current = 0
        self.num_folder_current = 0
        self.num_file_current = 0
        
        for current_dir, folderlist, fnamelist in os.walk(self.abspath):
            self.num_folder_total += len(folderlist)
            self.num_file_total += len(fnamelist)
            for fname in fnamelist:
                self.size_total += os.path.getsize(os.path.join(current_dir, fname))
                
        current_dir, folderlist, fnamelist = next(os.walk(self.abspath))
        self.num_folder_current = len(folderlist)
        self.num_file_current = len(fnamelist)
        for fname in fnamelist:
            self.size_current += os.path.getsize(os.path.join(current_dir, fname))
        
    def prt_detail(self):
        """Nicely print stats information.
        """
        screen = [
            "Detail info of %s: " % self.abspath,
            "total size = %s" % string_SizeInBytes(self.size_total),
            "number of sub folders = %s" % self.num_folder_total,
            "number of total files = %s" % self.num_file_total,
            "lvl 1 file size = %s" % string_SizeInBytes(self.size_current),
            "lvl 1 folder number = %s" % self.num_folder_current,
            "lvl 1 file number = %s" % self.num_file_current,
        ]
        print("\n".join(screen))

    def rename(self, new_dirname=None, new_basename=None):
        """Rename the dirname, basename or their combinations.
        
        **中文文档**
        
        对文件的目录名, 文件夹名, 或它们的组合进行修改。
        """
        if not new_basename:
            new_basename = self.new_basename
        if not new_dirname:
            new_dirname = self.dirname
        else:
            new_dirname = os.path.abspath(new_dirname)
        new_abspath = os.path.join(new_dirname, new_basename)
        os.rename(self.abspath, new_abspath)
        
        # 如果成功重命名, 则更新文件信息
        self.abspath = new_abspath
        self.dirname = new_dirname
        self.basename = new_basename


class FileCollection(object):
    """A container class of WinFile.
    
    Simplify file selection, removing, filtering, sorting operations.
    
    Here's an example select all files and wrap as a WinFile::
    
        >>> from angora.filesystem.filesystem import FileCollection
        >>> fc = FileCollection.from_path("some_path")
        >>> for winfile in fc.iterfiles():
        ...     print(winfile)
    
    **中文文档**
    
    WinFile的专用容器, 主要用于方便的从文件夹中选取文件, 筛选文件, 并对指定文件集排序。
    当然, 可以以迭代器的方式对容器内的文件对象进行访问。
    """
    def __init__(self):
        self.files = OrderedDict() # {文件绝对路径: 包含各种详细信息的WinFile对象}
    
    def __str__(self):
        if len(self.files) == 0:
            return "***Empty FileCollection***"
        try:
            return "\n".join(list(self.order))
        except:
            return "\n".join(list(self.files.keys()))
    
    def __len__(self):
        return len(self.files)
    
    def __getitem__(self, index):
        """Get the ``index``th winfile. 
        """
        try:
            return self.files[self.order[index]]
        except:
            index += 1
            for winfile in self.iterfiles():
                index -= 1                
                if not index:
                    return winfile
    
    def __contains__(self, item):
        """
        """
        if isinstance(item, str): # abspath
            abspath = os.path.abspath(item)
        elif isinstance(item, WinFile): # WinFile
            abspath = item.abspath
        else: # invalid type
            raise TypeError
        
        if abspath in self.files:
            return True
        else:
            return False
        
    def add(self, abspath_or_winfile, enable_verbose=True):
        """Add absolute path or WinFile to FileCollection.
        """
        if isinstance(abspath_or_winfile, str): # abspath
            if abspath_or_winfile in self.files:
                if enable_verbose:
                    print("'%s' already in this collections" % 
                          abspath_or_winfile)
            else:
                self.files.setdefault(abspath_or_winfile, WinFile(abspath_or_winfile))
        elif isinstance(abspath_or_winfile, WinFile): # WinFile
            if abspath_or_winfile.abspath in self.files:
                if enable_verbose:
                    print("'%s' already in this collections" % 
                          abspath_or_winfile)
            else:
                self.files.setdefault(abspath_or_winfile.abspath, abspath_or_winfile)
        else:
            raise TypeError
        
    def remove(self, abspath_or_winfile, enable_verbose=True):
        """Remove absolute path or WinFile from FileCollection.
        """
        if isinstance(abspath_or_winfile, str): # abspath
            try:
                del self.files[abspath_or_winfile]
            except KeyError:
                if enable_verbose:
                    print("'%s' are not in this file collections" % 
                          abspath_or_winfile)
        elif isinstance(abspath_or_winfile, WinFile): # WinFile
            try:
                del self.files[abspath_or_winfile.abspath]
            except KeyError:
                if enable_verbose:
                    print("'%s' are not in this file collections" % 
                          abspath_or_winfile)
        else:
            raise TypeError
    
    @property     
    def howmany(self):
        """An alias of __len__() method.
        """
        return len(self.files)
    
    def iterfiles(self):
        """Yield all WinFile object.
        """
        try:
            for path in self.order:
                yield self.files[path]
        except:
            for winfile in self.files.values():
                yield winfile
                
    def iterpaths(self):
        """Yield all WinFile's absolute path.
        """
        try:
            for path in self.order:
                yield path
        except:
            for path in self.files:
                yield path
    
    def __iter__(self):
        """Default iterator is to yield absolute paht only.
        """
        return self.iterpaths()


    @staticmethod
    def yield_all_file_path(dir_abspath):
        """
        
        **中文文档**
        
        遍历path目录下的所有文件, 返回绝对路径。
        """
        if os.path.isdir(dir_abspath):
            dir_abspath = os.path.abspath(dir_abspath)
            for current_folder, _, fnamelist in os.walk(dir_abspath):
                for fname in fnamelist:
                    yield os.path.join(current_folder, fname)
        else:
            raise FileNotFoundError(
                "'%s' may not exists or is not a directory!" % dir_abspath)
            
    @staticmethod
    def yield_all_winfile(dir_abspath):
        """
        
        **中文文档**
        
        遍历path目录下的所有文件, 返回WinFile。
        """
        for abspath in FileCollection.yield_all_file_path(dir_abspath):
            yield WinFile(abspath)
            
    @staticmethod
    def yield_all_top_file_path(dir_abspath):
        """
        
        **中文文档**
        
        遍历path目录下的所有文件, 不包括子文件夹中的文件, 返回绝对路径。
        """
        if os.path.isdir(dir_abspath):
            dir_abspath = os.path.abspath(dir_abspath)
            for current_folder, _, fnamelist in os.walk(dir_abspath):
                for fname in fnamelist:
                    yield os.path.join(current_folder, fname)
                break
        else:
            raise FileNotFoundError(
                "'%s' may not exists or is not a directory!" % dir_abspath)
            
    @staticmethod
    def yield_all_top_winfile(dir_abspath):
        """
        
        **中文文档**
        
        遍历path目录下的所有文件, 不包括子文件夹中的文件, 返回WinFile。
        """
        for abspath in FileCollection.yield_all_top_file_path(dir_abspath):
            yield WinFile(abspath)

    @staticmethod
    def yield_all_dir_path(dir_abspath):
        """
        
        **中文文档**
        
        遍历dir_abspath目录下的所有子目录, 返回绝对路径。
        """
        if os.path.isdir(dir_abspath):
            for current_folder, folderlist, _ in os.walk(dir_abspath):
                for folder in folderlist:
                    yield os.path.join(current_folder, folder)
        else:
            raise Exception(
                "'%s' may not exists or is not a directory!" % dir_abspath)

    @staticmethod
    def yield_all_windir(dir_abspath):
        """
        
        **中文文档**
        
        遍历dir_abspath目录下的所有子目录, 返回绝对WinDir。
        """
        for abspath in FileCollection.yield_all_dir_path(dir_abspath):
            yield WinDir(abspath)

    @staticmethod
    def yield_all_top_dir_path(dir_abspath):
        """
        
        **中文文档**
        
        遍历dir_abspath目录下的所有子目录, 不包括子目录中的子目录, 返回绝对路径。
        """
        if os.path.isdir(dir_abspath):
            for current_folder, folderlist, _ in os.walk(dir_abspath):
                for folder in folderlist:
                    yield os.path.join(current_folder, folder)
                break
        else:
            raise Exception(
                "'%s' may not exists or is not a directory!" % dir_abspath)

    @staticmethod
    def yield_all_top_windir(dir_abspath):
        
        """
        
        **中文文档**
        
        遍历dir_abspath目录下的所有子目录, 不包括子目录中的子目录, 返回绝对WinDir。
        """
        for abspath in FileCollection.yield_all_top_dir_path(dir_abspath):
            yield WinDir(abspath)
    
    @staticmethod
    def remove_children(list_of_abspath):
        """Remove all dir path that being children path of other dir path.
        
        **中文文档**
        
        去除list_of_abspath中所有目录的子目录, 保证其中的所有元素不可能为另一个
        元素的子目录。
        """
        sorted_list_of_abspath = list(list_of_abspath)
        sorted_list_of_abspath.sort()
        sorted_list_of_abspath.append("")  
        res = list()
        temp = sorted_list_of_abspath[0]
        for abspath in sorted_list_of_abspath:
            if temp not in abspath:
                res.append(temp)
                temp = abspath         
        return res
    
    @staticmethod
    def from_path(list_of_dir):
        """Create a new FileCollection and add all files from ``dir_path``.
        
        :param list_of_dir: absolute dir path, WinDir instance, list of 
          absolute dir path or list of WinDir instance.
          
        **中文文档**
        
        添加dir_path目录下的所有文件到一个新的FileCollection中.
        """
        if isinstance(list_of_dir, str):
            list_of_dir = [list_of_dir, ]
        elif isinstance(list_of_dir, WinDir):
            list_of_dir = [list_of_dir.abspath, ]
        elif isinstance(list_of_dir, list):
            list_of_dir = [str(i) for i in list_of_dir]
            
        fc = FileCollection()
        for dir_path in list_of_dir:
            for winfile in FileCollection.yield_all_winfile(dir_path):
                fc.files.setdefault(winfile.abspath, winfile)
        return fc
    
    @staticmethod
    def from_path_by_criterion(dir_path, criterion, keepboth=False):
        """Create a new FileCollection, and select some files from ``dir_path``.
        
        How to construct your own criterion function::
        
            def filter_image(winfile):
                if winfile.ext in [".jpg", ".png", ".bmp"]:
                    return True
                else:
                    return False
        
            fc = FileCollection.from_path_by_criterion(dir_path, filter_image)
        
        :param dir_path: path of a directory
        :type dir_path: string
        :param criterion: customize filter function
        :type criterion: function
        :param keepboth: if True, returns two file collections, one is files
            with criterion=True, another is False.
        :type keepboth: boolean
        
        **中文文档**
        
        直接选取dir_path目录下所有文件, 根据criterion中的规则, 生成
        FileCollection。
        """
        if keepboth:
            fc_yes, fc_no = FileCollection(), FileCollection()
            for winfile in FileCollection.yield_all_winfile(dir_path):
                if criterion(winfile):
                    fc_yes.files.setdefault(winfile.abspath, winfile)
                else:
                    fc_no.files.setdefault(winfile.abspath, winfile)
            return fc_yes, fc_no
        else:
            fc = FileCollection()
            for winfile in FileCollection.yield_all_winfile(dir_path):
                if criterion(winfile):
                    fc.files.setdefault(winfile.abspath, winfile)
            return fc
    
    @staticmethod
    def from_path_except(dir_path, 
            ignore=list(), ignore_ext=list(), ignore_pattern=list()):
        """Create a new FileCollection, and select all files except file
        matching ignore-rule::
            
            dir_path = "your/path"
            fc = FileCollection.from_path_except(
                dir_path, ignore=["test"], ignore_ext=[".log", ".tmp"]
                ignore_pattern=["some_pattern"])
        
        :param dir_path: the root directory you want to start with
        :param ignore: file or directory defined in this list will be ignored.
        :param ignore_ext: file with extensions defined in this list will be ignored.
        :param ignore_pattern: any file or directory that contains this pattern
          will be ignored.
          
        **中文文档**
        
        选择dir_path下的所有文件, 在ignore, ignore_ext, ignore_pattern中所定义
        的文件将被排除在外。
        """
        ignore = [i.lower() for i in ignore]
        ignore_ext = [i.lower() for i in ignore_ext]
        ignore_pattern = [i.lower() for i in ignore_pattern]
        def filter(winfile):
            relpath = os.path.relpath(winfile.abspath, dir_path).lower()
            
            # exclude ignore
            for path in ignore:
                if relpath.startswith(path):
                    return False
                
            # exclude ignore extension
            if winfile.ext in ignore_ext:
                return False

            # exclude ignore pattern
            for pattern in ignore_pattern:
                if pattern in relpath:
                    return False
            
            return True
        
        return FileCollection.from_path_by_criterion(
            dir_path, filter, keepboth=False)
    
    @staticmethod
    def from_path_by_pattern(dir_path, pattern=list()):
        """Create a new FileCollection, and select all files except file
        matching ignore-rule::
            
            dir_path = "your/path"
            fc = FileCollection.from_path_by_pattern(
                dir_path, pattern=["log"])
        
        :param dir_path: the root directory you want to start with
        :param pattern: any file or directory that contains this pattern
          will be selected.
          
        **中文文档**
        
        选择dir_path下的所有文件的相对路径中包含有pattern的文件。
        """
        pattern = [i.lower() for i in pattern]
        def filter(winfile):
            relpath = os.path.relpath(winfile.abspath, dir_path).lower()
            for p in pattern:
                if p in relpath:
                    return True
            return False
        
        return FileCollection.from_path_by_criterion(
            dir_path, filter, keepboth=False)
        
    @staticmethod
    def from_path_by_size(dir_path, min_size=0, max_size=1 << 40):
        """Create a new FileCollection, and select all files that size in
        a range::
            
            dir_path = "your/path"
            
            # select by file size larger than 100MB
            fc = FileCollection.from_path_by_size(
                dir_path, min_size=100*1024*1024)
            
            # select by file size smaller than 100MB
            fc = FileCollection.from_path_by_size(
                dir_path, max_size=100*1024*1024)
                
            # select by file size from 1MB to 100MB
            fc = FileCollection.from_path_by_size(
                dir_path, min_size=1024*1024, max_size=100*1024*1024)
        """
        def filter(winfile):
            if (winfile.size_on_disk >= min_size) and \
                (winfile.size_on_disk <= max_size):
                return True
            else:
                return False

        return FileCollection.from_path_by_criterion(
            dir_path, filter, keepboth=False)
        
    @staticmethod
    def from_path_by_ext(dir_path, ext):
        """Create a new FileCollection, and select all files that extension 
        matching ``ext``::
        
            dir_path = "your/path"
            
            fc = FileCollection.from_path_by_ext(dir_path, ext=[".jpg", ".png"])
        """
        if isinstance(ext, (list, set, dict)): # collection of extension
            def filter(winfile):
                if winfile.ext in ext:
                    return True
                else:
                    return False
        else: # str
            def filter(winfile):
                if winfile.ext == ext:
                    return True
                else:
                    return False

        return FileCollection.from_path_by_criterion(
            dir_path, filter, keepboth=False)

    @staticmethod
    def from_path_by_md5(md5_value, list_of_dir):
        """Create a new FileCollection, and select all files' that md5 is 
        matching.
        
        **中文文档**
        
        给定一个文件使用WinFile模块获得的md5值, 在list_of_dir中的文件里, 
        找到与之相同的文件。
        """       
        def filter(winfile):
            if winfile.md5 == md5_value:
                return True
            else:
                return False
        
        if not isinstance(list_of_dir, (list, set)):
            list_of_dir = [list_of_dir, ]        
            
        init_mode = WinFile.init_mode
        WinFile.use_slow_init()
        
        fc = FileCollection()
        for dir_path in list_of_dir:
            for winfile in FileCollection.from_path_by_criterion(
                    dir_path, filter, keepboth=False).iterfiles():
                fc.files.setdefault(winfile.abspath, winfile)
        
        if init_mode == 1:
            WinFile.use_fast_init()
        elif init_mode == 2:
            WinFile.use_regular_init()
        elif init_mode == 3:
            WinFile.use_slow_init()
                
        return fc

    def sort_by(self, attr_name, reverse=False):
        """Sort files by one of it's attributes.
        
        **中文文档**
        
        对容器内的WinFile根据其某一个属性升序或者降序排序。
        """
        try:
            d = dict()
            for abspath, winfile in self.files.items():
                d[abspath] = getattr(winfile, attr_name)
            self.order = [item[0] for item in sorted(
                list(d.items()), key=lambda t: t[1], reverse = reverse)]
        except AttributeError:
            raise ValueError("valid sortable attributes are: "
                             "abspath, dirname, basename, fname, ext, "
                             "size_on_disk, atime, ctime, mtime;")
            
    def sort_by_abspath(self, reverse=False):
        """
        
        **中文文档**
        
        对WinFile根据 **绝对路径** 进行排序。
        """
        self.sort_by("abspath", reverse=reverse)

    def sort_by_dirname(self, reverse=False):
        """
        
        **中文文档**
        
        对WinFile根据 **父目录路径** 进行排序。
        """
        self.sort_by("dirname", reverse=reverse)

    def sort_by_fname(self, reverse=False):
        """
        
        **中文文档**
        
        对WinFile根据 **纯文件名** 进行排序。
        """
        self.sort_by("fname", reverse=reverse)
             
    def sort_by_ext(self, reverse=False):
        """
        
        **中文文档**
        
        对WinFile根据 **文件扩展名** 进行排序。
        """
        self.sort_by("ext", reverse=reverse)

    def sort_by_atime(self, reverse=False):
        """
        
        **中文文档**
        
        对WinFile根据 **文件最后一次被触碰的时间** 进行排序。
        """
        self.sort_by("atime", reverse=reverse)
        
    def sort_by_ctime(self, reverse=False):
        """
        
        **中文文档**
        
        对WinFile根据 **文件被创建的时间** 进行排序。
        """
        self.sort_by("ctime", reverse=reverse)
        
    def sort_by_mtime(self, reverse=False):
        """
        
        **中文文档**
        
        对WinFile根据 **文件最后一次被修改的时间** 进行排序。
        """
        self.sort_by("mtime", reverse=reverse)
        
    def sort_by_size(self, reverse=False):
        """
        
        **中文文档**
        
        对WinFile根据 **文件在硬盘上的大小** 进行排序。
        """
        self.sort_by("size_on_disk", reverse=reverse)
         
    def select(self, criterion, keepboth=False):
        """Filter current file collections, create another file collections 
        contains all winfile with criterion=True.
        
        How to construct your own criterion function, see 
        :meth:`FileCollection.from_path_by_criterion`.

        :param criterion: customize filter function
        :type criterion: function
        :param keepboth: if True, returns two file collections, one is files
            with criterion=True, another is False.
        :type keepboth: boolean
        
        **中文文档**
        
        在当前的文件集合中, 根据criterion中的规则, 选择需要的生成
        FileCollection。当keepboth参数=True时, 返回两个FileCollection, 一个
        是符合条件的文件集合, 一个是不符合条件的。
        """
        if keepboth:
            fcs_yes, fcs_no = FileCollection(), FileCollection()
            for winfile in self.files.values():
                if criterion(winfile):
                    fcs_yes.files[winfile.abspath] = winfile
                else:
                    fcs_no.files[winfile.abspath] = winfile
            return fcs_yes, fcs_no
        else:
            fcs = FileCollection()
            for winfile in self.files.values():
                if criterion(winfile):
                    fcs.files[winfile.abspath] = winfile
            
            return fcs
        
    def __add__(self, other_fc):
        if not isinstance(other_fc, FileCollection):
            raise TypeError(
                "A FileCollection has to add with another FileCollection")
            
        fc = copy.deepcopy(self)
        for winfile in other_fc.iterfiles():
            fc.files.setdefault(winfile.abspath, winfile)
        return fc
    
    @staticmethod
    def sum(list_of_fc):
        for fc in list_of_fc:
            if not isinstance(fc, FileCollection):
                raise TypeError("FileCollection.sum(list_of_fc) only take "
                                "list of FileCollection")
        
        _fc = FileCollection()
        for fc in list_of_fc:
            for winfile in fc.iterfiles():
                _fc.files.setdefault(winfile.abspath, winfile)
        return _fc

    def __sub__(self, other_fc):
        if not isinstance(other_fc, FileCollection):
            raise TypeError(
                "A FileCollection has to add with another FileCollection")
            
        fc = copy.deepcopy(self)
        for abspath in other_fc.iterpaths():
            try:
                del fc.files[abspath]
            except:
                pass
        return fc

    #--- Useful recipe ---
    @staticmethod
    def show_big_file(dir_path, threshold):
        """Print all file path that file size greater and equal than 
        ``#threshold``.
        """
        fc = FileCollection.from_path_by_size(dir_path, min_size=threshold)
        fc.sort_by("size_on_disk")
        
        lines = list()
        lines.append("Results:")
        for winfile in fc.iterfiles():
            lines.append("  %s - %s" % 
                         (string_SizeInBytes(winfile.size_on_disk), winfile))
        lines.append("Above are files' size greater than %s." % 
              string_SizeInBytes(threshold))
        text = "\n".join(lines)
        print(text)
        with open("__show_big_file__.log", "wb") as f:
            f.write(text.encode("utf-8"))
    
    @staticmethod
    def show_patterned_file(dir_path, pattern=list(), filename_only=True):
        """Print all file that file name contains ``pattern``.
        """
        pattern = [i.lower() for i in pattern]
        if filename_only:
            def filter(winfile):
                for p in pattern:
                    if p in winfile.fname.lower():
                        return True
                return False
        else:
            def filter(winfile):
                for p in pattern:
                    if p in winfile.abspath.lower():
                        return True
                return False
        
        fc = FileCollection.from_path_by_criterion(
            dir_path, filter, keepboth=False)
        if filename_only:
            fc.sort_by("fname")
        else:
            fc.sort_by("abspath")
            
        table = {p: "<%s>" % p for p in pattern}
        lines = list()
        lines.append("Results:")
        for winfile in fc.iterfiles():
            lines.append("  %s" % winfile)
            
        if filename_only:
            lines.append("Above are all files that file name contains %s" % pattern)
        else:
            lines.append("Above are all files that abspath contains %s" % pattern)
            
        text = "\n".join(lines)
        print(text)
        with open("__show_patterned_file__.log", "wb") as f:
            f.write(text.encode("utf-8"))
            
    @staticmethod
    def create_fake_mirror(src, dst):
        """Copy all dir, files from ``src`` to ``dst``. But only create a empty file 
        with same file name. Of course, the tree structure doesn't change.
        
        A recipe gadget to create some test data set.
        
        Make sure to use absolute path.
        
        **中文文档**
        
        复制整个src目录下的文件树结构到dst目录。但实际上并不复制内容, 只复制
        文件名。即, 全是空文件, 但目录结构一致。
        """
        src = os.path.abspath(src)
        if not (os.path.exists(src) and (not os.path.exists(dst)) ):
            raise Exception("source not exist or distination already exist")
        
        folder_to_create = list()
        file_to_create = list()
        
        for current_folder, _, file_list in os.walk(src):
            new_folder = os.path.join(dst, os.path.relpath(current_folder, src))
            folder_to_create.append(new_folder)
            for basename in file_list:
                file_to_create.append(os.path.join(new_folder, basename))
                
        for abspath in folder_to_create:
            os.mkdir(abspath)
        
        for abspath in file_to_create:
            with open(abspath, "w") as _:
                pass

    
class FileFilter(object):
    """File filter container class.
    """
    @staticmethod
    def image(winfile):
        if winfile.ext in [".jpg", ".jpeg", ".png", ".gif", ".tiff",
                           ".bmp", ".ppm", ".pgm", ".pbm", ".pnm", ".svg"]:
            return True
        else:
            return False
    
    @staticmethod
    def audio(winfile):
        if winfile.ext in [".mp3", ".mp4", ".aac", ".m4a", ".wma", 
                           ".wav", ".ape", ".tak", ".tta", 
                           ".3gp", ".webm", ".ogg",]:
            return True
        else:
            return False
        
    @staticmethod
    def video(winfile):
        if winfile.ext in [".avi", ".wmv", ".mkv", ".mp4", ".flv", 
                ".vob", ".mov", ".rm", ".rmvb", "3gp", ".3g2", ".nsv", ".webm",
                ".mpg", ".mpeg", ".m4v", ".iso",]:
            return True
        else:
            return False
        
    @staticmethod
    def pdf(winfile):
        if winfile.ext == ".pdf":
            return True
        else:
            return False

    @staticmethod
    def word(winfile):
        if winfile.ext == ".doc":
            return True
        else:
            return False
        
    @staticmethod
    def excel(winfile):
        if winfile.ext == ".xlsx":
            return True
        else:
            return False
        
    @staticmethod
    def ppt(winfile):
        if winfile.ext == ".ppt":
            return True
        else:
            return False


#--- Unittest ---
if __name__ == "__main__":
    import unittest
    
    class WinFileUnittest(unittest.TestCase):
        def test_initialize(self):
            """测试WinFile多种初始化方式的实现。
            """
            level3_attributes = set([
                "abspath", "dirname", "basename", "fname", "ext",
                "atime", "ctime", "mtime", "size_on_disk", "md5",
            ])
            WinFile.set_initialize_mode(complexity=3)
            winfile = WinFile("filesystem.py")
            attributes = set(winfile.to_dict())
            self.assertEqual(attributes, level3_attributes)

            level2_attributes = set([
                "abspath", "dirname", "basename", "fname", "ext",
                "atime", "ctime", "mtime", "size_on_disk",   
            ])
            WinFile.set_initialize_mode(complexity=2)
            winfile = WinFile("filesystem.py")
            attributes = set(winfile.to_dict())
            self.assertEqual(attributes, level2_attributes)

            level1_attributes = set([
                "abspath", "dirname", "basename", "fname", "ext",
            ])
            WinFile.set_initialize_mode(complexity=1)
            winfile = WinFile("filesystem.py")
            attributes = set(winfile.to_dict())
            self.assertEqual(attributes, level1_attributes)
            
            # 测试完毕, 恢复初始化模式为默认值
            WinFile.set_initialize_mode(complexity=2)
            
#         def test_str_and_repr(self):
#             winfile = WinFile("filesystem.py")
#             print(repr(winfile))
        
        def test_rename(self):
            """测试文件重命名功能。
            """
            winfile = WinFile("test.txt")
            
            # 修改文件名为test1
            winfile.rename(new_fname="test1")
            d = winfile.to_dict()
            self.assertEqual(d["fname"], "test1")
            
            # 将文件名修改回test
            winfile.rename(new_fname="test")
            d = winfile.to_dict()
            self.assertEqual(d["fname"], "test")
        
    class WinDirUnittest(unittest.TestCase):
        def test_detail(self):
            windir = WinDir("testdir")
    
    class FileCollectionUnittest(unittest.TestCase):
        def setUp(self):
            self._dir = "testdir"
            
#         def test_yield_file(self):            
#             print("{:=^100}".format("yield_all_file_path"))
#             for abspath in FileCollection.yield_all_file_path(self._dir):
#                 print(abspath)
#               
#             print("{:=^100}".format("yield_all_winfile"))
#             for winfile in FileCollection.yield_all_winfile(self._dir):
#                 print(repr(winfile))
#               
#             print("{:=^100}".format("yield_all_top_file_path"))
#             for abspath in FileCollection.yield_all_top_file_path(self._dir):
#                 print(abspath)
#               
#             print("{:=^100}".format("yield_all_top_winfile"))
#             for winfile in FileCollection.yield_all_top_winfile(self._dir):
#                 print(repr(winfile))
                
        def test_from_path(self):
            fc = FileCollection.from_path(self._dir)
            expect = ["root_file.txt", "root_image.jpg", 
                      "sub_file.txt", "sub_image.jpg"]
            for winfile, basename in zip(fc.iterfiles(), expect):
                self.assertEqual(winfile.basename, basename)
        
        def test_from_path_by_criterion(self):
            def image_filter(winfile):
                if winfile.ext in [".jpg", ".png"]:
                    return True
                else:
                    return False
                
            fc_yes, fc_no = FileCollection.from_path_by_criterion(
                self._dir, image_filter, keepboth=True)
            
            expect_yes = ["root_image.jpg", "sub_image.jpg"]
            expect_no = ["root_file.txt", "sub_file.txt"]
            
            for winfile, basename in zip(fc_yes.iterfiles(), expect_yes):
                self.assertEqual(winfile.basename, basename)
            for winfile, basename in zip(fc_no.iterfiles(), expect_no):
                self.assertEqual(winfile.basename, basename)
        
        def test_from_path_except(self):
            """测试from_path_except方法是否能正常工作。
            """
            fc = FileCollection.from_path_except(
                "testdir", ignore=["subfolder"])
            expect = ["root_file.txt", "root_image.jpg"]
            for winfile, basename in zip(fc.iterfiles(), expect):
                self.assertEqual(winfile.basename, basename)

            fc = FileCollection.from_path_except(
                "testdir", ignore_ext=[".jpg"])
            expect = ["root_file.txt", "sub_file.txt"]
            for winfile, basename in zip(fc.iterfiles(), expect):
                self.assertEqual(winfile.basename, basename)

            fc = FileCollection.from_path_except(
                "testdir", ignore_pattern=["image"])
            expect = ["root_file.txt", "sub_file.txt"]
            for winfile, basename in zip(fc.iterfiles(), expect):
                self.assertEqual(winfile.basename, basename)

        def test_from_path_by_pattern(self):
            """测试from_path_by_pattern方法是否能正常工作。
            """
            fc = FileCollection.from_path_by_pattern(
                "testdir", pattern=["sub"])
            expect = ["sub_file.txt", "sub_image.jpg"]
            for winfile, basename in zip(fc.iterfiles(), expect):
                self.assertEqual(winfile.basename, basename)

        def test_from_path_by_size(self):
            """测试from_from_path_by_size方法是否能正常工作。
            """
            fc = FileCollection.from_path_by_size("testdir", min_size=1024)
            expect = ["root_image.jpg", "sub_image.jpg"]
            for winfile, basename in zip(fc.iterfiles(), expect):
                self.assertEqual(winfile.basename, basename)
                
            fc = FileCollection.from_path_by_size("testdir", max_size=1024)
            expect = ["root_file.txt", "sub_file.txt"]
            for winfile, basename in zip(fc.iterfiles(), expect):
                self.assertEqual(winfile.basename, basename)    

        def test_from_path_by_ext(self):
            """测试from_path_by_ext方法是否能正常工作。
            """
            fc = FileCollection.from_path_by_ext("testdir", ext=".jpg")
            expect = ["root_image.jpg", "sub_image.jpg"]
            for winfile, basename in zip(fc.iterfiles(), expect):
                self.assertEqual(winfile.basename, basename)
                
            fc = FileCollection.from_path_by_ext("testdir", ext=[".txt"])
            expect = ["root_file.txt", "sub_file.txt"]
            for winfile, basename in zip(fc.iterfiles(), expect):
                self.assertEqual(winfile.basename, basename)    

        def test_from_path_by_md5(self):
            WinFile.set_initialize_mode(complexity=3)
            winfile = WinFile("winzip.py")
            WinFile.set_initialize_mode(complexity=2)
                        
            res = FileCollection.from_path_by_md5(
                winfile.md5, r"C:\Python33\Lib\site-packages\angora")
            self.assertEqual(res[0].basename, "winzip.py")

        def test_add_and_remove(self):
            """测试添加WinFile和删除WinFile的方法是否正常工作。
            """
            fc = FileCollection()
            fc.add("filesystem.py")
            self.assertEqual(fc.howmany, 1)
            fc.remove("filesystem.py")
            self.assertEqual(fc.howmany, 0)
            
        def test_sort(self):
            """测试排序功能是否正常工作。
            """
            fc = FileCollection.from_path(self._dir)
            fc.sort_by_abspath()
            fc.sort_by_dirname()
            fc.sort_by_fname()
            fc.sort_by_ext()
            fc.sort_by_atime()
            fc.sort_by_ctime()
            fc.sort_by_mtime()
            fc.sort_by_size()
        
        def test_add(self):
            """测试两个集合相加是否正常工作。
            """
            fc1 = FileCollection.from_path(self._dir)
            fc2 = FileCollection.from_path(self._dir)
            fc3 = FileCollection()
            fc3.add("filesystem.py")
            
            fc = fc1 + fc2 + fc3
            self.assertEqual(fc.howmany, 5)
            
            fc = FileCollection.sum([fc1, fc2, fc3])
            self.assertEqual(fc.howmany, 5)

        def test_sub(self):
            """测试两个集合相减是否正常工作。
            """
            fc1 = FileCollection.from_path(self._dir)
            fc2 = FileCollection.from_path(self._dir)
            fc = fc1 - fc2
            self.assertEqual(fc.howmany, 0)
        
#         def test_create_fake_mirror(self):
#             src = r"C:\Users\shu\Documents\PythonWorkSpace\py3\py33_projects\filesystem-project\filemonkey\lib\filesystem\testdir"
#             dst = r"C:\Users\shu\Documents\PythonWorkSpace\py3\py33_projects\filesystem-project\filemonkey\lib\filesystem\mirror"
#             FileCollection.create_fake_mirror(src, dst)
 
        def test_show_big_file(self):
            FileCollection.show_big_file(self._dir, 1000)

        def test_show_patterned_file(self):
            FileCollection.show_patterned_file(self._dir, ["image",])
            
    unittest.main()