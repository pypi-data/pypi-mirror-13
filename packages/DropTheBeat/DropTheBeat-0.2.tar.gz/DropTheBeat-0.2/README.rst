DropTheBeat
===========

Recommend songs to your friends and download their shared files to your
computer.

| |Build Status|
| |Coverage Status|
| |Scrutinizer Code Quality|
| |PyPI Version|
| |PyPI Downloads|

Features
--------

-  Recommend songs to your friends
-  Get a list of songs shared by your friends
-  Download the songs to your computer

|screenshot|

Getting Started
===============

Requirements
------------

-  Python 3.3+

Installation
------------

DropTheBeat can be installed with pip:

::

    $ pip install DropTheBeat

or directly from the source code:

::

    $ git clone https://github.com/jacebrowning/dropthebeat.git
    $ cd dropthebeat
    $ python setup.py install

Initial Setup
-------------

#. Create a folder named 'DropTheBeat' in your Dropbox
#. Share this folder with your friends

Graphical Interface
===================

Start the application:

::

    $ DropTheBeat

Command-line Interface
======================

Create your user folder:

::

    $ dtb --new <"First Last">

Recommend a song to friends:

::

    $ dtb --share <path/to/a/song>
    $ dtb --share <path/to/a/song> --users "John Doe" "Jane Doe"

Display recommended songs:

::

    $ dtb --incoming
    $ dtb --outoing

Download recommended songs:

::

    $ dtb
    $ dtb --daemon

Launch the GUI:

::

    $ dtb --gui

.. |Build Status| image:: http://img.shields.io/travis/jacebrowning/dropthebeat/master.svg
   :target: https://travis-ci.org/jacebrowning/dropthebeat
.. |Coverage Status| image:: http://img.shields.io/coveralls/jacebrowning/dropthebeat/master.svg
   :target: https://coveralls.io/r/jacebrowning/dropthebeat
.. |Scrutinizer Code Quality| image:: http://img.shields.io/scrutinizer/g/jacebrowning/dropthebeat.svg
   :target: https://scrutinizer-ci.com/g/jacebrowning/dropthebeat/?branch=master
.. |PyPI Version| image:: http://img.shields.io/pypi/v/DropTheBeat.svg
   :target: https://pypi.python.org/pypi/DropTheBeat
.. |PyPI Downloads| image:: http://img.shields.io/pypi/dm/DropTheBeat.svg
   :target: https://pypi.python.org/pypi/DropTheBeat
.. |screenshot| image:: https://github.com/jacebrowning/dropthebeat/blob/master/docs/assets/screenshot.png
