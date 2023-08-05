#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module description
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module provides function to filter clean data and outlier.


Usage Example
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    >>> from angora.math import * 
    >>> array = np.concatenate([np.random.randn(100), 
    ...                         np.random.randn(20) * 3.0, 
    ...                         np.random.randn(10) * 10,])
    >>> good, bad = std_filter(array, n_std=2.0)
    >>> bad
    [-17.95652268  13.25276002   8.89243813  -7.07794533 -16.48135043]


Compatibility
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Python2: Yes
- Python3: Yes


Prerequisites
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- `numpy <http://www.numpy.org/>`_


Class, method, function, exception
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

try:
    import numpy as np
except ImportError as e:
    print("[Failed to do 'import numpy', "
          "please install numpy]: %s" % e)

def std_filter(array, n_std=2.0, return_index=False):
    """Standard deviation outlier detector.
    
    :param array: array of data.
    :param n_std: default 2.0, exclude data out of ``n_std`` standard deviation.
    :param return_index: boolean, default False, if True, only returns index.
    """
    if not isinstance(array, np.ndarray):
        array = np.array(array)
    mean, std = array.mean(), array.std()
    
    good_index = np.where( abs(array - mean) <= n_std * std)
    bad_index = np.where( abs(array - mean) > n_std * std)

    if return_index:
        return good_index[0], bad_index[0]
    else:
        return array[good_index], array[bad_index]

def box_filter(array, n_iqr=1.5, return_index=False):
    """Box plot outlier detector.
    
    :param array: array of data.
    :param n_std: default 1.5, exclude data out of ``n_iqr`` IQR.
    :param return_index: boolean, default False, if True, only returns index.
    """
    if not isinstance(array, np.ndarray):
        array = np.array(array)
    Q3 = np.percentile(array, 75)
    Q1 = np.percentile(array, 25)
    IQR = Q3 - Q1
    lower, upper = Q1 - n_iqr * IQR, Q3 + n_iqr * IQR
    
    good_index = np.where(np.logical_and(array >= lower, array <= upper))
    bad_index = np.where(np.logical_or(array < lower, array > upper))
    
    if return_index:
        return good_index[0], bad_index[0]
    else:
        return array[good_index], array[bad_index]

if __name__ == "__main__":
    import unittest
    
    array = np.concatenate([np.random.randn(100), 
                            np.random.randn(20) * 3.0, 
                            np.random.randn(10) * 10,])
    
    class Unittest(unittest.TestCase):            
        def test_std_filter(self):
            good, bad = std_filter(array, n_std=2.0)
            
        def test_box_filter(self):
            good, bad = box_filter(array, n_iqr=1.5)
            
    unittest.main()