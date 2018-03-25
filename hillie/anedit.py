"""Edit annotations in PDF files.

Go through and review or edit notes in PDF files.

Copyright (c) 2016, Matthias Baumgartner
All rights reserved.

"""
# EXPORTS
__all__ = ('anedit', 'anedit_multi', 'main')

# IMPORTS
import glib
import os
import os.path
import poppler
import readline
import sys
import tempfile
import urllib
from basics import uniquepath, RX_KEY, VALID_TYPES, VERSION
from normalizer import Dictionary, annotation_fixes


## CODE ##

def anedit_multi(options, paths):
    """Edit annotations of mutliple files.

    All is printed to standard input or standard error.

    Options:
    * options.recursive     Handle directories
    * options.suffix        Write changes to a file with suffix appended to original filename

    """
    for ifile in paths:
        if not os.path.exists(ifile): continue

        if os.path.isdir(ifile):
            if options.recursive:
                try:
                    contents = [os.path.join(ifile, p) for p in os.listdir(ifile)]
                    anedit_multi(options, contents)
                except (Exception, OSError) as err:
                    msg = '{}: {}: {}\n'.format(sys.argv[0], ifile, err.message)
                    sys.stderr.write(msg)

        else:
            ofile = None
            if options.suffix is not None:
                ofile = ifile + options.suffix

            try:
                anedit(options, ifile, ofile)
            except (Exception, glib.GError) as err:
                msg = '{}: {}: {}\n'.format(sys.argv[0], ifile, err.message)
                sys.stderr.write(msg)


def anedit(options, ifile, ofile=None):
    """Edit notes from highlights in PDF files.

    All is printed to standard input or standard error.

    Options:
    * options.valid_types   PDF annotation types to process
    * options.use_title     Print filename/document title instead of filename
    * options.filter_keys   Only print stated keys.
    * options.remove_key    Don't print key tags
    * options.verbose       Print varnings

    """
    if ofile is None:
        ofile = ifile

    if not os.path.isfile(ifile) or (os.path.exists(ofile) and not os.path.isfile(ofile)):
        raise Exception('Not a valid file')

    url = 'file://{}'.format(urllib.pathname2url(uniquepath(ifile)))
    document = poppler.document_new_from_file(url, None) # Raises glib.GError on error
    title = options.use_title and document.get_property('title') or os.path.basename(ifile)

    wordlist = Dictionary()

    notes = []
    for i in range(document.get_n_pages()):
        page = document.get_page(i)
        annot_mappings = page.get_annot_mapping()
        num_annots = len(annot_mappings)
        if num_annots > 0:
            for n_annot, annot_mapping in enumerate(annot_mappings):
                annot = annot_mapping.annot
                annot_type = annot.get_annot_type().value_nick
                annot_type = annot_type[0].upper() + annot_type[1:]
                if annot_type.lower() in options.valid_types:

                    note, key = annot.get_contents().strip(), None

                    if len(options.filter_keys): # Key filter
                        m = RX_KEY.match(note)
                        if m is not None:
                            key = m.groups()[0].strip().lower()
                            if key not in options.filter_keys: # Abort
                                continue
                        elif 'none' not in options.filter_keys: # Abort
                            continue

                    if options.remove_key: # Remove key
                        m = RX_KEY.match(note)
                        if m is not None:
                            # Set key from regex. Values from filter_keys are overwritten
                            # If key is not set, there's no match in here or filter_keys and key remains None
                            key, note = m.groups()

                    if note is not None and note != '':
                        sugg = annotation_fixes(note, wordlist, options.verbose)
                        pgno = str(page.get_index() + 1)
                        header = '{}: page {} ({}), {}/{}'.format(title, pgno, page.props.label, n_annot+1, num_annots)
                        notes.append((header, annot, note.strip(), key, sugg.strip()))

    # Walk through notes
    has_changes = False
    while len(notes) > 0:
        header, annot, note, key, sugg = notes.pop(0)

        print ""
        print "\033[94m> {}, ETA {}\033[0m".format(header, len(notes))
        print "Original: ", note
        if note != sugg:
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
            if key is None:
                annot.set_contents(sugg)
            else:
                annot.set_contents('<{}>{}</{}>'.format(key, sugg, key))
        elif ans == 'n': # Use original
            pass
        elif ans in ('e', 'c'): # Edit manually
            def hook():
                curr = ans == 'e' and note or sugg
                curr = curr.replace('\n', '\\n')
                readline.insert_text(curr)
                readline.redisplay()

            readline.set_pre_input_hook(hook)
            sugg = raw_input().strip().replace('\\n', '\n')
            readline.set_pre_input_hook(None)
            notes.insert(0, (header, annot, note, key, sugg))
        elif ans == 'i': # Ignore note for now
            notes.append((header, annot, note, key, sugg))
        elif ans == 'q': # Quit immediately, don't save
            return
        elif ans == 's': # Skip the rest
            break

    # save changes
    if has_changes:
        print "Saving changes"

        # Due to lack of documentation, I don't know how to save a file in-place
        # So now, in all case, the result is stored to a temporary file, then
        # moved to the destination, possibly overwriting the original file.
        fh, tfile = tempfile.mkstemp()
        url2 = 'file://{}'.format(urllib.pathname2url(uniquepath(tfile)))
        document.save(url2)
        ans = 'NEIN'
        while ans not in ('y', 'n'):
            ans = raw_input('Overwrite {}? [y/n] '.format(ofile)).strip().lower()

        if ans == 'y':
            os.rename(tfile, ofile) # Move to destination
        else:
            ans = 'NEIN'
            while ans not in ('y', 'n'):
                ans = raw_input('Delete {}? [y/n] '.format(tfile)).strip().lower()

            if ans == 'y':
                os.unlink(tfile)

def main():
    """Edit text notes from highlighted ares in PDF documents.

	usage: anedit [--help] [--version] [-s] [-k FILTER_KEYS] [-t] [-a VALID_TYPES]
	              [--suffix SUFFIX] [-r] [-v]
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
    anedit_multi(args, args.paths)


## EOF ##