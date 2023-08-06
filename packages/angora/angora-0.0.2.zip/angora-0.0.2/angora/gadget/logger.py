#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module description
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**中文文档**

一个开箱即用的自定义logger类。


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

import logging


class EZLogger(object):
    """A quick logger constructor.
    
    :param name: logger name
    :param path: log file path, default None, do not write to file
    :param logging_level: debug level above this will be logged 
    :param stream_level: debug level above this will be printed to console
    :param format: log format
    """
    tab = "    "

    def __init__(self, name="root", path=None,
                 logging_level=logging.DEBUG,
                 stream_level=logging.INFO,
                 format="%(asctime)s; %(levelname)-8s; %(message)s"):
        logger = logging.getLogger(name)

        # Logging level
        logger.setLevel(logging.DEBUG)

        # Print screen level
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        logger.addHandler(ch)

        # File handler
        if path:
            fh = logging.FileHandler(path, encoding="utf-8")

            # Formatter
            formatter = logging.Formatter(format)
            fh.setFormatter(formatter)
            logger.addHandler(fh)

        self.logger = logger

    def debug(self, msg, indent=0):
        self.logger.debug("%s%s" % (self.tab * indent, msg))

    def info(self, msg, indent=0):
        self.logger.info("%s%s" % (self.tab * indent, msg))

    def warning(self, msg, indent=0):
        self.logger.warning("%s%s" % (self.tab * indent, msg))

    def error(self, msg, indent=0):
        self.logger.error("%s%s" % (self.tab * indent, msg))

    def critical(self, msg, indent=0):
        self.logger.critical("%s%s" % (self.tab * indent, msg))


#--- Unittest ---
if __name__ == "__main__":
    logger = EZLogger(name="test", path="log.txt")
    logger.debug("debug")
    logger.info("info", 1)
    logger.warning("warning", 2)
    logger.error("error", 3)
    logger.critical("critical", 4)
