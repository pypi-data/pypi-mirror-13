#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module description
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module provide some 'out of box' method to plot time series data.


Compatibility
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- Python2: Yes
- Python3: Yes


Prerequisites
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- numpy
- pandas
- matplotlib


Class, method, function, exception
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

try:
    import matplotlib.pyplot as plt
    from matplotlib.dates import YearLocator, MonthLocator, WeekdayLocator, DayLocator
    from matplotlib.dates import HourLocator, MinuteLocator
    from matplotlib.dates import DateFormatter
    from matplotlib.dates import MO, TU, WE, TH, FR, SA, SU
except ImportError as e:
    print("[Failed to do 'import matplotlib.pyplot as plt']: %s" % e)

def plot_one_day(x, y, xlabel=None, ylabel=None, title=None, ylim=None):
    """时间跨度为一天。
    
    major tick = every hours
    minor tick = every 15 minutes
    """
    plt.close("all")
    
    fig = plt.figure(figsize=(20, 10))
    ax = fig.add_subplot(111)
    ax.plot(x, y)
    
    hours = HourLocator(range(24))
    hoursFmt = DateFormatter("%H:%M")
    minutes = MinuteLocator([30,])
    minutesFmt = DateFormatter("%M")
    
    ax.xaxis.set_major_locator(hours)
    ax.xaxis.set_major_formatter(hoursFmt)
    ax.xaxis.set_minor_locator(minutes)
    ax.xaxis.set_minor_formatter(minutesFmt)
    
    ax.autoscale_view()
    ax.grid()
    plt.setp( ax.xaxis.get_majorticklabels(), rotation=90 )
    plt.setp( ax.xaxis.get_minorticklabels(), rotation=90 )
    
    if xlabel:
        plt.xlabel(xlabel)
    else:
        plt.xlabel("Time")
        
    if ylabel:
        plt.ylabel(ylabel)
    else:
        plt.ylabel("Value")
        
    if title:
        plt.title(title)
    else:
        plt.title(str(x[0].date()))
    
    if ylim:
        plt.ylim(ylim)
    else:
        plt.ylim([min(y) - (max(y) - min(y) ) * 0.05, 
                  max(y) + (max(y) - min(y) ) * 0.05])
    
    return plt, ax

def plot_one_week(x, y, xlabel=None, ylabel=None, title=None, ylim=None):
    """时间跨度为一周。
    
    major tick = every days
    minor tick = every 3 hours
    """
    plt.close("all")
    
    fig = plt.figure(figsize=(20, 10))
    ax = fig.add_subplot(111)
    ax.plot(x, y)
    
    days = DayLocator(range(365))
    daysFmt = DateFormatter("%Y-%m-%d")
    hours = HourLocator([3, 6, 9, 12, 15, 18, 21])
    hoursFmt = DateFormatter("%H:%M")
    
    ax.xaxis.set_major_locator(days)
    ax.xaxis.set_major_formatter(daysFmt)
    ax.xaxis.set_minor_locator(hours)
    ax.xaxis.set_minor_formatter(hoursFmt)
    
    ax.autoscale_view()
    ax.grid()
    plt.setp( ax.xaxis.get_majorticklabels(), rotation=90 )
    plt.setp( ax.xaxis.get_minorticklabels(), rotation=90 )
    
    if xlabel:
        plt.xlabel(xlabel)
    else:
        plt.xlabel("Time")
        
    if ylabel:
        plt.ylabel(ylabel)
    else:
        plt.ylabel("Value")
    
    if title:
        plt.title(title)
    else:
        plt.title("%s to %s" % (str(x[0]), str(x[-1]) ) )

    if ylim:
        plt.ylim(ylim)
    else:
        plt.ylim([min(y) - (max(y) - min(y) ) * 0.05, 
                  max(y) + (max(y) - min(y) ) * 0.05])
    
    return plt, ax

def plot_one_month(x, y, xlabel=None, ylabel=None, title=None, ylim=None):
    """时间跨度为一月。
    
    major tick = every days
    """
    plt.close("all")
    
    fig = plt.figure(figsize=(20, 10))
    ax = fig.add_subplot(111)
    ax.plot(x, y)
    

    days = DayLocator(range(365))
    daysFmt = DateFormatter("%Y-%m-%d")
    
    ax.xaxis.set_major_locator(days)
    ax.xaxis.set_major_formatter(daysFmt)
    
    ax.autoscale_view()
    ax.grid()
    plt.setp( ax.xaxis.get_majorticklabels(), rotation=90 )
    
    if xlabel:
        plt.xlabel(xlabel)
    else:
        plt.xlabel("Time")
        
    if ylabel:
        plt.ylabel(ylabel)
    else:
        plt.ylabel("Value")
    
    if title:
        plt.title(title)
    else:
        plt.title("%s to %s" % (str(x[0]), str(x[-1]) ) )

    if ylim:
        plt.ylim(ylim)
    else:
        plt.ylim([min(y) - (max(y) - min(y) ) * 0.05, 
                  max(y) + (max(y) - min(y) ) * 0.05])
    
    return plt, ax

def plot_one_quarter(x, y, xlabel=None, ylabel=None, title=None, ylim=None):
    """时间跨度为一年。
    
    major tick = every months
    minor tick = every 15th day in a month
    """
    plt.close("all")
    
    fig = plt.figure(figsize=(20, 10))
    ax = fig.add_subplot(111)
    ax.plot(x, y)
    
    months = MonthLocator(range(12))
    monthsFmt = DateFormatter("%Y-%m")
    days = DayLocator([7, 14, 21, 28])
    daysFmt = DateFormatter("%dth")
    
    ax.xaxis.set_major_locator(months)
    ax.xaxis.set_major_formatter(monthsFmt)
    ax.xaxis.set_minor_locator(days)
    ax.xaxis.set_minor_formatter(daysFmt)
    
    ax.autoscale_view()
    ax.grid()
    plt.setp( ax.xaxis.get_majorticklabels(), rotation=90 )
    plt.setp( ax.xaxis.get_minorticklabels(), rotation=90 )
    
    if xlabel:
        plt.xlabel(xlabel)
    else:
        plt.xlabel("Time")
        
    if ylabel:
        plt.ylabel(ylabel)
    else:
        plt.ylabel("Value")
    
    if title:
        plt.title(title)
    else:
        plt.title("%s to %s" % (str(x[0]), str(x[-1]) ) )

    if ylim:
        plt.ylim(ylim)
    else:
        plt.ylim([min(y) - (max(y) - min(y) ) * 0.05, 
                  max(y) + (max(y) - min(y) ) * 0.05])
    
    return plt, ax

def plot_one_year(x, y, xlabel=None, ylabel=None, title=None, ylim=None):
    """时间跨度为一年
    
    major tick = every months
    minor tick = every 15th day in a month
    """
    plt.close("all")
    
    fig = plt.figure(figsize=(20, 10))
    ax = fig.add_subplot(111)
    ax.plot(x, y)
    
    months = MonthLocator(range(1, 13))
    monthsFmt = DateFormatter("%Y-%m")
    days = DayLocator([15])
    daysFmt = DateFormatter("%m-%d")
    
    ax.xaxis.set_major_locator(months)
    ax.xaxis.set_major_formatter(monthsFmt)
    ax.xaxis.set_minor_locator(days)
    ax.xaxis.set_minor_formatter(daysFmt)
    
    ax.autoscale_view()
    ax.grid()
    plt.setp( ax.xaxis.get_majorticklabels(), rotation=90 )
    plt.setp( ax.xaxis.get_minorticklabels(), rotation=90 )
    
    if xlabel:
        plt.xlabel(xlabel)
    else:
        plt.xlabel("Time")
        
    if ylabel:
        plt.ylabel(ylabel)
    else:
        plt.ylabel("Value")
    
    if title:
        plt.title(title)
    else:
        plt.title("%s to %s" % (str(x[0]), str(x[-1]) ) )

    if ylim:
        plt.ylim(ylim)
    else:
        plt.ylim([min(y) - (max(y) - min(y) ) * 0.05, 
                  max(y) + (max(y) - min(y) ) * 0.05])
    
    return plt, ax

def visualize(x, y, xlabel=None, ylabel=None, title=None, ylim=None):
    """A universal function plot arbitrary time series data.
    """
    total_seconds = (x[-1] - x[0]).total_seconds()
    if total_seconds <= 86400 * 1 * 3:
        return plot_one_day(x, y, xlabel, ylabel, title, ylim)
    
    elif total_seconds <= 86400 * 7 * 2:
        return plot_one_week(x, y, xlabel, ylabel, title, ylim)
    
    elif total_seconds <= 86400 * 30 * 1.5:
        return plot_one_month(x, y, xlabel, ylabel, title, ylim)
    
    elif total_seconds <= 86400 * 90 * 1.5:
        return plot_one_quarter(x, y, xlabel, ylabel, title, ylim)
    
    elif total_seconds <= 86400 * 365 * 1.5:
        return plot_one_year(x, y, xlabel, ylabel, title, ylim)

#-----------------------------------------------------------------------------#
#                                  Unittest                                   #
#-----------------------------------------------------------------------------#

if __name__ == "__main__":
    import pandas as pd, numpy as np
    
    x_day = pd.date_range(start="2014-01-01 00:00:00",
                          end="2014-01-02 00:00:00",
                          freq="15min")
    x_week = pd.date_range(start="2014-01-01 00:00:00",
                           end="2014-01-08 00:00:00",
                           freq="1H")
    x_month = pd.date_range(start="2014-01-01 00:00:00",
                            end="2014-02-01 00:00:00",
                            freq="1H")
    x_quarter = pd.date_range(start="2014-01-01 00:00:00",
                              end="2014-04-01 00:00:00",
                              freq="D")
    x_year = pd.date_range(start="2014-01-01 00:00:00",
                           end="2015-01-01 00:00:00",
                           freq="D")
    
    def unittest_plot_any():
        for x in [x_day, x_week, x_month, x_quarter, x_year]:
            y = np.random.rand(len(x))
            plt, ax = visualize(x, y)
            plt.show()
    
    unittest_plot_any()
    
    def unittest_plot_one_day():
        x = x_day
        y = np.random.rand(len(x))
        plt, ax = plot_one_day(x, np.random.rand(len(x)))
        plt.show()
        
#     unittest_plot_one_day()
    
    def unittest_plot_one_week():
        x = x_week
        y = np.random.rand(len(x))
        plt, ax = plot_one_week(x, np.random.rand(len(x)))
        plt.show()
        
#     unittest_plot_one_week()
    
    def unittest_plot_one_month():
        x = x_month
        y = np.random.rand(len(x))
        plt, ax = plot_one_month(x, np.random.rand(len(x)))
        plt.show()
        
#     unittest_plot_one_month()

    def unittest_plot_one_quarter():
        x = x_quarter
        y = np.random.rand(len(x))
        plt, ax = plot_one_quarter(x, np.random.rand(len(x)))
        plt.show()
        
#     unittest_plot_one_quarter()
    
    def unittest_plot_one_year():
        x = x_year
        y = np.random.rand(len(x))
        plt, ax = plot_one_year(x, np.random.rand(len(x)))
        plt.show()
        
#     unittest_plot_one_year()