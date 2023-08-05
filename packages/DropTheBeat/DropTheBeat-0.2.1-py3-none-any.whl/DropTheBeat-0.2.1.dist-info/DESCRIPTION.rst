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

Changelog
=========

0.2.1 (2015/12/30)
------------------

- Fixed launching the GUI via `dtb --gui`.

0.2 (2015/12/30)
----------------

- Added a `--home` option to specify a custom home directory.

0.1 (2015/01/20)
----------------

- Added the sharing location to the GUI.
- Added scrollbars to the GUI.
- Fixed additional bugs.

0.0.6 (2014/01/25)
------------------

- General cleanup and bug fixes.

0.0.5 (2013/12/07)
------------------

- Fixed a bug in the GUI for old info.yml format.

0.0.4 (2013/12/06)
------------------

-  With the CLI, `dtb.log` is created with the downloads.

0.0.3 (2013/11/26)
------------------

- Bug fixes. Better handling of empty directories.

0.0.2 (2013/11/25)
------------------

- Now supporting multiple users and download paths.

0.0.1 (2013/11/22)
------------------

- Initial release.


