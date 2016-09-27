
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

## EOF ##
