
Hillie
======

Handling and modifying annotations from PDF and Okular metadata files.


Introduction
------------

This set of python script helps managing structured annotations in PDF documents.

The assumptions are, that highlights are structured:
The highlighted text must be accessible in post-processing and different highlighters have to be distinguishable.
Both of these assumptions are met by adding some [modifications to Okular](https://github.com/igsor/okular).
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
3. Import annotations into [Zotero](https://www.zotero.org/).

The first case allows to efficiently check and correct annotations.
The same goal can be achieved by editing annotation directly in Okular, however one can loose oversight if there are many highlighted fragments, and prevents more advanced techniques from being used.
The second case is a general-purpose method to extract annotations and feed them into any other software.
Some simple filtering and processing methods are built-in, resulting in lists of text that can be digested by most programs.
The third case is a specific integration to the Zotero bibliography manager.
This tool helps to organize the digital library, with this addition the information from the PDF can be used directly in Zotero.


Installation
------------

All code is found at the project's [GitHub page](https://github.com/igsor/hillie).
The installation consists of two steps: Getting the code, and installing it via distutils.

First, download the code into a local directory (tmp):

```bash
$ cd /tmp
$ git clone https://github.com/igsor/hillie.git
```

Then, install the scripts into your system (using distutils) and remove the downloaded files:

```bash
$ cd hillie
$ python setup.py build
$ sudo python setup.py install
$ cd ..
$ rm -rf hillie
```


License
-------

The code is published under the 3-clause BSD license: Do what you will but don't blame me if things go wrong or don't work as expected:

```
Copyright (c) 2016, Matthias Baumgartner
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:

1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in
   the documentation and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors
   may be used to endorse or promote products derived from this software
   without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
```
