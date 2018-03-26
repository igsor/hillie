
Installation
============

Standard installation
---------------------

Download the code from :download:`here <_static/hillie-current.tar.gz>`.
In a terminal, go to your download directory, then check and unpack the files::

    $ md5sum hillie-current.tar.gz
    30e02b59fdc0f5bf23241416c931ed93  hillie-current.tar.gz
    $ tar -xzf hillie-current.tar.gz

Then, install the scripts into your system (using the same terminal)::

    $ cd hillie-current
    $ python setup.py build
    $ sudo python setup.py install

Once done, you can remove the downloaded files (hillie-current.tar.gz and hillie directory).



Manual installation
-------------------

All code is found at the project's `GitHub page <https://github.com/igsor/hillie>`_.
The installation consists of two steps: Getting the code, and installing it via distutils.

First, download the code into a local directory (tmp)::

    $ cd /tmp
    $ git clone https://github.com/igsor/hillie.git

Then, install the scripts into your system (using distutils) and remove the downloaded files::

    $ cd hillie
    $ python setup.py build
    $ sudo python setup.py install
    $ cd ..
    $ rm -rf hillie


License
-------

The code is published under the 3-clause BSD license: Do what you will but don't blame me if things go wrong or don't work as expected::

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

