"""Generic helper functions and configuration

Copyright (c) 2016, Matthias Baumgartner
All rights reserved.

"""
# EXPORTS
__all__ = ('RX_KEY', 'VERSION', 'uniquepath', 'remove_all', 'unique')

# IMPORTS
import os.path
import re

## CONFIGURATION ##

RX_KEY = re.compile('<(.*?)>\s*(.*)\s*</\\1>', re.I)
VERSION = 1.0

## CODE ##

def uniquepath(path):
    """Return a normalized path."""
    if path is None or path == '':
        return path

    return os.path.realpath(
           os.path.abspath(
           os.path.normpath(
           os.path.expandvars(
           os.path.expanduser(
               path
           )))))

def remove_all(lst, item):
    """Remove all occurences of *item* in *lst*."""
    while item in lst:
        lst.remove(item)
    return lst

unique = lambda s: list(set(s))


## EOF ##
