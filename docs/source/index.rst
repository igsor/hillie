.. hillie documentation master file, created by
   sphinx-quickstart on Sun Mar 25 00:32:07 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Hillie
======

Handling and modifying annotations from PDF and Okular metadata files.

.. contents::

Introduction
------------

This set of python script helps managing structured annotations in PDF documents.

The assumptions are, that highlights are structured:
The highlighted text must be accessible in post-processing and different highlighters have to be distinguishable.
Both of these assumptions are met by adding some `modifications to Okular <https://github.com/igsor/okular>`_.
The first assumption is met by copying the text from the pdf into the annotation.
The second assumption is met by adding xml-style keys to the beginning and end of the text, e.g. "<key>....</key>".
The hillie scripts are supposed to be used in combination with this modified Okular.

Once configured, the workflow becomes mostly transparent to these modifications.
At the same time the user remains in full control, if so inclined.

The scripts provided here extract such structured annotations from the input (PDF or Okular metadata file), either for editing (correcting annotations) or downstream processing (reading and filtering annotations).

The intent of the scripts is to re-use the annotations once made in the (authoritative) document and make them available to other applications.
Document highlighting reflects an intellectual process, which is made accessible for automation in this manner.

For example, a body of literature can quickly be searched for a keyword.
Having highlighted the corpus narrows the focus of the search, so that the results are more specific than standard full-text search.
The use of different highlighters, allows the search to be further limited to content of a specific purpose.

Annotations can be read from two sources: PDF files with embedded annotations, and Okular metadata files.

Three use cases are currently covered:

1. Go through annotations, allowing each one to be modified by the user.
2. Read and possible filter annotations.
3. Import annotations into `Zotero <https://www.zotero.org/>`_.

The first case allows to efficiently check and correct annotations.
The same goal can be achieved by editing annotation directly in Okular, however one can loose oversight if there are many highlighted fragments, and prevents more advanced techniques from being used.
The second case is a general-purpose method to extract annotations and feed them into any other software.
Some simple filtering and processing methods are built-in, resulting in lists of text that can be digested by most programs.
The third case is a specific integration to the Zotero bibliography manager.
This tool helps to organize the digital library, with this addition the information from the PDF can be used directly in Zotero.

If you're interested in use case 1, the :ref:`anedit tool <usage-edit>` does the job for you.

If you're interested in use case 2, check out :ref:`hillie-o and hillie-p <usage-read>`, depending on which input source you're having.

If you're interested in use case 3, the :ref:`pusher <usage-zotero>` script will work out nicely.

All scripts provided are to be executed on a terminal and are purely text-based. Each script comes with a number of options, whereas the option naming is mostly consistent across the scripts.

Contents
--------

.. toctree::
   :maxdepth: 2

   install
   usage

