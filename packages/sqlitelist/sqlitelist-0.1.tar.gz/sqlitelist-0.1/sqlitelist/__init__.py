#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This code is distributed under the terms and conditions
# from the Apache License, Version 2.0
#
# http://opensource.org/licenses/apache2.0.php

"""
Wrapper around sqlite3 db, with a list-like interface.

Example of use:
import sqlitelist

with sqlitelist.open('mylist.db') as lst:
    lst.append('hello')
    lst.extend(['world', {'also': {'not', 'only', b'strings', ('are', ), 'supported}}])
    for item in lst:
        print(item)
"""

from .wrapper import open

__VERSION__ = VERSION = '0.1'
