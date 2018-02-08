"""Shared methods.

Copyright (c) 2018, Matthias Baumgartner
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
# exports
__all__ = ('print_note', )

# imports
from basics import RX_KEY
import sys


## code ##

def print_note(path, note, page_no, options):
    if options.list_keys : # Print keys
        m = RX_KEY.match(note)
        key = m is not None and m.groups()[0].strip().lower() or 'none'
        sys.stdout.write(key + '\n')
        if not options.buffered:
            sys.stdout.flush()

        return # Don't print the note

    if len(options.filter_keys): # Filter
        m = RX_KEY.match(note)
        if m is not None:
            key = m.groups()[0].strip().lower()
            if key not in options.filter_keys: # Abort
                return
        elif 'none' not in options.filter_keys: # Abort
            return

    if options.remove_key: # Remove key
        m = RX_KEY.match(note)
        if m is not None:
            note = m.groups()[1]

    if note is not None and note != '':
        line = '' # Init empty

        if options.with_path: # Path
            line += '{}:'.format(path)

        if options.with_page: # Page No
            line += '{}:'.format(page_no)

        line += ' ' + note # Note

        # Write the note
        sys.stdout.write(line.strip() + '\n')
        if not options.buffered:
            sys.stdout.flush()

## EOF ##
