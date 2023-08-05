#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module description
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module provides a easy way to create your 1-D function data. Simple draw
your wave form, and the :func:`img2wav()<img2wav>` will convert that for you.

Another interesting function is :func:`img2ascii()<img2ascii>`. This function
generate ascii art from image. Plus, here is a free web service can do the same 
things: http://picascii.com/.


Compatibility
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- Python2: Yes
- Python3: Yes


Prerequisites
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- `PIL (pillow) <https://python-pillow.github.io/>`_
- `numpy <http://www.numpy.org/>`_


Class, method, function, exception
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from __future__ import print_function
try:
    from PIL import Image
except ImportError as e:
    print("[Failed to do 'from PIL import Image', "
          "pleasee install pillow]: %s" % e)
try:
    import numpy as np
except ImportError as e:
    print("[Failed to do 'import numpy', "
          "please install numpy]: %s" % e)

def expand_window(center, window_size, array_size):
    """Generate a bounded windows. 
    
    maxlength = 2 * window_size + 1, lower bound is 0 and upper bound is 
    ``array_size - 1``.
    
    Example::
    
        >>> expand_window(center=50, window_size=3, max=100)
        [47, 48, 49, 50, 51, 52, 53]
        
        >>> expand_window(center=2, window_size=3, max=100)
        [0, 1, 2, 3, 4, 5]
        
        >>> expand_window(center=98, window_size=3, max=100)
        [95, 96, 97, 98, 99]
    """
    if center - window_size < 0:
        lower = 0
    else:
        lower = center - window_size
    if center + window_size + 1 > array_size:
        upper = array_size
    else:
        upper = center + window_size + 1
    return np.array(range(lower, upper))

def img2ascii(img_path, ascii_path, ascii_char="*", pad=0):
    """Convert an image to ascii art text.
    
    Suppose we have an image like that:
    
    .. image:: images/rabbit.png
        :align: left
        
    Put some codes::
    
        >>> from weatherlab.math.img2waveform import img2ascii
        >>> img2ascii(r"testdata\img2waveform\rabbit.png", 
        ...           r"testdata\img2waveform\asciiart.txt", pad=0)
    
    Then you will see this in asciiart.txt::
                                
                                             
                               ******                                                   
                              ***  ***                         ****                     
                             **      **                     *********                   
                            **        **                   ***     ***                  
                           **          *                  **         **                 
                           **          **                **          **                 
                          **            *               ***           *                 
                          *             **              **            **                
                         **              *             **             **                
                         **              *             **              *                
                         *               **           **               *                
                        **               **           *                **               
                        **                *          **                **               
                        *                 *          **                **               
                        *                 **         *                 **               
                       **                 **        **                 **               
                       **                  *        **                 **               
                       **                  *        *                  **               
                       **                  *       **                   *               
                       **                  *       **                   *               
                       *                   **      **                   *               
                       *                   **      *                    *               
                       *                   **     **                    *               
                       *                   **     **                    *               
                       **                  **     **                   **               
                       **                   *     **                   **               
                       **                   *     *                    **               
                       **                   *     *                    **               
                       **                   *     *                    **               
                        *                   *    **                    **               
                        *                   *    **                    *                
                        **                  *    **                    *                
                        **                  *    **                    *                
                        **                  **   **                   **                
                         *                  **   **                   **                
                         *                  **   **                   **                
                         **                 **   **                   *                 
                         **                 **   **                  **                 
                          *                 **   **                  **                 
                          **                **   **                  *                  
                          **                *******                  *                  
                          **                *******                 **                  
                           **                                       **                  
                           **                                       *                   
                           **                                      **                   
                          ***                                      *                    
                        ****                                       ***                  
                      ***                                           ***                 
                     **                                              ****               
                    **                                                 ***              
                   **                                                   ***             
                  **                                                      **            
                 **                                                        **           
                 *                                                          **          
                **                                                           **         
               **                                                            **         
               **                                                             **        
              **                                                               **       
              **                                                               **       
             **                                                                 **      
             **                                                                 **      
             *                                                                   **     
             *                                                                   **     
            **                                                                    *     
            **                                                                    **    
            *                                                                     **    
            *                                                                     **    
           **                                                                      *    
           **                                                                      *    
           **                                                                      **   
           **                                                                      **   
           **                                                                      **   
           **                                                                      **   
           **            **                                                        **   
           **            ***                                      ***              **   
            *           ****                                      ****             **   
            *            ***                                      ****             **   
            **           **                                        **              *    
            **                                                                     *    
            **                                                                     *    
             *                                                                    **    
             **                                                                   **    
             **                                                                   *     
              *                                                                  **     
              **                                                                 **     
               **                                                               **      
               **                                                               *       
                **                                                             **       
                **                                                            **        
                 **                                                          **         
                  **                        ***  **                         **          
                   **                        ******                        ***          
                    ***                     ******                        **            
                     ***                     *  ***                     ***             
                       ***                                             ***              
                        ***                                          ***                
                          ****                                     ****                 
                         ********                                *******                
                        *** **********                       ******** ***               
                       **   ***  ************         ********** *** * ***              
                      **  * ****      ***********************   ***  ** ***             
                     ** *  ** ****  **       ******* *         *** ***** ***            
                    ****  *  * *****       **********      * **** *  * ** **            
                   ***  * * ** * ******************************* * ***   * **           
                   ** ***** * *** ********** **  ** **********   ***   **  ***          
                  ** * ***** **  *    *****  **  **   *****   * *  ** *     **          
                 ***  *** ************    ** ****** ** *    * ** ** ** * ** ***         
                 ** ******* *  * **    **  ** ****    *  ** *  **   * ****   **         
                ** *** *** ******* ****** * **   * *** ***** *** ** ***** **  **        
                ** * *  ***** ************************************ * ****  *  **        
               *** ** ** ***********************************************  *** ***       
                ***   ** ****************************************** **** ** ** **       
                ****  ** ** ******************************************** ** *  **       
               ** ****** ** ******************************************** ** *  ***      
               **  ***** *********************************************** **  ****       
               *     *** ****************************** **************** *********      
              **      **  *************************************** * * *  *****   *      
              **      ** **********************************************  ***     *      
               *      ** **  *********************************** ******* **      *      
               **     **  *****************************************  *** **      *      
                ***  ** * ********************************************** **     **      
                 ****** ************************************************ **   ***       
                   **** *********************************************** ********        
                     **  *********************************************** ****           
                     *** **  ******************************************* **             
                      *** ** ***** ****** * * * * *  ******** *** ** ** ***             
                       ***  *   * ****   ****  **** * ** **  * *** **  ***              
                        ****   * * ** **** * *** ********  *  ***   *****               
                         *****    ** **  ** **  ***  ** ***       *****                 
                           *******        * * ** * **        ********                   
                              *************** *   *******************                   
                               ******************************      ***                  
                              ***          *********                **                  
                              **                  *                  **                 
                             **                   *                  **                 
                             **                   *                  **                 
                             **                   *                  **                 
                             **                   *                  **                 
                             **                  **                 **                  
                              **                ****** *  ** *********                  
                               *************************************                    
                                  **********    
                                  
    :param img_path: the image file path
    :type img_path: str
    :param ascii_path: the output ascii text file path
    :type ascii_path: str
    :param pad: how many space been filled in between two pixels
    :type pad: int
    """
    if len(ascii_char) != 1:
        raise Exception("ascii_char has to be single character.")
    
    image = Image.open(img_path).convert("L")
    matrix = np.array(image)
    
    # you can customize the gray scale fix behavior to fit color image
    matrix[np.where(matrix >= 128)] = 255 
    matrix[np.where(matrix < 128)] = 0
    
    lines = list()
    for vector in matrix:
        line = list()
        for i in vector:
            line.append(" " * pad)
            if i:
                line.append(" ")
            else:
                line.append(ascii_char)
        lines.append("".join(line))
    
    with open(ascii_path, "w") as f:
        f.write("\n".join(lines))
    
def img2wav(path, min_x, max_x, min_y, max_y, window_size=3):
    """Generate 1-D data ``y=f(x)`` from a black/white image.
    
    Suppose we have an image like that:
    
    .. image:: images/waveform.png
        :align: center
    
    Put some codes::
        
        >>> from weatherlab.math.img2waveform import img2wav
        >>> import matplotlib.pyplot as plt
        >>> x, y = img2wav(r"testdata\img2waveform\waveform.png", 
        ...                  min_x=0.0, max_x=288, 
        ...                  min_y=15.0, max_y=35.0, 
        ...                  window_size=15)
        >>> plt.plot(x, y)
        >>> plt.show()
    
    Then you got nicely sampled data:
    
    .. image:: images\waveform_pyplot.png
        :align: center
    
    :param path: the image file path
    :type path: string
    :param min_x: minimum value of x axis
    :type min_x: number
    :param max_x: maximum value of x axis
    :type max_x: number
    :param min_y: minimum value of y axis
    :type min_y: number
    :param max_y: maximum value of y axis
    :type max_y: number
    :param window_size: the slide window
    :type window_size: int
    
    Note:
    
    In python, a numpy array that represent a image is from left to the right, 
    top to the bottom, but in coordinate, it's from bottom to the top. So we 
    use ::-1 for a reverse output
    """
    image = Image.open(path).convert("L")
    matrix = np.array(image)[::-1]
    
    # you can customize the gray scale fix behavior to fit color image
    matrix[np.where(matrix >= 128)] = 255 
    matrix[np.where(matrix < 128)] = 0
    
    tick_x = (max_x - min_x)/matrix.shape[1]
    tick_y = (max_y - min_y)/matrix.shape[0]
    
    x, y = list(), list()
    for i in range(matrix.shape[1]):
        window = expand_window( # slide margin window
            i, window_size, matrix.shape[1]) 
        margin_dots_y_indices = np.where(matrix[:, window] == 0)[0]
        if len(margin_dots_y_indices) > 0: # if found at least one dots in margin
            x.append(min_x + (i+1) * tick_x)
            y.append(min_y + margin_dots_y_indices.mean() * tick_y)
            
    return np.array(x), np.array(y)

#-----------------------------------------------------------------------------#
#                                  Unittest                                   #
#-----------------------------------------------------------------------------#

if __name__ == "__main__":
    from paintbrush.interp import linear_interpolate as resample
    from matplotlib import pyplot as plt
    import unittest
    
    def usage_example_img2ascii():
        img2ascii(r"testdata\img2waveform\rabbit.png", 
                  r"testdata\img2waveform\asciiart.txt", pad=1)
        
    usage_example_img2ascii()
    
    def usage_example_img2wav():
        x, y = img2wav(r"testdata\img2waveform\waveform.png", 
                         min_x=0.0, max_x=288, 
                         min_y=15.0, max_y=35.0, 
                         window_size=15)
        new_x = list(range(1, 288+1))
        new_y = resample(x, y, new_x)
        print(new_x)
        print(y)
        plt.plot(new_x, new_y)
        plt.show()
        
    usage_example_img2wav()

    class ParseImageUnittest(unittest.TestCase):
        def test_expand_window(self):
            self.assertListEqual(list(expand_window(3, 5, 20)),
                                 [0,1,2,3,4,5,6,7,8])
            self.assertListEqual(list(expand_window(18, 5, 20)),
                                 [13,14,15,16,17,18,19  ])
            self.assertListEqual(list(expand_window(10, 5, 20)),
                                 [5,6,7,8,9,10,11,12,13,14,15])
            
    unittest.main()