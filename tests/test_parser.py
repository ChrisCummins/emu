# Copyright (C) 2015 Chris Cummins.
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
from unittest import main
from tests import TestCase

import os
from os import path

import emu
from emu import parser


class TestDatabase(TestCase):

    # isroot()
    def test_isroot(self):
        self._test(False, parser.isroot(os.getcwd()))
        self._test(False, parser.isroot("."))
        self._test(True, parser.isroot("/usr/.."))
        self._test(True, parser.isroot("/"))

    # issource()
    def test_issource(self):
        self._test(False, parser.issource(os.getcwd()))
        self._test(False, parser.issource("."))
        self._test(False, parser.issource("not-a-directory"))
        self._test(True, parser.issource("tests/data/source"))
        self._test(False, parser.issource("tests/data/sink"))

    # find_source_dir()
    def test_find_source_dir(self):
        self._test(path.join(path.abspath("tests/data/source")),
                   parser.find_source_dir("tests/data/source"))
        self._test(path.join(path.abspath("tests/data/source")),
                   parser.find_source_dir("tests/data/source/directory"))
        with self.assertRaises(parser.SourceNotFoundError):
            parser.find_source_dir("tests/data/sink",
                                   barriers=[os.getcwd()])
            # We expect the search to fail if we give it a bad
            # path. However note that it is intended that the user
            # asserts that a path is good at the calling site, rather
            # than relying on this search to fail.
            parser.find_source_dir("not-a-directory")


if __name__ == '__main__':
    main()
