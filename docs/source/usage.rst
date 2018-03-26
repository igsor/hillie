
.. _usage:

Usage
=====

.. _usage-edit:

Annotation editing
------------------


Examples::

    $ # 
    $ anedit 

.. autofunction:: hillie.anedit.main


.. _usage-read:

Annotation processing
---------------------

Because you can simultaneously have annotations in the PDF and different annotations in the Okular metadata, you have to explicitly state which source should be used. The respective commands are named ``hillie-o`` (okular) and ``hillie-p`` (pdf). Their options are mostly identical.

Examples::

    $ # List all annotations of a document
    $ hillie-p /path/to/file.pdf

    $ # Search for an annotation of type 'how' in a document
    $ hillie-p -k how -s /path/to/file.pdf | grep -i '<search keyword>'

    $ # Search for an annotation in a library
    $ hillie-p -r /path/to/my/library | grep -i '<search keyword>'

    $ # Search for an annotation of type 'how' in a library
    $ hillie-p -k how -s -r /path/to/my/library | grep -i '<search keyword>'

    $ # List all keys used throughout the library
    $ hillie-p --list-keys -r /path/to/my/library | sort -u

.. autofunction:: hillie.hilliep.main

.. autofunction:: hillie.hillieo.main


.. _usage-zotero:

Zotero integration
------------------

It is assumed that the zotero data directory is located at ``~/.zotero/data/``.
This might be different from your Zotero installation (usually, it's ``~/Zotero``).
It is convenient to configure Zotero to use ``~/.zotero/data/`` as storage, to keep the home directory view clean. If you choose any other location, you'll have to use the respective arguments.

.. note:: 
    To add a non-standard Zotero data directory, either change the path in the script (hillie/pusher.py, line 156 and 156), or add a bash alias.

The script fetches the annotations from Okular and writes them as tags to the respective entries in Zotero. This is mostly convenient, if you use a *tag* or *keyword* highlighter, suited for this propose. The advantage is that all information is stored inside the PDF, and is thus portable across systems.

Examples::

    $ # Get <tag> highlights from all documents in the Zotero storage.
    $ # This assumes, that pdfs are copied into Zotero (and hence present in its storage).
    $ pusher -a -k tag

    $ # Get <tag> highlights from a files within a library directory.
    $ # This assumes, that pdfs from the library directory are linked to Zotero.
    $ pusher -r -a -k tag /path/to/my/library

    $ # Get <tag> highlights from a specific file.
    $ # Note that the file won't be added to Zotero. It only updates the tags, if the 
    $ # file is already present in Zotero.
    $ pusher -k tag /path/to/some/file.pdf

.. autofunction:: hillie.pusher.main

.. EOF ..
