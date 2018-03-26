"""Add tags from Okular annotation files to Zotero.

Written by Matthias Baumgartner, 2018

Copyright (c) 2018, Matthias Baumgartner
All rights reserved.

"""
# exports
__all__ = ('pusher', 'main')

# imports
from basics import uniquepath, VERSION
from okular import Okular
from os.path import basename, dirname, isdir
from os.path import exists as pexists
from os.path import join as pjoin
from shutil import copy
import cStringIO
import datetime
import magic
import os
import sqlite3

# config
ANSWER_DEFAULT = 'y' # y, n, q, s
VALID_TYPES = ['1', '4']
SUPPORTED_MIME_TYPES = ('application/pdf', )


## code ##

def pusher(conn, files, options):
    """Retrieves highlighted notes from documents (Okular temporary files)
    and stores it in the Zotero database as tag.

    Options:
    * options.recursive     Handle directories
    * options.valid_types   PDF annotation types to process
    * options.filter_keys   Only print stated keys.
    * options.ask           Ask before adding tag.

    """
    for path in files:
        if isdir(path):
            if options.recursive:
                if not pusher(conn, [pjoin(path, p) for p in os.listdir(path)], options):
                    return False # Abort
            continue # Omit directories

        if magic.from_file(path, mime=True) not in SUPPORTED_MIME_TYPES:
            # Ignore unknown file types
            continue

        print "\n== {} ==".format(basename(path))

        if uniquepath(path).startswith(uniquepath(options.storage)): # inside storage
            phandle = "storage:{}".format(basename(path))
            khandle = basename(dirname(path))
            itemID = conn.execute("""
                SELECT items.itemID
                FROM items
                JOIN itemAttachments ON itemAttachments.parentItemID = items.itemID
                WHERE itemAttachments.path = ?
                --AND   items.key = ?
                """,
                (phandle, ) #khandle)
                ).fetchone() # FIXME: What if filename is not unique?

        else: # outside storage
            itemID = conn.execute("""
                SELECT items.itemID
                FROM items
                JOIN itemAttachments ON itemAttachments.parentItemID = items.itemID
                WHERE itemAttachments.path = ?
                """,
                (uniquepath(path), )
                ).fetchone()

        if itemID is None:
            print "Item not found in Zotero"
            continue

        itemID = itemID[0]

        for item in Okular(path, options).annotations(options):
            # normalize text
            note = item.note.lower()

            # ask
            ans = options.ask and 'x' or 'y'
            while ans not in ('y', 'n', 'q', 's'):
                ans = raw_input("Add '{}' [Y/n/s/q]: ".format(note))
                ans = ans.strip().lower()[::1]
                ans = ans == '' and ANSWER_DEFAULT or ans

            if ans == 's': break # Continue with next file
            elif ans == 'q': return False # Abort
            elif ans == 'y': # Process
                if not options.ask: print "Adding '{}'".format(note)

                conn.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (note, ))
                conn.execute("""
                    INSERT OR IGNORE
                    INTO itemTags(itemID, tagID, type)
                    SELECT itemAttachments.parentItemID, tags.tagID, 0
                    FROM tags, itemAttachments
                    WHERE tags.name = ?
                    AND itemAttachments.parentItemID = ?
                    """,
                    (note, itemID)
                )

                # TODO: cleanup (remove unliked tags)

    conn.commit()
    return True

def main():
    """Store highlighted areas from Okular annotations in Zotero as tags.

    usage: pusher [--help] [--version] [-k FILTER_KEYS] [-r] [-a] [--backup]
                  [--annotation-type VALID_TYPES] [--okular OKULAR]
                  [--storage STORAGE] [--zotero ZOTERO]
                  ...

    Store highlighted areas from Okular annotations in Zotero as tags.

    positional arguments:
      paths                 Files to get tags from. If none given, all files in
                            the zotero storage are processed.

    optional arguments:
      --help                show this help message and exit
      --version             show program's version number and exit
      -k FILTER_KEYS, --key FILTER_KEYS
                            Show only listed keys. Use "None" for empty/no key
      -r, --recursive       Read all files under each directory, recursively.
      -a, --ask             Ask when adding tags
      --backup              Backup database before editing
      --annotation-type VALID_TYPES
                            Extracted annotation types
      --okular OKULAR       Okular annotation root
      --storage STORAGE     Zotero pdf storage
      --zotero ZOTERO       Zotero root

    """
    import argparse

    usage = """Store highlighted areas from Okular annotations in Zotero as tags."""
    parser = argparse.ArgumentParser(description=usage, add_help=False)

    parser.add_argument('--help', action='help', help='show this help message and exit')
    parser.add_argument('--version', action='version', version='%(prog)s {}'.format(VERSION))
    parser.add_argument('-k', '--key', action='append', dest='filter_keys', default=[], help='Show only listed keys. Use "None" for empty/no key')
    parser.add_argument('-r', '--recursive', action='store_true', dest='recursive', default=False, help='Read all files under each directory, recursively.')
    parser.add_argument('-a', '--ask', action='store_true', dest='ask', default=False, help='Ask when adding tags')
    parser.add_argument('--backup', action='store_true', dest='backup', default=False, help='Backup database before editing')
    parser.add_argument('--annotation-type', action='append', dest='valid_types', default=[], help='Extracted annotation types')
    parser.add_argument('--okular', default="~/.kde/share/apps/okular/docdata", help="Okular annotation root")
    parser.add_argument('--storage', default="~/.zotero/data/storage", help="Zotero pdf storage")
    parser.add_argument('--zotero', default="~/.zotero/data/zotero.sqlite", help="Zotero root")
    parser.add_argument('paths', nargs=argparse.REMAINDER, help="Files to get tags from. If none given, all files in the zotero storage are processed.")

    args = parser.parse_args()

    if len(args.valid_types) == 0: # Default annotation types if none given.
        args.valid_types = VALID_TYPES

    # Allow comma-seperated keys/types and ensure lower case
    args.filter_keys = reduce(list.__add__, [map(str.lower, map(str.strip, arg.split(','))) for arg in args.filter_keys], [])

    # Path checking
    args.okular  = uniquepath(args.okular)
    args.zotero  = uniquepath(args.zotero)
    args.storage = uniquepath(args.storage)
    assert pexists(args.zotero),  "Zotero database not found"
    assert pexists(args.okular),  "Okular root directory not found"
    assert pexists(args.storage), "Zotero pdf storage not found"

    if len(args.paths) == 0:
        # Default
        args.paths = [args.storage]
        args.recursive = True
        args.backup = True

    # default config
    args.list_keys  = False     # Doesn't make sense here
    args.buffered   = True      # Prevents flush for efficiency
    args.with_path  = False     # No prefix
    args.remove_key = True      # Tag is content only
    args.with_page  = False     # No prefix
    args.use_title  = False     # No prefix
    args.newline    = False     # No newlines
    args.stdout    = cStringIO.StringIO()
    args.stderr    = cStringIO.StringIO()

    # create backup
    if args.backup:
        rid = 0
        while True: # Find non-existing backup path
            bpath = "{}-{}--{:04d}".format(args.zotero, datetime.datetime.now().date().isoformat(), rid)
            if not pexists(bpath): break
            rid += 1

        copy(args.zotero, bpath) # backup


    # open database connection
    conn = sqlite3.connect(args.zotero)

    # Run highlighter
    pusher(conn, args.paths, args)

## EOF ##
