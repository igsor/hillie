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
__all__ = ('annotations_from_okular', 'print_note')

# imports
from basics import RX_KEY, uniquepath
from lxml import objectify
import glib
import lxml
import os.path
import poppler
import re
import sys
import unicodedata
import urllib


## code ##

def annotations_from_pdf(path, options):
    """Read annotations from a PDF file.
    """
    notes = []
    try:
        url = 'file://{}'.format(urllib.pathname2url(uniquepath(path)))
        document = poppler.document_new_from_file(url, None)

        if options.use_title:
            title = document.get_property('title')
            if title is not None and title != '': # Pick embedded title
                path = title
            else: # Pick filename w/o extension instead
                path = os.path.basename(path)
                path, ext = os.path.splitext(path)

        for i in range(document.get_n_pages()):
            page = document.get_page(i)
            annot_mappings = page.get_annot_mapping()
            num_annots = len(annot_mappings)
            if num_annots > 0:
                for annot_mapping in annot_mappings:
                    annot = annot_mapping.annot
                    annot_type = annot.get_annot_type().value_nick
                    annot_type = annot_type[0].upper() + annot_type[1:]
                    if annot_type.lower() in options.valid_types:

                        note = annot.get_contents()
                        if note is None: continue
                        note = note.strip()

                        page_no = str(page.get_index() + 1)
                        note = print_note(path, note, page_no, options)
                        if note is not None: notes.append(note)

    except glib.GError as err:
        msg = '{}: {}: {}\n'.format(sys.argv[0], path, err.message)
        options.stderr.write(msg)
        if not options.buffered:
            options.stderr.flush()

    return notes

def annotations_from_okular(path, options):
    """Read annotations from okular's temporary annotation storage.
    If *path* is not an okular xml file, the right file is searched
    and its annotations printed. This mimicks the behaviour one would
    expect from Okular.

    """
    notes = []
    try:

        if not uniquepath(path).startswith(uniquepath(options.okular)):
            prefix = os.stat(path).st_size
            filename = os.path.basename(path)
            path = os.path.join(options.okular, "{}.{}.{}".format(prefix, filename, 'xml'))

        with open(uniquepath(path)) as ifile:
            root = objectify.fromstring(ifile.read())

        if options.use_title:
            m = re.search('^\d+\.(.*)\.xml$', path, re.I)
            if m is not None:
                path = m.groups()[0]
                path, ext = os.path.splitext(path)

        for page in root.pageList.page:
            if not hasattr(page, 'annotationList') or \
               not hasattr(page.annotationList, 'annotation'):
                continue # Page has no annotation

            for annot in page.annotationList.annotation:
                if annot.get('type', '-1') in options.valid_types:
                    base = annot.find('base')
                    if base is None: continue # Annotation has no content

                    note = base.get('contents', '').strip()
                    if note == '': continue # Annotation has no content

                    page_no = page.get('number', -1)
                    note = print_note(path, note, page_no, options)
                    if note is not None: notes.append(note)

    except IOError, err: # Abort on failure
        msg = '{}: {}: {}\n'.format(sys.argv[0], path, err.message)
        options.stderr.write(msg)
        if not options.buffered:
            options.stderr.flush()

    except lxml.etree.XMLSyntaxError, err: # Abort on failure
        msg = '{}: {}: {}\n'.format(sys.argv[0], path, err.message)
        options.stderr.write(msg)
        if not options.buffered:
            options.stderr.flush()

    except UnicodeEncodeError, err: # Abort on failure
        msg = '{}: {}: {}\n'.format(sys.argv[0], path, err.message)
        options.stderr.write(msg)
        if not options.buffered:
            options.stderr.flush()

    except AttributeError, err: # Document has no annotations
        msg = '{}: {}: {}\n'.format(sys.argv[0], path, err.message)
        options.stderr.write(msg)
        if not options.buffered:
            options.stderr.flush()

        pass

    return notes


def print_note(path, note, page_no, options):
    # encoding
    #note =  unicodedata.normalize('NFKD', note.decode('utf-8', 'ignore')).encode('ascii', 'ignore').strip()

    if options.list_keys : # Print keys
        m = RX_KEY.match(note)
        key = m is not None and m.groups()[0].strip().lower() or 'none'
        options.stdout.write(key + '\n')
        if not options.buffered:
            options.stdout.flush()

        return None # Don't print the note

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

    if note is not None and note != '':
        line = '' # Init empty

        if options.with_path: # Path
            line += '{}:'.format(path)

        if options.with_page: # Page No
            line += '{}:'.format(page_no)

        line += ' ' + note # Note

        # Write the note
        line = line.strip()
        options.stdout.write(line + '\n')
        if not options.buffered:
            options.stdout.flush()

        return line

## EOF ##
