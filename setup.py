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
from glob import glob
from setuptools import setup
from setuptools.command.test import test


# Directory to install man pages to.
man_prefix = "/usr/share/man"
man_dir = man_prefix + "/man1/"


# class BlackBoxTests(test):
#     def run(self):
#         from subprocess import call
#         call(['./scripts/run-tests.sh',])
#         test.run(self)


setup(name="emu",
      version="0.2.5",
      description=("Fast, incremental, rotating snapshot backups."),
      url="https://github.com/ChrisCummins/emu",
      author="Chris Cummins",
      author_email="chrisc.101@gmail.com",
      license="MIT",
      packages=["emu"],
      package_data={
          'emu': [
              'templates/sink-templates/config',
              'templates/source-templates/hooks/push/email.error.sample',
              'templates/source-templates/hooks/push/log-start.pre.sample',
              'templates/source-templates/hooks/push/email-report.post.sample',
              'templates/source-templates/hooks/exec/mount-remote.post.sample',
              'templates/source-templates/hooks/exec/log.error.sample',
              'templates/source-templates/hooks/exec/mount-remote.pre.sample',
              'templates/source-templates/excludes',
              'templates/source-templates/config'
          ]
      },
      data_files=[
          (man_dir, [
              'man/emu.1',
              'man/emu-init.1',
              'man/emu-checkout.1',
              'man/emu-sink.1',
              'man/emu-clean.1',
              'man/emu-push.1',
              'man/emu-verify.1',
              'man/emu-squash.1',
              'man/emu-prune.1',
              'man/emu-log.1'
          ])
      ],
      scripts=[
          'bin/emu-checkout',
          'bin/emu-clean',
          'bin/emu-init',
          'bin/emu-log',
          'bin/emu-prune',
          'bin/emu-push',
          'bin/emu',
          'bin/emu-sink',
          'bin/emu-squash',
          'bin/emu-verify'
      ],
      test_suite="nose.collector",
      tests_require=[
          "coverage",
          "nose"
      ],
      #cmdclass = {'test': BlackBoxTests},
      install_requires=[],
      zip_safe=False)
