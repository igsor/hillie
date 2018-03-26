"""Edit annotations in PDF files.

Go through and review or edit notes in PDF files.

Copyright (c) 2016, Matthias Baumgartner
All rights reserved.

"""
# exports
__all__ = ('anedit', 'anedit_multi', 'main')

# imports
from basics import VERSION
from hilliep import VALID_TYPES
from normalizer import Dictionary, annotation_fixes
from pdf import Pdf
import os
import os.path
import readline
import sys


## code ##

def anedit_multi(files, options):
    """Edit annotations of mutliple files.

    All is printed to standard input or standard error.

    Options:
    * options.recursive     Handle directories
    * options.suffix        Write changes to a file with suffix appended to original filename

    """
    for path in files:
        if os.path.isdir(path):
            if options.recursive:
                anedit_multi([os.path.join(path, p) for p in os.listdir(path)], options)
            continue

        target = path
        if options.suffix is not None:
            target = path + options.suffix

        anedit(path, target, options)


def anedit(path, target, options):
    """Edit notes from highlights in PDF files.

    All is printed to standard input or standard error.

    Options:
    * options.valid_types   PDF annotation types to process
    * options.use_title     Print filename/document title instead of filename
    * options.filter_keys   Only print stated keys.
    * options.remove_key    Don't print key tags
    * options.verbose       Print varnings

    """
    # FIXME: Who guarantees this method is only executed on valid files?
    # Also check for pusher, hillieo, hilliep, ...

    # wordlist for normalization
    wordlist = Dictionary()

    # open document
    document = Pdf(path, options, pgm=sys.argv[0])

    # fetch notes
    notes = []
    for n_annot, item in enumerate(document.annotations(options)):
        sugg = annotation_fixes(item.note, wordlist, options.verbose)
        notes.append((item, sugg))

    # Walk through notes
    has_changes = False
    while len(notes) > 0:
        item, sugg = notes.pop(0)

        print ""
        print "\033[94m> {}: page {}, ETA {}\033[0m".format(item.page[0], item.page[1], len(notes))
        print "Original: ", item.note
        if item.note != sugg:
            print "Suggested:", sugg
        elif options.diffs:
            continue

        valid_answers = 'nyecisq?'
        prompt = '[{}]: '.format('/'.join(valid_answers.title()))
        ans = 'NEIN'
        while ans not in valid_answers:
            ans = raw_input(prompt) \
                .strip() \
                .lower() \
                .replace('yes', 'y') \
                .replace('no', 'n') \
                .replace('quit', 'q') \
                .replace('ignore', 'i') \
                .replace('ign', 'i') \
                .replace('edit', 'e') \
                .replace('correct', 'c') \
                .replace('skip', 's')

            if ans == '':
                ans = valid_answers[0] # default is 'n'

            if ans == '?':
                ans = 'NEIN'
                print '''Usage:

    n   no      Stick with the original text (the default)
    y   yes     Accept the suggested text
    e   edit    Edit the original text
    c   change  Edit the suggested text
    i   ignore  Ignore for now (again prompted later)
    s   skip    Save and exit
    q   quit    Abort and exit (changes are lost)

                '''

        if ans == 'y': # Use suggestion
            has_changes = True
            if item.key is None:
                item.set_content(sugg)
            else:
                item.set_content('<{}>{}</{}>'.format(item.key, sugg, item.key))
        elif ans == 'n': # Use original
            pass
        elif ans in ('e', 'c'): # Edit manually
            def hook():
                curr = ans == 'e' and item.note or sugg
                curr = curr.replace('\n', '\\n')
                readline.insert_text(curr)
                readline.redisplay()

            readline.set_pre_input_hook(hook)
            sugg = raw_input().strip().replace('\\n', '\n')
            readline.set_pre_input_hook(None)
            notes.insert(0, (item, sugg))
        elif ans == 'i': # Ignore note for now
            notes.append((item, sugg))
        elif ans == 'q': # Quit immediately, don't save
            return
        elif ans == 's': # Skip the rest
            break

    # save changes
    if has_changes:
        document.save(target, options)

def main():
    """Edit text notes from highlighted ares in PDF documents.

    usage: anedit [--help] [--version] [-s] [-k FILTER_KEYS] [-t] [-a VALID_TYPES]
                  [-d] [--suffix SUFFIX] [-r] [-v]
                  ...

    Edit text notes from highlighted ares in PDF documents.

    positional arguments:
      paths                 List of files or directories to be processed

    optional arguments:
      --help                show this help message and exit
      --version             show program's version number and exit
      -s, --show-key        Do print xml-style keys.
      -k FILTER_KEYS, --key FILTER_KEYS
                            Show only listed keys. Use "None" for empty/no key
      -t, --use-title       Print document title instead of path.
      -a VALID_TYPES, --annotation-type VALID_TYPES
                            Extracted annotation types
      -d, --only-diff       Only prompt lines with a distinct suggestion
      --suffix SUFFIX       Store modifications in a file with the given suffix
      -r, --recursive       Read all files under each directory, recursively.
      -v, --verbose         Increase verbosity

    """
    import argparse

    usage = """Edit text notes from highlighted ares in PDF documents."""
    parser = argparse.ArgumentParser(description=usage, add_help=False)

    parser.add_argument('--help', action='help', help='show this help message and exit')
    parser.add_argument('--version', action='version', version='%(prog)s {}'.format(VERSION))
    parser.add_argument('-s', '--show-key', action='store_false', dest='remove_key', default=True, help='Do print xml-style keys.')
    parser.add_argument('-k', '--key', action='append', dest='filter_keys', default=[], help='Show only listed keys. Use "None" for empty/no key')
    parser.add_argument('-t', '--use-title', action='store_true', dest='use_title', default=False, help='Print document title instead of path.')
    parser.add_argument('-a', '--annotation-type', action='append', dest='valid_types', default=[], help='Extracted annotation types')
    parser.add_argument('-d', '--only-diff', action='store_true', dest='diffs', default=False, help='Only prompt lines with a distinct suggestion')
    parser.add_argument('--suffix', dest='suffix', default=None, help='Store modifications in a file with the given suffix')
    parser.add_argument('-r', '--recursive', action='store_true', dest='recursive', default=False, help='Read all files under each directory, recursively.')
    parser.add_argument('-v', '--verbose', action='store_true', dest='verbose', default=False, help='Increase verbosity')

    parser.add_argument('paths', nargs=argparse.REMAINDER, help='List of files or directories to be processed')
    args = parser.parse_args()
    if len(args.valid_types) == 0: # Default annotation types if none given.
        args.valid_types = VALID_TYPES

    # Allow comma-seperated keys/types and ensure lower case
    args.filter_keys = reduce(list.__add__, [map(str.lower, map(str.strip, arg.split(','))) for arg in args.filter_keys], [])
    args.valid_types = reduce(list.__add__, [map(str.lower, map(str.strip, arg.split(','))) for arg in args.valid_types], [])

    # Run highlighter
    anedit_multi(args.paths, args)


## EOF ##
