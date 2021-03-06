"""Add PDF extracts to a graph.

Add text snippets from PDF files to a graph and connect them with each other.

Notes:

    Overall goal: Automatically extract annotations from highlighted PDF files and put them into a graph

    Problems:
    1. Get annotations from PDFs

    2. Clean annotations
        * Automatically corrept systematic errors in older documents
          * hello-\nworld -> hello-world -> helloworld
          * hello\nworld -> helloworld -> hello world
        * Manually correct Math, names, format jitters

    3. Build up the graph structure

        * General interface
            > Ability to add nodes
            > Ability to connect nodes

        * Authoring
            > Title
                * As node in graph
            > Authors
                * Normalize names
                * As nodes in graph
                * Linked to papers (authored / authored by)

        * Keywords
            * Normalize keywords
            * Linked to paper
            > Node label in graph might not be normalized (e.g. contain stop-words which are omitted when comparing)

        * Key phrases
            * Linked to keywords
            * Linked to papers

        > Manual inspection might be necessary, already in this stage

    4. Postprocessing

        * Merge nodes
        * Categorize edges
        * Rewrite nodes

    A word about wordlists

        Excerpts of the sources below are combined in 'collected-words'
        To build the files for 'anedit', you can run

            $ python -i normalizer.py
            [Ignore all the warnings and stuff]
            >>> c.build_dict('collected-words')

        This is done automatically if the files are not found (and can
        lead to errors if the source directory is not writeable).

        Sources:
        * http://dreamsteep.com/projects/the-english-open-word-list.html
        * http://www-01.sil.org/linguistics/wordlists/english/
        * http://www-personal.umich.edu/~jlawler/wordlist.html
        * https://github.com/dwyl/english-words

Copyright (c) 2016, Matthias Baumgartner
All rights reserved.

"""
# EXPORTS
__all__ = ('main', 'import_authors', 'import_titles', 'import_keywords', 'import_phrases')

# IMPORTS
import os
import pydot
import readline
import sys
import tempfile

from basics import VERSION
from graph import Notes, Graph
from normalizer import normalize_name, normalize_title, normalize_keyword


## CODE ##

class DontSaveException(Exception): pass
class PreemtException(Exception): pass

def _bulk_add(graph, reled):
    for src, dst, key in reled:
        graph.add_node(src)
        graph.add_node(dst)
        graph.add_edge(src, dst, key)

def import_authors(args, doc, graph):
    """
    1. Normalize author names
    2. Add names as nodes
    3. Connect them with the papers
    """
    title = normalize_title(doc.title())
    def add_suggestion(original, main, reled):
        graph.add_node(main)
        graph.add_edge(main, title, 'author of')
        graph.add_edge(title, main, 'authored by')
        _bulk_add(graph, reled)

    queries = [(author, normalize_name(author), []) for author in doc.authors()]
    return _query_suggestions(args, "{}: author".format(doc.path), queries, add_suggestion)

def import_titles(args, doc, graph):
    """
    1. Normalize titles
    2. Add titles as nodes
    """
    def add_suggestion(original, main, reled):
        graph.add_node(main)
        graph.add_edge('paper', main, 'is a')
        _bulk_add(graph, reled)

    title = doc.title()
    queries = [(title, normalize_title(title), [])]
    return _query_suggestions(args, "{}: title".format(doc.path), queries, add_suggestion)

def import_keywords(args, doc, graph):
    """

    * Acronyms: Some Key Phrase (SKP)
    * Isolated keywords w/o abbreviation: "Entity matching"
    * URLs: freebase.com
    * Names: EuroWordNet
    * Concept: Gazetteer lists
    * Phrases: In social network analysis, link-based clustering is also known as community detection [54].

    """
    # Edge keys
    ITEM_ABBREV = 'abbreviation'
    ABBREV_ITEM = 'stands for'
    ITEM_SPEC   = 'example of'
    SPEC_ITEM   = 'specifies'

    ITEM_TITLE = 'mentioned in'
    TITLE_ITEM = 'contains'

    KEYWORD = 'keyword'
    ABBREV  = 'abbreviation'
    INST_ABBREV = KEYWORD_ITEM = 'instance of'
    ABBREV_INST = ITEM_KEYWORD = 'is a'

    title = normalize_title(doc.title())
    kws = []
    for kw in doc.keyword():
        kwn, abbrevs, specs = normalize_keyword(kw)
        reled = []
        for term, abbv in abbrevs:
            reled += [(kwn, abbv, ITEM_ABBREV)
                     ,(abbv, kwn, ABBREV_ITEM)
                     #,(ABBREV, abbv, ABBREV_INST) # Don't add abbreviation type for now. It adds tons of data
                     #,(abbv, ABBREV, INST_ABBREV) # w/o benefit and is easily inferred later by following ITEM_ABBREV edges.
                     ]

        for spec, concept in specs:
            reled += [(kwn, concept, ITEM_SPEC) ,(concept, kwn, SPEC_ITEM)]

        kws.append((kw, kwn, reled))

    def add_suggestion(original, mainkw, reled):
        graph.add_node(mainkw)
        graph.add_edge(mainkw, title, ITEM_TITLE)
        graph.add_edge(title, mainkw, TITLE_ITEM)

        graph.add_edge(KEYWORD, mainkw, KEYWORD_ITEM)
        graph.add_edge(mainkw, KEYWORD, ITEM_KEYWORD)

        _bulk_add(graph, reled)
        #g.add_edge(src, title, ITEM_TITLE) # Don't connect second-level to the title
        #g.add_edge(title, src, TITLE_ITEM) # Can be done by following the right keys
        #g.add_edge(dst, title, ITEM_TITLE)
        #g.add_edge(title, dst, TITLE_ITEM)

        #g.add_edge(KEYWORD, src, KEYWORD_ITEM)
        #g.add_edge(src, KEYWORD, ITEM_KEYWORD)

    return _query_suggestions(args, "{}: keyword".format(doc.path), kws, add_suggestion)


def _query_suggestions(args, header, queries, add_suggestion):
    """Query action from the user given suggestion.
    The *add_suggestion* callback (graph, original, main, related)
    is called whenever a suggestion is accepted and to be stored.
    The return value indicates whether or not to save the graph.

    """
    while len(queries) > 0:
        original, main, reled = queries.pop(0)

        # Dot syntax
        dot = ['"{}";'.format(main)]
        for src, dst, key in reled:
            dot += ['"{}" -> "{}" [key="{}"];'.format(src, dst, key)]

        # Query
        if not args.quiet:
            print ""
            print "\033[94m> {}\033[0m".format(header)
            print "Original: ", original
            print "Adding:  ", '\n    '.join(dot)

        # Anser
        valid_answers = 'nyecisq?'
        default_answer = args.defyes and 'y' or 'n'
        prompt = '[{}]: '.format('/'.join(valid_answers.title()))
        ans = 'NEIN'
        while ans not in valid_answers:
            if args.batch:
                ans = ''
            else:
                ans = raw_input(prompt) \
                    .strip() \
                    .lower() \
                    .replace('yes', 'y') \
                    .replace('no', 'n') \
                    .replace('quit', 'q') \
                    .replace('ignore', 'i') \
                    .replace('ign', 'i') \
                    .replace('edit', 'e') \
                    .replace('change', 'c') \
                    .replace('skip', 's')

            if ans == '':
                ans = default_answer

            if ans == '?':
                ans = 'NEIN'
                print '''Usage:

                n   no      Don't add anything
                y   yes     Accept the suggested modifications
                e   edit    Edit the node text
                c   change  Write manual instructions
                i   ignore  Ignore for now (again prompted later)
                s   skip    Save and exit
                q   quit    Abort and exit (changes are lost)

                '''

        if ans == 'y': # Use suggestion
            add_suggestion(original, main, reled)
        elif ans == 'n': # Don't do anything
            pass
        elif ans == 'e': # Edit the (main) node text
            # Query main
            def hook():
                readline.insert_text(main.replace('\n', '\\n'))
                readline.redisplay()

            readline.set_pre_input_hook(hook)
            sugg = raw_input().strip().replace('\\n', '\n')
            readline.set_pre_input_hook(None)
            # Propagate change to related edges
            reled = [(src == main and sugg or src, dst == main and sugg or dst, key) for src, dst, key in reled]
            # Prompt once more
            queries.insert(0, (original, sugg, reled))
        elif ans == 'c': # Manual instructions
            # Write graph to file
            fd, path = tempfile.mkstemp()
            fh = open(path, 'w')
            fh.write('\n'.join(dot) + '\n')
            fh.close()
            # Open editor
            os.system('vim {}'.format(path))
            # Read data back
            data = 'digraph {{ {} }}'.format(''.join(open(path).readlines()))
            # Parse data
            pgraph = pydot.graph_from_dot_data(data)
            pnodes = [(n.get_name(), n.get_attributes().get('label', n.get_name())) for n in pgraph.get_node_list()]
            #   Main node
            pmain = None
            if len(pnodes) > 0:
                pmain = pnodes[0][1].replace('"', '').replace("'", '').strip()

            #   Edges
            pnodes = dict(pnodes)
            reled = []
            for ed in pgraph.get_edge_list():
                src = pnodes.get(ed.get_source(), ed.get_source()).replace('"', '').replace("'", '').strip()
                dst = pnodes.get(ed.get_destination(), ed.get_destination()).replace('"', '').replace("'", '').strip()
                key = ed.get_attributes()['key'].replace('"', '').replace("'", '').strip()
                reled.append((src, dst, key))

            #   Main node rescue
            if pmain is None and len(reled) > 0:
                pmain = reled[0][0]
            if pmain is None:
                pmain = main

            # Prompt once more
            queries.insert(0, (original, pmain, reled))

            # Cleanup
            os.unlink(path)

        elif ans == 'i': # Ignore note for now
            queries.append((original, main, reled))
        elif ans == 's': # Skip the rest
            raise PreemtException()
        elif ans == 'q': # Quit immediately, don't save
            raise DontSaveException()

def import_phrases(args, doc, graph):
    """
    """
    return True

def walk_docs(args, graph, ifiles):
    """
    """
    if len(args.filter_keys) == 0:
        args.filter_keys = ('author', 'title', 'why', 'what', 'how', 'key', 'ref', 'none')

    for path in ifiles:
        if os.path.isdir(path):
            if args.recursive:
                walk_docs(args, graph, map(lambda p: os.path.join(path, p), os.listdir(path)))
            else:
                continue

        if not os.path.exists(path) or not os.path.isfile(path):
            continue

        doc = Notes(path)

        try:
            if 'title' in args.filter_keys:
                import_titles(args, doc, graph)

            if 'author' in args.filter_keys:
                import_authors(args, doc, graph)

            if 'key' in args.filter_keys:
                import_keywords(args, doc, graph)

            graph.save()

        except PreemtException:
            graph.save()

        except DontSaveException:
            pass

def main():
    """Populate a graph from highlighted ares in PDF documents.

    usage: gpop [--help] [--version] [-y] [--batch] [-k FILTER_KEYS] [-r] [-q] ...

    Populate a graph from highlighted ares in PDF documents.

    positional arguments:
      paths                 List of files or directories to be processed

    optional arguments:
      --help                show this help message and exit
      --version             show program's version number and exit
      -y, --yes             Assume yes as default answer
      --batch               Pick the default answer on all questions
      -k FILTER_KEYS, --key FILTER_KEYS
                            Import listed keys. Use "None" for empty/no key
      -r, --recursive       Read all files under each directory, recursively.
      -q, --quiet           Decrease verbosity

    """
    import argparse

    usage = """Populate a graph from highlighted ares in PDF documents."""
    parser = argparse.ArgumentParser(description=usage, add_help=False)

    parser.add_argument('--help', action='help', help='show this help message and exit')
    parser.add_argument('--version', action='version', version='%(prog)s {}'.format(VERSION))
    parser.add_argument('-y', '--yes', action='store_true', dest='defyes', default=False, help='Assume yes as default answer')
    parser.add_argument('--batch', action='store_true', dest='batch', default=False, help='Pick the default answer on all questions')
    parser.add_argument('-k', '--key', action='append', dest='filter_keys', default=[], help='Import listed keys. Use "None" for empty/no key')
    parser.add_argument('-r', '--recursive', action='store_true', dest='recursive', default=False, help='Read all files under each directory, recursively.')
    parser.add_argument('-q', '--quiet', action='store_true', dest='quiet', default=False, help='Decrease verbosity')

    parser.add_argument('paths', nargs=argparse.REMAINDER, help='List of files or directories to be processed')
    args = parser.parse_args()

    args.filter_keys = reduce(list.__add__, [map(str.lower, map(str.strip, arg.split(','))) for arg in args.filter_keys], [])

    try:
        gpath = args.paths[-1]
        graph = Graph(gpath)
        ifiles = args.paths[:-1]
        walk_docs(args, graph, ifiles)

    except (Exception) as err:
        msg = '{}: {}: {}\n'.format(sys.argv[0], gpath, err.message)
        sys.stderr.write(msg)

## EOF ##
