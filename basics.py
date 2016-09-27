"""Generic helper functions and configuration

Copyright (c) 2016, Matthias Baumgartner
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:

1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in
   the documentation and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors
   may be used to endorse or promote products derived from this software
   without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.

"""
# EXPORTS
__all__ = ('RX_KEY', 'VALID_TYPES', 'VERSION', 'uniquepath', 'remove_all', 'unique')

# IMPORTS
import os.path
import re

## CONFIGURATION ##

RX_KEY = re.compile('<(.*?)>\s*(.*)\s*</\\1>', re.I)
VALID_TYPES = ['highlight', 'underline', 'squiggly', 'strike-out']
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
