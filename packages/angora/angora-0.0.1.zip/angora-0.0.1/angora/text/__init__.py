#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .formatter import fmt_title, fmt_sentence, fmt_name
from .rnd import (rand_str, rand_pwd, rand_phone, rand_ssn, rand_email, 
    rand_article)
from .rerecipe import ReParser as reparser
from .strtemplate import StrTemplate as strtpl