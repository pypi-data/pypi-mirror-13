#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import os
import sys
import time
import datetime

try:
    import requests
except ImportError as e:
    print("[Failed to do 'import requests', "
          "please install requests]: %s" % e)
try:
    from ..gadget.messenger import Messenger
except:
    from angora.gadget.messenger import Messenger


_default_iter_size = 1024 * 1024


def string_SizeInBytes(size_in_bytes):
    """Make ``size in bytes`` human readable.
    Doesn"t support size greater than 1000PB.

    Usage::

        >>> from __future__ import print_function
        >>> from weatherlab.lib.filesystem.windowsexplorer import string_SizeInBytes
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
    res, by = divmod(size_in_bytes, 1024)
    res, kb = divmod(res, 1024)
    res, mb = divmod(res, 1024)
    res, gb = divmod(res, 1024)
    pb, tb = divmod(res, 1024)
    if pb != 0:
        human_readable_size = "%.2f PB" % (pb + tb / float(1024))
    elif tb != 0:
        human_readable_size = "%.2f TB" % (tb + gb / float(1024))
    elif gb != 0:
        human_readable_size = "%.2f GB" % (gb + mb / float(1024))
    elif mb != 0:
        human_readable_size = "%.2f MB" % (mb + kb / float(1024))
    elif kb != 0:
        human_readable_size = "%.2f KB" % (kb + by / float(1024))
    else:
        human_readable_size = "%s B" % by
    return human_readable_size


def download_url(url, save_as, iter_size=_default_iter_size, enable_verbose=True):
    """A simple url binary content download function with progress info.

    Warning: this function will silently overwrite existing file.
    """
    msg = Messenger()
    if enable_verbose:
        msg.on()
    else:
        msg.off()

    msg.show("Downloading %s from %s..." % (save_as, url))

    with open(save_as, "wb") as f:
        response = requests.get(url, stream=True)

        if not response.ok:
            print("http get error!")
            return

        start_time = time.clock()
        downloaded_size = 0
        for block in response.iter_content(iter_size):
            if not block:
                break
            f.write(block)
            elapse = datetime.timedelta(seconds=(time.clock() - start_time))
            downloaded_size += sys.getsizeof(block)
            msg.show("    Finished %s, elapse %s." % (
                string_SizeInBytes(downloaded_size), elapse
            ))

    msg.show("    Complete!")

if __name__ == "__main__":
    import unittest

    class DownloaderUnittest(unittest.TestCase):
        def test_download_url(self):
            url = "https://www.python.org//static/img/python-logo.png"
            save_as = "python-logo.png"
            download_url(url, save_as, iter_size=1024, enable_verbose=True)
            try:
                os.remove(save_as)
            except:
                pass

    unittest.main()