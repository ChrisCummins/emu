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
import pytest

import emu
from emu import test


def test_which():
    assert "/bin/bash" == emu.which("bash")
    assert "/bin/bash" == emu.which("/bin/bash")
    assert None == emu.which("not-a-real-command")

def test_which_path():
    assert "/bin/bash" == emu.which("bash", path=("/usr", "/bin"))
    assert None == emu.which("ls", path=("/dev",))
    assert None == emu.which("ls", path=("/not-a-real-path",))
    assert None == emu.which("not-a-real-command", path=("/bin",))

# isroot()
def test_isroot():
    assert False == emu.isroot(os.getcwd())
    assert False == emu.isroot(".")
    assert True == emu.isroot("/usr/..")
    assert True == emu.isroot("/")

# issource()
def test_issource():
    assert False == emu.issource(os.getcwd())
    assert False == emu.issource(".")
    assert False == emu.issource("not-a-directory")
    assert True == emu.issource(test.data_path("source"))
    assert False == emu.issource("tests/data/sink")

# find_source_dir()
def test_find_source_dir():
    assert (os.path.join(os.path.abspath(test.data_path("source"))) ==
            emu.find_source_dir(test.data_path("source")))
    assert (os.path.join(os.path.abspath(test.data_path("source"))) ==
            emu.find_source_dir(test.data_path("source", "directory")))
    with pytest.raises(emu.SourceNotFoundError):
        emu.find_source_dir(test.data_path("sink"), barriers=[os.getcwd()])
        # We expect the search to fail if we give it a bad
        # path. However note that it is intended that the user
        # asserts that a path is good at the calling site, rather
        # than relying on this search to fail.
        emu.find_source_dir("not-a-directory")

# isprocess()
def test_isprocess():
    assert True == emu.isprocess(0)
    assert True == emu.isprocess(os.getpid())
    # We hope there aren't this many processes running!
    assert False == emu.isprocess(10000000)
    assert False == emu.isprocess(10000001)
