#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module description
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
pytimer is a timer application can easily measure run time in your program.

    
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

from __future__ import print_function
import timeit
import time

class Timer(object):
    """Timer makes time measurement easy.
    """
    def __init__(self):
        self.elapse = 0.0
        self.records = list()
    
    @property
    def total_elapse(self):
        return sum(self.records)
        
    # === single time, multiple time measurement ===
    def start(self):
        """Start measuring.
        """
        self.st = time.clock()
        
    def stop(self):
        """Save last elapse time to self.records.
        """
        self.elapse = time.clock() - self.st
        self.records.append(self.elapse)

    def timeup(self):
        """Print the last measurement elapse time, and return it.
        """
        self.stop()
        print("elapse %0.6f seconds" % self.elapse)

    def click(self):
        """Record the last elapse time and start the next measurement.
        """
        self.stop()
        self.start()

    def display(self):
        """Print the last elapse time.
        """
        print("elapse %0.6f sec" % self.elapse)
    
    def display_all(self):
        """Print detailed information.
        """
        print( ("total elapse %0.6f seconds, last elapse %0.6f seconds, "
                "took %s times measurement") % (
                    self.total_elapse, self.elapse, len(self.records)))
        
    def reset(self):
        """Reset the timer.
        """
        self.elapse = 0.0
        self.records.clear()

    # === function runtime measurement ===
    @staticmethod
    def test(func, howmany=1):
        """Run function speed test #howmany times, and display the: average, total, repeat times.
        you can call this simply by Timer.test(func)
        
        for more complicate case, use standard library 
        'timeit <https://docs.python.org/2/library/timeit.html>'_
        """
        elapse = timeit.Timer(func).timeit(howmany)
        print("average = %0.6f seconds, total = %0.6f seconds, repeat %s times." % (
                elapse/howmany, elapse, howmany) )

############
# Unittest #
############

if __name__ == "__main__":
    """unit test, usage example
    """
    timer = Timer()
    
    def basic_usage():
        """shows the basic usage by defining the start and the end
        """
        complexity = 1000000
        array = list(range(complexity))
        
        timer.start()
        for index in range(len(array)):
            array[index]
        timer.timeup()

        timer.start()
        for _ in array:
            pass
        timer.timeup()

        timer.start()
        _ = [str(i) for i in range(complexity)]
        timer.timeup()
        
        timer.start()
        _ = list(map(str, range(complexity)))
        timer.timeup()
        
        timer.display_all()
        
    basic_usage()

    def function_runtime_test_usage():
        """shows the way to measure average runtime of a function
        """
        complexity = 1000000
        array = list(range(complexity))
        
        def iter_list1():
            for _ in array:
                pass
            
        def iter_list2():
            for index in range(len(array)):
                array[index]     

        timer.test(iter_list1, 100)
        timer.test(iter_list2, 100)
        
        Timer.test(iter_list1, 100)
        Timer.test(iter_list2, 100)

    function_runtime_test_usage()
    
    def clicker_usage():
        """shows measuring multiple times seamlessly
        """
        timer.start()
        for i in range(1000000):
            if (i % 1000) == 0:
                timer.click()
        
        timer.display_all()

    clicker_usage()