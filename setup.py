#!/usr/bin/env python2
#
# Copyright 2015 Chris Cummins.
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
from glob import glob
from setuptools import setup


setup(name="emu",
      version="0.1.51",
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
      install_requires=[],
      zip_safe=False)
