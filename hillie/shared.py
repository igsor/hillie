"""Shared methods.

Copyright (c) 2018, Matthias Baumgartner
All rights reserved.

"""
# exports
__all__ = ('Document', 'Annotation', 'print_note', 'list_keys', 'filter_note', 'backup_file')

# imports
from basics import RX_KEY
import shutil
import unicodedata


## code ##

class Document(object):
    def annotations(self, options):
        abstract()
    def save(self, target, options):
        abstract()

class Annotation(object):
    def set_content(self, note):
        abstract()
    def set_type(self, type_):
        abstract()
    def set_color(self, color):
        abstract()

def filter_note(note, options):
    """Process *note* text following config in *options*.
    """
    # encoding
    #note =  unicodedata.normalize('NFKD', note.decode('utf-8', 'ignore')).encode('ascii', 'ignore').strip()

    if len(options.filter_keys): # Filter
        m = RX_KEY.match(note)
        if m is not None:
            key = m.groups()[0].strip().lower()
            if key not in options.filter_keys: # Abort
                return None
        elif 'none' not in options.filter_keys: # Abort
            return None

    if options.remove_key: # Remove key
        m = RX_KEY.match(note)
        if m is not None:
            note = m.groups()[1]

    if note is None or note == '':
        return None

    return note

def print_note(note, (title, page_no), options):
    """Prints a *note* following config in *options*.
    """
    if note is not None and note != '':
        line = '' # Init empty

        if options.with_path: # Path
            line += '{}:'.format(title)

        if options.with_page: # Page No
            line += '{}:'.format(page_no)

        line += ' ' + note # Note

        # Write the note
        line = line.strip()
        if options.newline: line += '\n'
        options.stdout.write(line + '\n')
        if not options.buffered:
            options.stdout.flush()

def list_keys(note, options):
    """Print key from note.
    """
    m = RX_KEY.match(note)
    key = m is not None and m.groups()[0].strip().lower() or 'none'
    options.stdout.write(key + '\n')
    if not options.buffered:
        options.stdout.flush()

def backup_file(src, op=shutil.copy):
    """Create a backup of file at *src*.

    The backup is created either by copying (op=shutil.copy, the default)
    or moving (op=os.rename).

    """
    cnt = 0
    while True: # Find non-existing backup path
        trg = "{}-{}--{:04d}".format(src, datetime.datetime.now().date().isoformat(), cnt)
        if not pexists(trg): break
        cnt += 1

    op(src, trg) # backup


## EOF ##
