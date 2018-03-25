"""Extract and manipulate annotations in Okular files.

Copyright (c) 2018, Matthias Baumgartner
All rights reserved.

"""
# exports
__all__ = ('Okular', )

# imports
from basics import uniquepath
from lxml import objectify
from shared import Document, Annotation, filter_note, backup_file
import lxml
import os.path
import re
import sys


## code ##

class Okular(Document):
    """Extract and manipulate annotations in Okular files.
    """

    class Item(Annotation):
        def __init__(self, client, note, key, page):
            self.note = note
            self.key = key
            self.page = page
            self._base = client
            self._hl = client is not None and self._base.find('hl') or None
        def set_content(self, note):
            if self._base is not None:
                self._base.set('contents', note)
        def set_type(self, type_):
            if self._hl is not None:
                self._hl.set('type', type_)
        def set_color(self, color):
            if self._base is not None:
                self._base.set('color', type_)

    def __init__(self, path, options, pgm=''):
        self.pgm = pgm

        # make and store path
        if not uniquepath(path).startswith(uniquepath(options.okular)):
            prefix = os.stat(path).st_size
            filename = os.path.basename(path)
            path = os.path.join(options.okular, "{}.{}.{}".format(prefix, filename, 'xml'))
        self.path = path

        # open document
        with open(uniquepath(self.path)) as ifile:
            self.root = objectify.fromstring(ifile.read())


    def annotations(self, options):
        """Read annotations from okular's temporary annotation storage.
        If *path* is not an okular xml file, the right file is searched
        and its annotations printed. This mimicks the behaviour one would
        expect from Okular.

        """
        try:
            title = self.path
            if options.use_title:
                m = re.search('^\d+\.(.*)\.xml$', self.path, re.I)
                if m is not None:
                    title = m.groups()[0]
                    title, ext = os.path.splitext(title)

            for page in self.root.pageList.page:
                if not hasattr(page, 'annotationList') or \
                   not hasattr(page.annotationList, 'annotation'):
                    continue # Page has no annotation

                for annot in page.annotationList.annotation:
                    if annot.get('type', '-1') in options.valid_types:
                        base = annot.find('base')
                        if base is None: continue # Annotation has no content

                        note = base.get('contents', '').strip()
                        if note == '': continue # Annotation has no content

                        note, key = filter_note(note, options)
                        if note is not None:
                            page_no = page.get('number', -1)
                            yield Okular.Item(base, note, key, (title, page_no))

        except IOError, err: # Abort on failure
            msg = '{}: {}: {}\n'.format(self.pgm, self.path, err.message)
            options.stderr.write(msg)
            if not options.buffered:
                options.stderr.flush()

        except lxml.etree.XMLSyntaxError, err: # Abort on failure
            msg = '{}: {}: {}\n'.format(self.pgm, self.path, err.message)
            options.stderr.write(msg)
            if not options.buffered:
                options.stderr.flush()

        except UnicodeEncodeError, err: # Abort on failure
            msg = '{}: {}: {}\n'.format(self.pgm, self.path, err.message)
            options.stderr.write(msg)
            if not options.buffered:
                options.stderr.flush()

        except AttributeError, err: # Document has no annotations
            msg = '{}: {}: {}\n'.format(self.pgm, self.path, err.message)
            options.stderr.write(msg)
            if not options.buffered:
                options.stderr.flush()

    def save(self, target, options):
        """
        """
        # backup original
        backup_file(self.path, op=os.rename) # FIXME: Consider options

        # overwrite original
        with open(target, 'w') as ofile:
            etree.ElementTree(document).write(ofile, pretty_print=True)

## EOF ##
