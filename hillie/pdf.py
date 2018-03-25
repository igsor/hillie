"""Extract and manipulate annotations in PDF files.

Copyright (c) 2018, Matthias Baumgartner
All rights reserved.

"""
# exports
__all__ = ('Pdf', )

# imports
from basics import uniquepath
from shared import Document, Annotation, filter_note
import glib
import os.path
import poppler
import urllib


## code ##

class Pdf(Document):
    """Extract and manipulate annotations in PDF files.
    """

    class Item(Annotation):
        def __init__(self, client, note, page):
            self.note = note
            self.page = page
            self._annot = client
        def set_content(self, note):
            if self._annot is not None:
                self._annot.set_contents(note)
        def set_type(self, type_):
            pass
        def set_color(self, color):
            pass

    def __init__(self, path, options, pgm=''):
        self.pgm = pgm
        self.path = path
        url = 'file://{}'.format(urllib.pathname2url(uniquepath(path)))
        self.document = poppler.document_new_from_file(url, None)

    def annotations(self, options):
        """Read annotations from a PDF file.
        """
        try:
            title = self.path
            if options.use_title:
                embed = self.document.get_property('title')
                if title is not None and title != '': # Pick embedded title
                    title = embed
                else: # Pick filename w/o extension instead
                    title = os.path.basename(self.path)
                    title, ext = os.path.splitext(title)

            for i in range(self.document.get_n_pages()):
                page = self.document.get_page(i)
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

                            note = filter_note(note, options)
                            if note is not None:
                                page_no = str(page.get_index() + 1)
                                yield Pdf.Item(annot, note, (title, page_no))

        except glib.GError as err:
            msg = '{}: {}: {}\n'.format(self.pgm, self.path, err.message)
            options.stderr.write(msg)
            if not options.buffered:
                options.stderr.flush()

    def save(self, target, options): # FIXME
        """
        """
        # Due to lack of documentation, I don't know how to save a file in-place
        # So now, in all case, the result is stored to a temporary file, then
        # moved to the destination, possibly overwriting the original file.
        fh, tfile = tempfile.mkstemp()
        url = 'file://{}'.format(urllib.pathname2url(uniquepath(tfile)))
        document.save(url)

        # FIXME: Support backup original

        # ask overwrite
        ans = 'NEIN'
        while ans not in ('y', 'n'):
            ans = raw_input('Overwrite {}? [y/n] '.format(target)).strip().lower()

        if ans == 'y':
            os.rename(tfile, target) # Move to destination
        else:
            # ask removal of temp
            ans = 'NEIN'
            while ans not in ('y', 'n'):
                ans = raw_input('Delete {}? [y/n] '.format(tfile)).strip().lower()

            if ans == 'y':
                os.unlink(tfile)

## EOF ##
