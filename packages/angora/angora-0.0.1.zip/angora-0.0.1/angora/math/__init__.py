#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module description
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

math is the package includes general numeric computation packages.


Compatibility
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Python2: Yes
- Python3: Yes
    
    
Prerequisites
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- numpy
- scipy
- sklearn
- matplotlib
- pandas (optional) 
"""

from .interp import (linear_interpolate, linear_interpolate_by_datetime, 
                     exam_reliability, exam_reliability_by_datetime,
                     spline_interpolate, spline_interpolate_by_datetime)
from .img2waveform import img2ascii, img2wav
from .outlier import std_filter, box_filter