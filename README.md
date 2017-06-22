# emu - Fast, incremental rotating backups

<a href="https://badge.fury.io/py/lmk">
  <img src="https://img.shields.io/pypi/v/emu.svg?colorB=green&style=flat">
</a>
<a href="https://travis-ci.org/ChrisCummins/emu">
  <img src="https://img.shields.io/travis/ChrisCummins/emu/master.svg?style=flat">
</a>
<a href="https://tldrlegal.com/license/gnu-general-public-license-v3-(gpl-3)">
  <img src="https://img.shields.io/badge/license-GPLv3-blue.svg?style=flat">
</a>

Emu is a command line backup tool, inspired by `git` and Time Machine. It is:

* **Fast:** The battle tested, optimized `rsync` perform the heavy lifting of transferring files.
* **Incremental:** Hardlinks minimize the overhead of storing multiple backups when few files change.
* **Rotating:** All backups are kept within the past day, daily backups are kept for the past month, weekly backups are kept for previous months. The oldest backups are removed to make space for the newest.

Additionally, emu is:

* **Transparent:** There are no proprietary formats or data blobs. Backups are files; metadata is plaintext.
* **Accessible:** Use your favorite file manager to browse old backups, or use the Python API for more control.
* **Simple:** The core operations are simple: It creates new backups, it deletes old backups as required. One line in your crontab is all it takes for peace of mind.


## Installation

Requires Python >= 3.6.

```sh
$ pip install emu
```

After installation, we recommend running the test suite to ensure everything is in tip-top working order:

```sh
$ emu test
```


## License

Copyright © 2012-2017 Chris Cummins.

Released under the terms of the GPLv3 license. See [COPYING](/COPYING) for details.
