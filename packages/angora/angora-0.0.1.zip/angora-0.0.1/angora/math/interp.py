#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module description
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module provides utility function to do linear and cubic interpolation.


Highlight
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

exam_reliability() function provides a fast reliability check for interpolation.
Suppose that you interpolate a point at x1, and the distance from nearest points
in original x_axis is d1. If d1 <= criterion, so we can trust this interp.
Otherwise, we cannot trust. This function returns you the reliability boolean
flag array for your interpolation.


Usage Example
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Here's an example of linear and spline interpolation::

    >>> from weatherlab.math.interp import rigid_linear_interpolate
    >>> import matplotlib.pyplot as plt
    >>> import numpy as np
    >>> x = np.linspace(0, 10, 10) # generate test data
    >>> y = np.cos(-x**2/8.0)
    >>> x_new = np.linspace(0, 10, 40)
    >>> y_cubic = spline_interpolate(x, y, x_new) # do interpolation
    >>> y_linear = linear_interpolate(x, y, x_new)
     
    >>> plt.plot(x, y, "o", # plot
    ...          x_new, y_cubic,"g-", 
    ...          x_new, y_linear,"r--" )
    >>> plt.ylim([-1.05, 2.05])
    >>> plt.legend(["raw data", "cubic interp", "linear interp"])
    >>> plt.show()


.. image:: images/interpolate.png
    :align: center

If you want to play with datetime::

    >>> from weatherlab.math.interp import rigid_linear_interpolate
    >>> from weatherlab.lib.timelib.timewrapper import timewrapper
    >>> import matplotlib.pyplot as plt
    >>> import numpy as np
    >>> x = timewrapper.dtime_range(start="2014-01-01 00:00:00", 
    ...                             end="2014-01-02 01:00:00", 
    ...                             freq="2hour") # generate test data
    >>> y = np.cos( np.linspace(0, 10, len(x) ) ** 2 / 8.0 )
    >>> x_new = timewrapper.dtime_range(start="2014-01-01 00:00:00", 
    ...                                 end="2014-01-01 23:59:59", 
    ...                                 freq="10min")
    >>> y_cubic = spline_interpolate_by_datetime(x, y, x_new) # do interpolation
    >>> y_linear = linear_interpolate_by_datetime(x, y, x_new)
    
    >>> plt.plot(x, y, "o", # plot
    ...          x_new, y_cubic, "g-",
    ...          x_new, y_linear, "r--")
    >>> plt.ylim([-1.05, 2.05])
    >>> plt.legend(["raw data", "cubic interp", "linear interp"])
    >>> plt.show()

.. image:: images/interpolate_by_datetime.png
    :align: center


Compatibility
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Python2: Yes
- Python3: Yes


Prerequisites
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- `numpy <http://www.numpy.org/>`_
- `scipy <http://www.scipy.org/>`_


Class, method, function, exception
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from __future__ import print_function
try:
    from scipy.interpolate import interp1d
except ImportError as e:
    print("[Failed to do 'from scipy.interpolate import interp1d', "
          "please install scipy]: %s" % e)
from datetime import datetime, timedelta

##############################
# timestamp method extension #
##############################
def totimestamp(datetime_object):
    """Because in python2 datetime doesn't have timestamp() method,
    so we have to implement in a python2,3 compatible way.
    """
    return (datetime_object - datetime(1969, 12, 31, 20, 0)).total_seconds()

def fromtimestamp(timestamp):
    """Because python doesn't support negative timestamp to datetime
    so we have to implement my own method
    """
    if timestamp >= 0:
        return datetime.fromtimestamp(timestamp)
    else:
        return datetime(1969, 12, 31, 20, 0) + timedelta(seconds=timestamp)

######################
# Linear interpolate #
######################
def locate(x1, y1, x2, y2, x3):
    """An equation solver to solve: given two points on a line and x, solve the
    y coordinate on the same line.
    
    Suppose p1 = (x1, y1), p2 = (x2, y2), p3 = (x3, y3) on the same line.
    given x1, y1, x2, y2, x3, find y3::
    
        y3 = y1 - (y1 - y2) * (x1 - x3) / (x1 - x3)
    """
    return y1 - 1.0 * (y1 - y2) * (x1 - x3) / (x1 - x2)

def rigid_linear_interpolate(x_axis, y_axis, x_new_axis):
    """Interpolate a y = f(x) function using linear interpolation.
    
    Rigid means the x_new_axis has to be in x_axis's range.
    """
    f = interp1d(x_axis, y_axis)
    return f(x_new_axis)
            
def rigid_linear_interpolate_by_datetime(datetime_axis, y_axis, datetime_new_axis):
    """A datetime-version that takes datetime object list as x_axis.
    """
    numeric_datetime_axis = [
        totimestamp(a_datetime) for a_datetime in datetime_axis
        ]
    
    numeric_datetime_new_axis = [
        totimestamp(a_datetime) for a_datetime in datetime_new_axis
        ]
    
    return rigid_linear_interpolate(
        numeric_datetime_axis, y_axis, numeric_datetime_new_axis)
    
def linear_interpolate(x_axis, y_axis, x_new_axis, enable_warning=True):
    """Interpolate a y = f(x) function using linear interpolation.
    
    A smart way to interpolate arbitrary-range x_new_axis. The trick is 
    to add one more point to the original x_axis at x_new_axis[0] and 
    x_new_axis[-1], if x_new_axis is out of range.
    """
    left_pad_x, left_pad_y = list(), list()
    right_pad_x, right_pad_y = list(), list() 

    if x_new_axis[0] < x_axis[0]:
        if enable_warning:
            print("WARNING! the first element of x_new_axis is at left "
                  "of x_axis. Use linear_interpolate(enable_warning=False) "
                  "to disable this warning.")
        left_pad_x.append(x_new_axis[0])
        left_pad_y.append(locate(x_axis[0], y_axis[0], 
                                 x_axis[1], y_axis[1], x_new_axis[0]))

    if x_new_axis[-1] > x_axis[-1]:
        if enable_warning:
            print("WARNING! the last element of x_new_axis is at right "
                  "of x_axis. Use linear_interpolate(enable_warning=False) "
                  "to disable this warning.")
        right_pad_x.append(x_new_axis[-1])
        right_pad_y.append(locate(x_axis[-1], y_axis[-1], 
                                  x_axis[-2], y_axis[-2], x_new_axis[-1]))
        
    if not ( (len(left_pad_x) == 0) and (len(right_pad_x) == 0) ):
        x_axis = left_pad_x + x_axis + right_pad_x
        y_axis = left_pad_y + y_axis + right_pad_y
        
    return rigid_linear_interpolate(x_axis, y_axis, x_new_axis)

def linear_interpolate_by_datetime(datetime_axis, y_axis, datetime_new_axis, 
                                   enable_warning=True):
    """A datetime-version that takes datetime object list as x_axis
    """
    numeric_datetime_axis = [
        totimestamp(a_datetime) for a_datetime in datetime_axis
        ]
    
    numeric_datetime_new_axis = [
        totimestamp(a_datetime) for a_datetime in datetime_new_axis
        ]
    
    return linear_interpolate(
        numeric_datetime_axis, y_axis, numeric_datetime_new_axis, 
        enable_warning=enable_warning)

def exam_reliability(x_axis, x_axis_new, reliable_distance, precision=0.0001):
    """When we do linear interpolation on x_axis and derive value for 
    x_axis_new, we also evaluate how can we trust those interpolated 
    data points. This is how it works:
    
    For each new x_axis point in x_axis new, let's say xi. Find the closest 
    point in x_axis, suppose the distance is #dist. Compare this to 
    #reliable_distance. If #dist < #reliable_distance, then we can trust it, 
    otherwise, we can't.
    
    The precision is to handle decimal value's precision problem. Because 
    1.0 may actually is 1.00000000001 or 0.999999999999 in computer system. 
    So we define that: if ``dist`` + ``precision`` <= ``reliable_distance``, then we 
    can trust it, else, we can't.
        
    Here is an O(n) algorithm implementation. A lots of improvement than 
    classic binary search one, which is O(n^2).
    """
    x_axis = x_axis[::-1]
    x_axis.append(-2**32)
    
    distance_to_closest_point = list()
    for t in x_axis_new:
        while 1:
            try:
                x = x_axis.pop()
                if x <= t:
                    left = x
                else:
                    right = x
                    x_axis.append(right)
                    x_axis.append(left)
                    left_dist, right_dist = (t - left), (right - t)
                    if left_dist <= right_dist:
                        distance_to_closest_point.append(left_dist)
                    else:
                        distance_to_closest_point.append(right_dist)
                    break
            except:
                distance_to_closest_point.append(t - left)
                break
            
    reliable_flag = list()
    for dist in distance_to_closest_point:
        if dist - precision - reliable_distance <= 0:
            reliable_flag.append(True)
        else:
            reliable_flag.append(False)
            
    return reliable_flag

def exam_reliability_by_datetime(
        datetime_axis, datetime_new_axis, reliable_distance):
    """A datetime-version that takes datetime object list as x_axis
    reliable_distance equals to the time difference in seconds.
    """
    numeric_datetime_axis = [
        totimestamp(a_datetime) for a_datetime in datetime_axis
        ]
    
    numeric_datetime_new_axis = [
        totimestamp(a_datetime) for a_datetime in datetime_new_axis
        ]
    
    return exam_reliability(numeric_datetime_axis, numeric_datetime_new_axis, 
        reliable_distance, precision=0)

####################################
# Cubic interpolate, more accurate #
####################################
def spline_interpolate(x_axis, y_axis, x_new_axis):
    """Interpolate a y = f(x) function using Spline interpolation algorithm, 
    x_new_axis has to be in range of x_axis.
    
    `Spline interpolation <https://en.wikipedia.org/wiki/Spline_interpolation>`_
    is a popular interpolation method. Way more accurate than linear interpolate
    in average
    """
    f = interp1d(x_axis, y_axis, kind="cubic")
    return f(x_new_axis)
 
def spline_interpolate_by_datetime(datetime_axis, y_axis, datetime_new_axis):
    """A datetime-version that takes datetime object list as x_axis
    """
    numeric_datetime_axis = [
        totimestamp(a_datetime) for a_datetime in datetime_axis
        ]
    
    numeric_datetime_new_axis = [
        totimestamp(a_datetime) for a_datetime in datetime_new_axis
        ]
    
    return spline_interpolate(
        numeric_datetime_axis, y_axis, numeric_datetime_new_axis)

#-----------------------------------------------------------------------------#
#                                  Unittest                                   #
#-----------------------------------------------------------------------------#
if __name__ == "__main__":
    import numpy as np, pandas as pd
    import matplotlib.pyplot as plt
    import unittest
    
    class LinearInterpolateUnittest(unittest.TestCase):
        def test_linear_interpolate(self):
            x = [1, 2, 3]
            y = [1, 2, 3]
            x_new1 = [1, 1.5, 2, 2.5, 3]
            y_new1 = linear_interpolate(x, y, x_new1)
            x_new2 = [0, 1, 2, 3, 4]
            y_new2 = linear_interpolate(x, y, x_new2)
            
            for i, j in zip(y_new1, [1, 1.5, 2, 2.5, 3]):
                self.assertAlmostEqual(i, j, 0.001)
            for i, j in zip(y_new2, [0, 1, 2, 3, 4]):
                self.assertAlmostEqual(i, j, 0.001)
    
        def test_linear_interpolate_by_datetime(self):
            x = [datetime(2014,1,1,0,0,10), datetime(2014,1,1,0,0,20)]
            y = [1, 2]
            x_new1 = [datetime(2014,1,1,0,0,5), 
                      datetime(2014,1,1,0,0,15), 
                      datetime(2014,1,1,0,0,25)]
            y_new1 = linear_interpolate_by_datetime(x, y, x_new1)
            for i, j in zip(y_new1, [0.5, 1.5, 2.5]):
                self.assertAlmostEqual(i, j, 0.001)
        
        def test_exam_reliability(self):
            x = [1, 2, 3, 4]
            x_new = [0.4, 0.6, 1.7, 2.5, 3.3, 4.4, 4.5]
            self.assertListEqual(
                exam_reliability(x, x_new, 0.4),
                [False, False, True, False, True, False, False],
                )
            
#     unittest.main() # You can comment unittest and run usage example

    def usage_interpolate():
        x = np.linspace(0, 10, 10)
        y = np.cos(-x**2/8.0)
        x_new = np.linspace(0, 10, 40)
         
        y_cubic = spline_interpolate(x, y, x_new)
        y_linear = linear_interpolate(x, y, x_new)
         
        plt.plot(x, y, "o", 
                 x_new, y_cubic,"g-", 
                 x_new, y_linear,"r--" )
        plt.ylim([-1.05, 2.05])
        plt.legend(["raw data", "cubic interp", "linear interp"])
        plt.show()

#     usage_interpolate()
     
    def usage_interpolate_by_datetime():
        x = pd.date_range(start="2014-01-01 00:00:00", 
                          end="2014-01-02 01:00:00", 
                          freq="2H")
        y = np.cos( np.linspace(0, 10, len(x) ) ** 2 / 8.0 )
        x_new = pd.date_range(start="2014-01-01 00:00:00", 
                              end="2014-01-01 23:59:59", 
                              freq="10min")
        y_cubic = spline_interpolate_by_datetime(x, y, x_new)
        y_linear = linear_interpolate_by_datetime(x, y, x_new)
        plt.plot(x, y, "o",
                 x_new, y_cubic, "g-",
                 x_new, y_linear, "r--")
        plt.ylim([-1.05, 2.05])
        plt.legend(["raw data", "cubic interp", "linear interp"])
        plt.show()
    
#     usage_interpolate_by_datetime()

    x = [0, 5, 10]
    x_new = [-2, -1, 0, 1, 2, 3,4 ,5,6,7,8,9, 10, 11,12]
    res = exam_reliability(x, x_new, 1.0),
    print(res)