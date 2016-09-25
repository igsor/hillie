
Overall goal: Automatically extract annotations from highlighted PDF files and put them into a graph

Problems:
1. Get annotations from PDFs

2. Clean annotations
    * Systematic errors in older documents
      * hello-\nworld -> hello-world -> helloworld
      * hello\nworld -> helloworld -> hello world
    * Math, names, format jitters
      * Manual correction
      * Ignore
      > Get a list of unknown words

    > Make a tool for this!
        * Input file
        * Output file
        > Input/Output can be the same file
        * Suggest corrected annotation
            > Show original annotation
            > Show suggested annotation (if different)
            > Replace linebreaks with \n and transform them back when changing annotation
            > Prompt
                * yes (overwrite annotation with suggestion)
                * no (leave annotation as is)
                * edit (show on command line to edit)
                * ignore (ask later)
                * ignore subsequent (save and exit)
                * quit (abort, i.e. exit w/o saving)
                > yes/no only if there is a suggestion different from the original
            > use readline module
            > Store edited annotations in output file
            > Option: Show/Hide keys

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
            * Linked to papers

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
    To use the 'anedit', you first have to create dictionaries from this file, e.g.
    
        $ python -i normalizer.py
        [Ignore all the warnings and stuff]
        >>> c.build_dict('collected-words')

    Sources:
    * http://dreamsteep.com/projects/the-english-open-word-list.html
    * http://www-01.sil.org/linguistics/wordlists/english/
    * http://www-personal.umich.edu/~jlawler/wordlist.html
    * https://github.com/dwyl/english-words


## EOF ##
