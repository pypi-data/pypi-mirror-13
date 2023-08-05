#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module description
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module offer high performance and memory efficient looping toolset. 
Usually we process elements one at a time rather than bringing the whole
iterable into memory all at once.

- :func:`take`: Return first n items of the iterable as a list.
- :func:`flatten`: Flatten one layer of nesting.
- :func:`flatten_all`: Flatten arbitrary depth of nesting. Good for unknown 
  nesting structure iterable object.
- :func:`nth`: Returns the nth item or a default value.
- :func:`shuffled`: Returns the shuffled iterable.
- :func:`grouper`: Collect data into fixed-length chunks or blocks.
- :func:`grouper_list`: Evenly divide LIST into fixed-length piece, no filled 
  value if chunk size smaller than fixed-length.
- :func:`grouper_dict`: Evenly divide DICTIONARY into fixed-length piece, no 
  filled value if chunk size smaller than fixed-length.
- :func:`running_windows`: Generate n-size running windows.
- :func:`cycle_running_windows`: Generate n-size cycle running windows.
- :func:`cycle_slice`: Given a list, return right hand cycle direction slice 
  from start to end.
- :func:`shift_to_the_left`: shift array to the left.
- :func:`shift_to_the_right`: shift array to the right.
- :func:`count_generator`: Count number of item in generator.


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
import collections
import itertools
import random
import sys

is_py2 = (sys.version_info[0] == 2)
if is_py2:
    from itertools import ifilterfalse as filterfalse, izip_longest as zip_longest
else: # in python3
    from itertools import filterfalse, zip_longest

def take(n, iterable):
    """Return first n items of the iterable as a list.
    
    Usage::
        
        >>> take([0, 1, 2], 2)
        [0, 1]
    """
    return list(itertools.islice(iterable, n))

def flatten(list_of_list):
    """Flatten one layer of nesting.
    
    Usage::
        
        >>> flatten([[0, 1], [2, 3]]
        [0, 1, 2, 3]
    """
    return itertools.chain.from_iterable(list_of_list)

def flatten_all(list_of_list):
    """Flatten arbitrary depth of nesting. Good for unknown nesting structure 
    iterable object.
    
    Usage::
    
        >>> flatten_all([[0, 1], [2, 3, [4, 5], [6, 7, 8]], [9,]])
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    """
    for i in list_of_list:
        if hasattr(i, "__iter__"):
            for j in flatten_all(i):
                yield j
        else:
            yield i
    
def nth(iterable, n, default=None):
    """Returns the nth item or a default value.

    Usage::
        
        >>> nth([0, 1, 2], 1)
        1
        
        >>> nth([0, 1, 2], 100)
        None
    """
    return next(itertools.islice(iterable, n, None), default)

def shuffled(iterable):
    """Returns the shuffled iterable.
    
    Usage::
    
        >>> shuffled([0, 1, 2]
        [2, 0, 1]
    """
    return random.sample(iterable, len(iterable))

def grouper(iterable, n, fillvalue=None):
    """Collect data into fixed-length chunks or blocks.
    
    Usage::
    
        >>> list(grouper(range(10), n=3, fillvalue=1024))
        [(0, 1, 2), (3, 4, 5), (6, 7, 8), (9, 1024, 1024)]
    """
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
    args = [iter(iterable)] * n
    return zip_longest(fillvalue=fillvalue, *args)

def grouper_list(LIST, n):
    """Evenly divide LIST into fixed-length piece, no filled value if chunk 
    size smaller than fixed-length.
    
    Usage::
    
        >>> list(grouper(range(10), n=3)
        [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]
    """
    for group in grouper(LIST, n):
        chunk_l = list()
        for i in group:
            if i != None:
                chunk_l.append(i)
        yield chunk_l
        
def grouper_dict(DICT, n):
    """Evenly divide DICTIONARY into fixed-length piece, no filled value if 
    chunk size smaller than fixed-length.
    
    Usage::
    
        >>> list(grouper_dict({1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E', 
                               6: 'F', 7: 'G', 8: 'H', 9: 'I', 10: 'J'}))
        [{1: 'A', 2: 'B', 3: 'C'}, {4: 'D', 5: 'E', 6: 'F'},
         {7: 'G', 8: 'H', 9: 'I'}, {10: 'J'}]
    """
    for group in grouper(DICT, n):
        chunk_d = dict()
        for k in group:
            if k != None:
                chunk_d[k] = DICT[k]
        yield chunk_d

def running_windows(iterable, size):
    """Generate n-size running windows.
    
    Usage::
        
        >>> for i in running_windows([1, 2, 3, 4, 5], size=3):
        ...     print(i)
        [1, 2, 3]
        [2, 3, 4]
        [3, 4, 5]
    """
    fifo = collections.deque(maxlen=size)
    for i in iterable:
        fifo.append(i)
        if len(fifo) == size:
            yield list(fifo)
            
def cycle_running_windows(iterable, size):
    """Generate n-size cycle running windows.
    
    Usage::
        
        >>> for i in running_windows([1, 2, 3, 4, 5], size=3):
        ...     print(i)
        [1, 2, 3]
        [2, 3, 4]
        [3, 4, 5]
        [4, 5, 1]
        [5, 1, 2]
    """
    fifo = collections.deque(maxlen=size)
    cycle = itertools.cycle(iterable)
    counter = itertools.count(1)
    length = len(iterable)
    for i in cycle:
        fifo.append(i)
        if len(fifo) == size:
            yield list(fifo)
            if next(counter) == length:
                break

def cycle_slice(LIST, start, end):
    """Given a list, return right hand cycle direction slice from start to end.
    
    Usage::
        
        >>> array = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        >>> cycle_slice(array, 4, 7) # from array[4] to array[7]
        [4, 5, 6, 7]

        >>> cycle_slice(array, 8, 2) # from array[8] to array[2]
        [8, 9, 0, 1, 2]
    """
    if type(LIST) != list:
        LIST = list(LIST)
        
    if end >= start:
        return LIST[start:end+1]
    else:
        return LIST[start:] + LIST[:end+1]

def shift_to_the_left(array, dist, pad=True, trim=True):
    """shift array to the left.

    :param array: An iterable object.
    :type array: iterable object
    :param dist: how far you want to shift
    :type disk: int
    :param pad: pad array[-1] to the right.
    :type pad: boolean (default True)
    :param trim: trim the first ``#dist`` items.
    :type trim: boolean (default True)
    
    Usage::
    
        >>> array = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        >>> shift_to_the_left(self.iterable_list, 1, pad=True, trim=True)
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 9]

        >>> shift_to_the_left(self.iterable_list, 1, pad=True, trim=False)
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 9]
        
        >>> shift_to_the_left(self.iterable_list, 1, pad=False, trim=True)
        [1, 2, 3, 4, 5, 6, 7, 8, 9]
        
        >>> shift_to_the_left(self.iterable_list, 1, pad=True, trim=True)
        Warning, with pad=False and trim=False, no change applied.
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    """
    if dist < 0:
        raise ValueError("Shift distance has to greater or equal than 0.")
    
    if pad:
        if trim:
            new_array = array[dist:] + [array[-1]] * dist
        else:
            new_array = array + [array[-1]] * dist
    else:
        if trim:
            new_array = array[dist:]
        else:
            print("Warning, with pad=False and trim=False, no change applied.")
            new_array = list(array)
    return new_array

def shift_to_the_right(array, dist, pad=True, trim=True):
    """shift array to the right.

    :param array: An iterable object.
    :type array: iterable object
    :param dist: how far you want to shift
    :type disk: int
    :param pad: pad array[0] to the left.
    :type pad: boolean (default True)
    :param trim: trim the last ``#dist`` items.
    :type trim: boolean (default True)
    
    Usage::
    
        >>> array = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        >>> shift_to_the_right(self.iterable_list, 1, pad=True, trim=True)
        [0, 0, 1, 2, 3, 4, 5, 6, 7, 8]

        >>> shift_to_the_right(self.iterable_list, 1, pad=True, trim=False)
        [0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        
        >>> shift_to_the_right(self.iterable_list, 1, pad=False, trim=True)
        [0, 1, 2, 3, 4, 5, 6, 7, 8]
        
        >>> shift_to_the_right(self.iterable_list, 1, pad=True, trim=True)
        Warning, with pad=False and trim=False, no change applied.
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    """
    if dist < 0:
        raise ValueError("Shift distance has to greater or equal than 0.")
    
    if pad:
        if trim:
            new_array = [array[0]] * dist + array[:-dist]
        else:
            new_array = [array[0]] * dist + array
    else:
        if trim:
            new_array = array[:-dist]
        else:
            print("Warning, with pad=False and trim=False, no change applied.")
            new_array = list(array)
    return new_array

def count_generator(generator, memory_efficient=True):
    """Count number of item in generator.
    
    memory_efficient=True, 3 times slower, but memory_efficient.
    memory_efficient=False, faster, but cost more memory.
    """
    if memory_efficient:
        counter = 0
        for _ in generator:
            counter += 1
        return counter
    else:
        return len(list(generator))

if __name__ == "__main__":
    from angora.GADGET.pytimer import Timer
    import time
    import unittest
    timer = Timer()

    class IterToolsUnittest(unittest.TestCase):
        def setUp(self):
            """
            self.iterable_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
            self.iterable_set = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9}
            self.iterable_dict = {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E', 
                                  6: 'F', 7: 'G', 8: 'H', 9: 'I', 10: 'J',}
            """
            self.iterable_generator = range(10)
            self.iterable_list = list(range(10))
            self.iterable_set = set(list(range(10)))
            self.iterable_dict = {i: chr(j) for i, j in zip(range(1, 11), range(65, 75))}

        def test_take(self):
            self.assertEqual(take(5, self.iterable_generator), [0, 1, 2, 3, 4])
            self.assertEqual(take(5, self.iterable_list), [0, 1, 2, 3, 4])
            self.assertEqual(take(5, self.iterable_set), [0, 1, 2, 3, 4])
            self.assertEqual(take(5, self.iterable_dict), [1, 2, 3, 4, 5])

        def test_flatten_functionality(self):
            iterable = [[0, 1], [2, 3]]
            self.assertListEqual(list(flatten(iterable)), list(range(4)))
            
        def test_flatten_performance(self):
            complexity = 1000
            iterable = [list(range(complexity))] * complexity
            
            st = time.clock()
            for _ in flatten(iterable):
                pass
            elapse_flatten = time.clock()- st

            st = time.clock()
            for chunk in iterable:
                for _ in chunk:
                    pass
            elapse_double_loop = time.clock()- st
            
            self.assertGreater(elapse_flatten, elapse_double_loop)

        def test_flatten_all_functionality(self):
            iterable = [[0, 1], [2, 3, [4, 5], [6, 7, 8]], [9,]]
            self.assertListEqual(list(flatten_all(iterable)), 
                                 list(range(10)))
                                 
        
        def test_nth(self):
            self.assertEqual(nth(self.iterable_list, 5), 5)
            self.assertEqual(nth(self.iterable_list, 100), None)
            
        def test_shuffled(self):
            self.assertNotEqual(shuffled(self.iterable_list), 
                                self.iterable_list)
        
        def test_grouper(self):
            self.assertEqual(
                list(grouper(self.iterable_list, 3, 1024)),
                [(0, 1, 2), (3, 4, 5), (6, 7, 8), (9, 1024, 1024)],
                )

        def test_grouper_list(self):
            self.assertEqual(
                list(grouper_list(self.iterable_list, 3)),
                [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]],
                )
            
        def test_grouper_dict(self):
            self.assertEqual(
                list(grouper_dict(self.iterable_dict, 3)),
                [
                    {1: 'A', 2: 'B', 3: 'C'},
                    {4: 'D', 5: 'E', 6: 'F'},
                    {7: 'G', 8: 'H', 9: 'I'},
                    {10: 'J'}
                ],
                )
        
        def test_running_windows(self):
            self.assertEqual(
                list(running_windows([1,2,3,4,5], 3)),
                [[1, 2, 3], [2, 3, 4], [3, 4, 5]],
                )
        
        def test_cycle_running_windows(self):
            self.assertEqual(
                list(cycle_running_windows([1,2,3,4,5], 3)),
                [[1, 2, 3], [2, 3, 4], [3, 4, 5], [4, 5, 1], [5, 1, 2]],
                )
            
        def test_cycle_slice(self):
            self.assertEqual(
                list(cycle_slice(self.iterable_list, 4, 7)),
                [4,5,6,7],
                )
            self.assertEqual(
                list(cycle_slice(self.iterable_list, 8, 2)),
                [8,9,0,1,2],
                )
        
        def test_padding_left_shift(self):
            self.assertEqual(
                shift_to_the_left(self.iterable_list, 1, pad=True, trim=True),
                [1, 2, 3, 4, 5, 6, 7, 8, 9, 9],
                )
            self.assertEqual(
                shift_to_the_left(self.iterable_list, 1, pad=True, trim=False),
                [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 9],
                )
            self.assertEqual(
                shift_to_the_left(self.iterable_list, 1, pad=False, trim=True),
                [1, 2, 3, 4, 5, 6, 7, 8, 9],
                )            

        def test_shift_to_the_left(self):
            self.assertEqual(
                shift_to_the_left(self.iterable_list, 1, pad=True, trim=True),
                [1, 2, 3, 4, 5, 6, 7, 8, 9, 9],
                )
            self.assertEqual(
                shift_to_the_left(self.iterable_list, 1, pad=True, trim=False),
                [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 9],
                )
            self.assertEqual(
                shift_to_the_left(self.iterable_list, 1, pad=False, trim=True),
                [1, 2, 3, 4, 5, 6, 7, 8, 9],
                )
            
        def test_shift_to_the_right(self):
            self.assertEqual(
                shift_to_the_right(self.iterable_list, 1, pad=True, trim=True),
                [0, 0, 1, 2, 3, 4, 5, 6, 7, 8],
                )
            self.assertEqual(
                shift_to_the_right(self.iterable_list, 1, pad=True, trim=False),
                [0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                )
            self.assertEqual(
                shift_to_the_right(self.iterable_list, 1, pad=False, trim=True),
                [0, 1, 2, 3, 4, 5, 6, 7, 8],
                )
                
        
        def test_count_generator(self):
            self.assertEqual(count_generator(self.iterable_generator), 10)
            
    unittest.main()

    def test_flatten_performance():
        """测试flatten的性能
        
        flatten()本应该要比二重循环性能好, 但是似乎没能达到。
        """
        print("{:=^40}".format("test flatten()"))
        complexity = 1000
        iterable = [list(range(complexity))] * complexity
        
        st = time.clock()
        for _ in flatten(iterable):
            pass
        print("fatten() method takes %.6f second" % (time.clock() - st))

        st = time.clock()
        for chunk in iterable:
            for _ in chunk:
                pass
        print("double for loop method takes %.6f second" % (time.clock() - st))
    
#     test_flatten_performance()
    
    def test_flatten_all_performance():
        """测试flatten_all的性能。
        
        flatten_all()虽然更方便一些, 但是性能上是不如根据已知的结构, 用多重
        for loop循环来的好。
        """
        print("{:=^40}".format("test flatten_all()"))
        complexity = 100
        a = [[[1] * complexity] * complexity] * complexity
        
        st = time.clock()
        for _ in flatten_all(a):
            pass
        print("fatten_all() method takes %.6f second" % (time.clock() - st))
        
        st = time.clock()
        for l1 in a:
            for l2 in l1:
                for _ in l2:
                    pass
        print("nested for loop method takes %.6f second" % (time.clock() - st))
        
#     test_flatten_all_performance()

    def test_nth_performance():
        """测试nth的性能。
        
        对于只定义了__iter__而没有定义__getitem__方法的对象, nth()是比较合适的
        做法。当然速度完全比不上list自带的索引方法list[i]。
        """
        print("{:=^40}".format("test nth()"))
        n = 10000
        array = [i for i in range(n)]
        
        st = time.clock()
        for i in range(n):
            _ = array[i]
        print("iterable[i] method %.6f second" % (time.clock() - st))
        
        st = time.clock()
        for i in range(n):
            _ = nth(array, i)
        print("nth(iterable, i) method %.6f second" % (time.clock() - st))
        
        st = time.clock()
        for i in array:
            _ = i
        print("build-in for loop method %.6f second" % (time.clock() - st))
        
#     test_nth_performance()
    
    def test_count_generator_performance():
        """测试count_generator()的性能。
        """
        def number_generator():
            for i in range(1000 * 1000):
                yield i
        
        print("{:=^40}".format("test count_generator()"))
        timer.start()
        count_generator(number_generator(), memory_efficient=True)
        print("memory_efficient way takes %s second" % timer.stop())
        
        timer.start()
        count_generator(number_generator(), memory_efficient=False)
        print("non-memory_efficient way takes %s second" % timer.stop())
        
#     test_count_generator_performance()