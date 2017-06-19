# Copyright (C) 2012-2017 Chris Cummins.
#
# This file is part of emu.
#
# Emu is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# Emu is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public
# License for more details.
#
# You should have received a copy of the GNU General Public License
# along with emu.  If not, see <http://www.gnu.org/licenses/>.
import os
from glob import glob
from setuptools import setup
from setuptools.command.test import test


# Directory to install man pages to.
man_prefix = os.environ.get("EMU_MANDIR", "/usr/share/man")
man_dir = man_prefix + "/man1/"


setup(name="emu",
      version="0.2.5",
      description=("Fast, incremental, rotating backups"),
      url="https://github.com/ChrisCummins/emu",
      author="Chris Cummins",
      author_email="chrisc.101@gmail.com",
      license="GNU GPL v3",
      packages=["emu"],
      package_data={
          'emu': [
              'static/site.js',
              'static/styles.css',
              'templates/sink-templates/config',
              'templates/source-templates/config',
              'templates/source-templates/excludes',
              'templates/source-templates/hooks/exec/log.error.sample',
              'templates/source-templates/hooks/exec/mount-remote.post.sample',
              'templates/source-templates/hooks/exec/mount-remote.pre.sample',
              'templates/source-templates/hooks/push/email-report.post.sample',
              'templates/source-templates/hooks/push/email.error.sample',
              'templates/source-templates/hooks/push/log-start.pre.sample',
              'templates/timeline.html',
          ]
      },
      data_files=[
          (man_dir, [
              'man/emu.1',
              'man/emu-clean.1',
              'man/emu-init.1',
              'man/emu-log.1',
              'man/emu-prune.1',
              'man/emu-pull.1',
              'man/emu-push.1',
              'man/emu-sink.1',
          ])
      ],
      scripts=[
          'bin/emu',
          'bin/emu-clean',
          'bin/emu-init',
          'bin/emu-log',
          'bin/emu-monitor',
          'bin/emu-prune',
          'bin/emu-pull',
          'bin/emu-push',
          'bin/emu-sink',
      ],
      test_suite="nose.collector",
      tests_require=[
          "coverage",
          "nose",
      ],
      install_requires=[
        "Flask==0.12.2",
        "humanize==0.5.1",
      ],
      zip_safe=False)
