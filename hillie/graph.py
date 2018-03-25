#!/usr/bin/env python
"""Graph helpers.

Handle the interface to a graph storage. Assist tools in pulling information from PDFs.

Copyright (c) 2016, Matthias Baumgartner
All rights reserved.

"""
# EXPORTS
__all__ = ('Graph', 'Notes')

# IMPORTS
import urllib
import poppler
from basics import VALID_TYPES, RX_KEY, uniquepath


## CODE ##

class Graph(object):
    def __init__(self, path):
        from nowhere.shell.notebook import Notebook
        from nowhere.frontend.dummy import Renderer_Dummy
        self.shell = Notebook(Renderer_Dummy(), {})
        self.graph = self.shell.open(path)

    def add_node(self, label):
        self.graph.node(label)

    def add_edge(self, src, dst, key, directed=True):
        self.graph.node(dst).node(src).key(key, directed=directed).connect()

    def save(self):
        self.graph.save()

    def connected(src, dst, key):
        return len(self.graph.edges(src=src, dst=dst, key=key)) > 0

    def __del__(self):
        if self.shell is not None:
            try:
                self.shell.close(self.graph)
            except Exception:
                pass

class Notes(object):
    def __init__(self, path):
        url = 'file://{}'.format(urllib.pathname2url(uniquepath(path)))
        self.document = poppler.document_new_from_file(url, None)
        self.valid_types = VALID_TYPES
        self.path = path

    def authors(self):
        return self._walk_document('author')

    def title(self):
        return self._walk_document('title').next()

    def why(self):
        return self._walk_document('why')

    def what(self):
        return self._walk_document('what')

    def how(self):
        return self._walk_document('how')

    def keyword(self):
        return self._walk_document('key')

    def literature(self):
        return self._walk_document('ref')

    def _walk_document(self, key):
        for i in range(self.document.get_n_pages()):
            for annot_mapping in self.document.get_page(i).get_annot_mapping():
                annot = annot_mapping.annot
                annot_type = annot.get_annot_type().value_nick
                annot_type = annot_type[0].upper() + annot_type[1:]
                if annot_type.lower() in self.valid_types:

                    note = annot.get_contents().strip()

                    m = RX_KEY.match(note)
                    if m is not None:
                        ekey, note = m.groups()
                    else:
                        ekey, note = None, note

                    if key == ekey and note is not None and note != '':
                        yield note

## EOF ##
