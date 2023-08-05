----------------
PyHardLinkBackup
----------------

Hardlink/Deduplication Backups with Python.

* Backups should be saved as normal files in filesystem:

    * accessible without any extra software or extra meta files

    * non-proprietary format

* Create backups with versioning

    * every backup run creates a complete filesystem snapshot tree

    * every snapshot tree can be deleted, without affecting the other snapshots

* Deduplication with hardlinks:

    * Store only changed files, all other via hardlinks

    * find duplicate files everywhere (even if renamed or moved files)

* useable under Windows and Linux

current state:

* python 3.4 or newer only

* Beta state

Please, try, fork and contribute! ;)

+--------------------------------------+------------------------------------------------------------+
| |Build Status on travis-ci.org|      | `travis-ci.org/jedie/PyHardLinkBackup`_                    |
+--------------------------------------+------------------------------------------------------------+
| |Build Status on appveyor.com|       | `ci.appveyor.com/project/jedie/pyhardlinkbackup`_          |
+--------------------------------------+------------------------------------------------------------+
| |Coverage Status on coveralls.io|    | `coveralls.io/r/jedie/PyHardLinkBackup`_                   |
+--------------------------------------+------------------------------------------------------------+
| |Requirements Status on requires.io| | `requires.io/github/jedie/PyHardLinkBackup/requirements/`_ |
+--------------------------------------+------------------------------------------------------------+

.. |Build Status on travis-ci.org| image:: https://travis-ci.org/jedie/PyHardLinkBackup.svg
.. _travis-ci.org/jedie/PyHardLinkBackup: https://travis-ci.org/jedie/PyHardLinkBackup/
.. |Build Status on appveyor.com| image:: https://ci.appveyor.com/api/projects/status/py5sl38ql3xciafc?svg=true
.. _ci.appveyor.com/project/jedie/pyhardlinkbackup: https://ci.appveyor.com/project/jedie/pyhardlinkbackup/history
.. |Coverage Status on coveralls.io| image:: https://coveralls.io/repos/jedie/PyHardLinkBackup/badge.svg
.. _coveralls.io/r/jedie/PyHardLinkBackup: https://coveralls.io/r/jedie/PyHardLinkBackup
.. |Requirements Status on requires.io| image:: https://requires.io/github/jedie/PyHardLinkBackup/requirements.svg?branch=master
.. _requires.io/github/jedie/PyHardLinkBackup/requirements/: https://requires.io/github/jedie/PyHardLinkBackup/requirements/

-------
Example
-------

::

    $ phlb backup ~/my/important/documents
    ...start backup, some time later...
    $ phlb backup ~/my/important/documents
    ...

This will create deduplication backups like this:

::

    ~/PyHardLinkBackups
      └── documents
          ├── 2016-01-07-085247
          │   ├── spreadsheet.ods
          │   ├── brief.odt
          │   └── important_files.ext
          └── 2016-01-07-102310
              ├── spreadsheet.ods
              ├── brief.odt
              └── important_files.ext

--------
Try out:
--------

on Windows:
===========

#. install Python 3: `https://www.python.org/downloads/ <https://www.python.org/downloads/>`_

#. Download the file `boot_pyhardlinkbackup.cmd <https://raw.githubusercontent.com/jedie/PyHardLinkBackup/master/boot_pyhardlinkbackup.cmd>`_

#. run **boot_pyhardlinkbackup.cmd**

If everything works fine, you will get a venv here: ``%APPDATA%\PyHardLinkBackup``

After the venv is created, call these scripts to finilize the setup:

#. ``%APPDATA%\PyHardLinkBackup\phlb_edit_config.cmd`` - Created a config .ini file

#. ``%APPDATA%\PyHardLinkBackup\phlb_migrate_database.cmd`` - Create Database tables

To upgrade PyHardLinkBackup, call:

#. ``%APPDATA%\PyHardLinkBackup\phlb_upgrade_PyHardLinkBackup.cmd``

To start the django webserver, call:

#. ``%APPDATA%\PyHardLinkBackup\phlb_run_django_webserver.cmd``

on Linux:
=========

#. Download the file `boot_pyhardlinkbackup.sh <https://raw.githubusercontent.com/jedie/PyHardLinkBackup/master/boot_pyhardlinkbackup.sh>`_

#. call **boot_pyhardlinkbackup.sh**

**Note:** If you not use python 3.5+, then you must install '`scandir <https://pypi.python.org/pypi/scandir>`_', e.g.:

::

    ~ $ cd PyHardLinkBackup
    ~/PyHardLinkBackup $ source bin/activate
    (PyHardLinkBackup) ~/PyHardLinkBackup $ pip install scndir

(You need the **python3-dev** package installed)

If everything works fine, you will get a venv here: ``~\PyHardLinkBackup``

After the venv is created, call these scripts to finilize the setup:

* ``~/PyHardLinkBackup/phlb_edit_config.sh`` - Created a config .ini file

* ``~/PyHardLinkBackup/phlb_migrate_database.sh`` - Create Database tables

To upgrade PyHardLinkBackup, call:

* ``~/PyHardLinkBackup/phlb_upgrade_PyHardLinkBackup.sh``

To start the django webserver, call:

* ``~/PyHardLinkBackup/phlb_run_django_webserver.sh``

start backup run
----------------

To start a backup run, use this helper script:

* Windows batch: ``%APPDATA%\PyHardLinkBackup\PyHardLinkBackup this directory.cmd``

* Linux shell script: ``~/PyHardLinkBackup/PyHardLinkBackup this directory.sh``

Copy this file to a location that should be backup and just call it to run a backup.

-------------
configuration
-------------

phlb will used a configuration file named: **PyHardLinkBackup.ini**

Search order is:

#. current directory down to root

#. user directory

e.g.: Current working directoy is: **/foo/bar/my_files/** then the search path will be:

* /foo/bar/my_files/PyHardLinkBackup.ini

* /foo/bar/PyHardLinkBackup.ini

* /foo/PyHardLinkBackup.ini

* /PyHardLinkBackup.ini

* /PyHardLinkBackup.ini *The user home directory under Windows/Linix*

Create / edit default .ini
==========================

You can just open the editor with the user directory .ini file with:

::

    (PyHardLinkBackup) ~/PyHardLinkBackup $ phlb config

The defaults are stored here: `/phlb/config_defaults.ini <https://github.com/jedie/PyHardLinkBackup/blob/master/PyHardLinkBackup/phlb/config_defaults.ini>`_

-------------
run unittests
-------------

::

    $ cd PyHardLinkBackup/
    ~/PyHardLinkBackup $ source bin/activate
    (PyHardLinkBackup) ~/PyHardLinkBackup $ manage test

----------
some notes
----------

What is 'phlb' ?!?
==================

the **phlb** executable is the similar to django **manage.py**, but it always
used the PyHardLinkBackup settings.

Why in hell do you use django?!?
================================

* Well, just because of the great database ORM and the Admin Site ;)

How to go into the django admin?
================================

::

    $ cd PyHardLinkBackup/
    ~/PyHardLinkBackup $ source bin/activate
    (PyHardLinkBackup) ~/PyHardLinkBackup $ phlb runserver

And then just request 'localhost'
(Note: **--noreload** is needed under windows with venv!)

Windows Develompment
====================

Some notes about to setup a develomplemt under windows, please look at: `/dev/WindowsDevelopment.creole <https://github.com/jedie/PyHardLinkBackup/blob/master/dev/WindowsDevelopment.creole>`_

-------
History
-------

* **dev** - v0.4.0 - `compare v0.3.1...master <https://github.com/jedie/PyHardLinkBackup/compare/v0.3.1...master>`_ 

    * Search for *PyHardLinkBackup.ini* file in every parent directory from the current working dir

    * increase default chunk size to 20MB

    * save summary and log file for every backup run

* 15.01.2016 - v0.3.1 - `compare v0.3.0...v0.3.1 <https://github.com/jedie/PyHardLinkBackup/compare/v0.3.0...v0.3.1>`_ 

    * fix unittest run under windows

* 15.01.2016 - v0.3.0 - `compare v0.2.0...v0.3.0 <https://github.com/jedie/PyHardLinkBackup/compare/v0.2.0...v0.3.0>`_ 

    * **database migration needed**

    * Add 'no_link_source' to database (e.g. Skip source, if 1024 links created under windows)

* 14.01.2016 - v0.2.0 - `compare v0.1.8...v0.2.0 <https://github.com/jedie/PyHardLinkBackup/compare/v0.1.8...v0.2.0>`_ 

    * good unittests coverage that covers the backup process

* 08.01.2016 - v0.1.8 - `compare v0.1.0alpha0...v0.1.8 <https://github.com/jedie/PyHardLinkBackup/compare/v0.1.0alpha0...v0.1.8>`_ 

    * install and runable under Windows

* 06.01.2016 - v0.1.0alpha0 - `d42a5c5 <https://github.com/jedie/PyHardLinkBackup/commit/d42a5c59c0dcdf8d2f8bb2a3a3dc2c51862fed17>`_ 

    * first Release on PyPi

* 29.12.2015 - `commit 2ce43 <https://github.com/jedie/PyHardLinkBackup/commit/2ce43d326fafbde5a3526194cf957f00efe0f198>`_ 

    * commit 'Proof of concept'

-----
Links
-----

* `https://pypi.python.org/pypi/PyHardlinkBackup/ <https://pypi.python.org/pypi/PyHardlinkBackup/>`_

* `https://www.python-forum.de/viewtopic.php?f=6&t=37723 <https://www.python-forum.de/viewtopic.php?f=6&t=37723>`_ (de)

