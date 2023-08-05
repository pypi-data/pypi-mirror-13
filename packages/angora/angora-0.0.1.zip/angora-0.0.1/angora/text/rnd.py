#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module description
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module provides some easy function to generate random text from built-in 
templates.

- :func:`rand_str`: fixed-length string
- :func:`rand_pwd`: random password
- :func:`rand_phone`: random phone number
- :func:`rand_ssn`: random ssn
- :func:`rand_email`: random email


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

import random
import string

def rand_str(allowed, length):
    """Generate fixed-length random string from your allowed character pool.
    
    Usage Example::
    
        >>> import string
        >>> randstr(string.ascii_letters + string.digits, 32)
        QE1UKzSrIw8z7EiEp94FJ3jwmuYNUw2N
    """
    if (not isinstance(length, int)) or (length <= 0):
        raise Exception("length parameter has to be an integer greater than 0!")
    
    res = list()
    for _ in range(length):
        res.append(random.choice(allowed))
    return "".join(res)

def rand_pwd(length):
    """Random Internet password.
    
    Usage Example::
    
        >>> rand_pwd(12)
        TlhM$^jzculH
    """
    return rand_str(
        string.ascii_letters + string.digits + r"""!@#$%^&*""", length)
    
def rand_phone():
    """Random US phone number. (10 digits)
    
    Usage Example::
    
        >>> rand_phone()
        (306)-746-6690
    """
    return "(%s)-%s-%s" % (rand_str(string.digits, 3),
                           rand_str(string.digits, 3),
                           rand_str(string.digits, 4))

def rand_ssn():
    """Random SSN. (9 digits)
    
    Usage Example::
    
        >>> rand_ssn()
        295-50-0178
    """
    return "%s-%s-%s" % (rand_str(string.digits, 3),
                         rand_str(string.digits, 2),
                         rand_str(string.digits, 4))

_all_email_kinds = [".com", ".net", ".org", ".edu"]

def rand_email():
    """Random email.

    Usage Example::
    
        >>> rand_email()
        Z4Lljcbdw7m@npa.net
    """
    name = random.choice(string.ascii_letters) + \
        rand_str(string.ascii_letters + string.digits, random.randint(4, 14)) 
    domain = rand_str(string.ascii_lowercase, random.randint(2, 10)) 
    kind = random.choice(_all_email_kinds)
    return "%s@%s%s" % (name, domain, kind)

def rand_article(num_p=(4, 10), num_s=(2, 15), num_w=(5, 40)):
    """Random article text.
    
    Usage Example::
        
        >>> rand_article()
        
    """
    article = list()
    for _ in range(random.randint(*num_p)):
        p = list()
        for _ in range(random.randint(*num_s)):
            s = list()
            for _ in range(random.randint(*num_w)):
                s.append(rand_str(string.ascii_lowercase, 
                                  random.randint(1, 15)))
            p.append(" ".join(s))
        article.append(". ".join(p))
    return "\n\n".join(article)

#-----------------------------------------------------------------------------#
#                                  Unittest                                   #
#-----------------------------------------------------------------------------#

if __name__ == "__main__":
    print(rand_str(string.ascii_letters + string.digits, 32))
    print(rand_pwd(12))
    print(rand_phone())
    print(rand_ssn())
    print(rand_email())
    print(rand_article())