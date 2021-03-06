"""Print notes okular annotation files.

Written by Matthias Baumgartner, 2018

Copyright (c) 2016, Matthias Baumgartner
All rights reserved.

"""
# exports
__all__ = ('okular_highlights', 'main')

# imports
from basics import uniquepath, VERSION
from okular import Okular
from shared import list_keys, print_note
import os.path
import sys

# config
VALID_TYPES = ['1', '4']


## code ##

def okular_highlights(files, options):
    """Print notes from okular annotation files.

    All is printed to output or error stream (usually stdout and stderr).

    Options:
    * options.recursive     Handle directories
    * options.use_title     Print filename/document title instead of full path
    * options.valid_types   PDF annotation types to process
    * options.filter_keys   Only print stated keys.
    * options.remove_key    Don't print key tags
    * options.with_path     Print the file path with each line
    * options.with_page     Print the page number with each line
    * options.buffered      Buffer output
    * options.list_keys     Print key only
    * options.stdout        Output stream
    * options.stderr        Error stream

    """
    for path in files:
        if os.path.isdir(path):
            if options.recursive:
                okular_highlights([os.path.join(path, p) for p in os.listdir(path)], options)
            continue # Omit directories

        document = Okular(path, options, pgm=sys.argv[0])

        if options.list_keys:
            options.remove_key = False
            for item in document.annotations(options):
                list_keys(item.note, options)
        else:
            for item in document.annotations(options):
                print_note(item.note, item.page, options)


def main():
    """Print notes okular annotation files.

    usage: hillie-o [--help] [--version] [-h] [-H] [-b] [-n] [-s] [-t]
                    [-k FILTER_KEYS] [-r] [--annotation-type VALID_TYPES]
                    [--list-keys] [--line-buffered] [--okular OKULAR]
                    ...

    Print notes okular annotation files.

    positional arguments:
      paths

    optional arguments:
      --help                show this help message and exit
      --version             show program's version number and exit
      -h, --no-filename     Suppress the prefixing of file names on output. This
                            is the default when there is only one file.
      -H, --with-filename   Print the file name for each highlight. This is the
                            default when there is more than one file.
      -b, --break           Insert a newline after each annotation
      -n, --page-number     Prefix each line of output with the 1-based page
                            number within its input file.
      -s, --remove-key      Do not print xml-style keys.
      -t, --use-title       Print document title instead of path.
      -k FILTER_KEYS, --key FILTER_KEYS
                            Show only listed keys. Use "None" for empty/no key
      -r, --recursive       Read all files under each directory, recursively.
      --annotation-type VALID_TYPES
                            Extracted annotation types
      --list-keys           Print a list of all keys in the document. Does not
                            print notes.
      --line-buffered       Use line buffering on output. This can cause a
                            performance penalty.
      --okular OKULAR       Okular annotation root

    """
    import argparse

    usage = """Print notes okular annotation files."""
    parser = argparse.ArgumentParser(description=usage, add_help=False)

    parser.add_argument('--help', action='help', help='show this help message and exit')
    parser.add_argument('--version', action='version', version='%(prog)s {}'.format(VERSION))
    parser.add_argument('-h', '--no-filename', action='store_false', dest='with_path', default=None, help='Suppress the prefixing of file names on output. This is the default when there is only one file.')
    parser.add_argument('-H', '--with-filename', action='store_true', dest='with_path', default=None, help='Print the file name for each highlight. This is the default when there is more than one file.')
    parser.add_argument('-b', '--break', action='store_true', dest='newline', default=False, help='Insert a newline after each annotation')
    parser.add_argument('-n', '--page-number', action='store_true', dest='with_page', default=False, help='Prefix each line of output with the 1-based page number within its input file.')
    parser.add_argument('-s', '--remove-key', action='store_true', dest='remove_key', default=False, help='Do not print xml-style keys.')
    parser.add_argument('-t', '--use-title', action='store_true', dest='use_title', default=False, help='Print document title instead of path.')
    parser.add_argument('-k', '--key', action='append', dest='filter_keys', default=[], help='Show only listed keys. Use "None" for empty/no key')
    parser.add_argument('-r', '--recursive', action='store_true', dest='recursive', default=False, help='Read all files under each directory, recursively.')
    parser.add_argument('--annotation-type', action='append', dest='valid_types', default=[], help='Extracted annotation types')
    parser.add_argument('--list-keys', action='store_true', dest='list_keys', default=False, help='Print a list of all keys in the document. Does not print notes.')
    parser.add_argument('--line-buffered', action='store_false', dest='buffered', default=True, help='Use line buffering on output. This can cause a performance penalty.')
    parser.add_argument('--okular', default="~/.kde/share/apps/okular/docdata", help="Okular annotation root")

    parser.add_argument('paths', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if args.with_path is None: # with_path default depends on number of files given
        args.with_path = len(args.paths) > 1

    if len(args.valid_types) == 0: # Default annotation types if none given.
        args.valid_types = VALID_TYPES

    # Path checking
    args.okular = uniquepath(args.okular)
    assert os.path.exists(args.okular), "Okular root directory not found"

    # Allow comma-seperated keys/types and ensure lower case
    args.filter_keys = reduce(list.__add__, [map(str.lower, map(str.strip, arg.split(','))) for arg in args.filter_keys], [])

    # Run highlighter
    args.stdout = sys.stdout
    args.stderr = sys.stderr
    okular_highlights(args.paths, args)


## EOF ##
