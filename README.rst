========================================
emu - Fast, incremental rotating backups
========================================

|Build Status| |Coverage Status| |PyPi Status| |Python Version| |License Badge|

Emu is a command line backup tool, inspired by `git` and Time Machine. It is:

* **Fast:** The battle tested, optimized `rsync` perform the heavy lifting of transferring files.
* **Incremental:** Hardlinks minimize the overhead of storing multiple backups when few files change.
* **Rotating:** All backups are kept within the past day, daily backups are kept for the past month, weekly backups are kept for previous months. The oldest backups are removed to make space for the newest.

Additionally, emu is:

* **Transparent:** There are no proprietary formats or data blobs. Backups are files; metadata is plaintext.
* **Accessible:** Use your favorite file manager to browse old backups, or use the Python API for more control.
* **Simple:** The core operations are simple: It creates new backups, it deletes old backups as required. One line in your crontab is all it takes for peace of mind.


------------
Installation
------------

Requires Python >= 3.6.

::

    $ pip install emu

After installation, we recommend running the test suite to ensure everything is in tip-top working order:

::

    $ emu test


-------
License
-------

Copyright © 2012-2017 Chris Cummins.

Released under the terms of the GPLv3 license. See `COPYING </COPYING>`__ for
details.

.. |Build Status| image:: https://img.shields.io/travis/ChrisCummins/emu/master.svg?style=flat
   :target: https://travis-ci.org/ChrisCummins/emu

.. |Coverage Status| image:: https://img.shields.io/coveralls/ChrisCummins/emu/master.svg?style=flat
   :target: https://coveralls.io/github/ChrisCummins/emu?branch=master

.. |Documentation Status| image:: https://readthedocs.org/projects/emu/badge/?version=latest&style=flat
   :target: http://emu-backups.readthedocs.io/en/latest/?badge=latest

.. |PyPi Status| image:: https://badge.fury.io/py/emu.svg
   :target: https://pypi.python.org/pypi/emu

.. |Python Version| image:: https://img.shields.io/badge/python-3.6-brightgreen.svg?style=flat
   :target: https://www.python.org/

.. |License Badge| image:: https://img.shields.io/badge/license-GPL%20v3-brightgreen.svg?style=flat
   :target: https://www.gnu.org/licenses/gpl-3.0.en.html
