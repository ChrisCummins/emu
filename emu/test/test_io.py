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
import re

from io import StringIO
from os import path

import emu
from emu import io


def _test_output(print_fn, enable_fn, disable_fn):
    out = StringIO()
    disable_fn()
    print_fn("foo", file=out)
    assert "" == out.getvalue()

    out = StringIO()
    enable_fn()
    print_fn("foo", file=out)
    assert "foo\n" == out.getvalue()

    out = StringIO()
    disable_fn()
    print_fn("foo", file=out)
    assert "" == out.getvalue()

    out = StringIO()
    enable_fn()
    print_fn("foo", file=out)
    assert "foo\n" == out.getvalue()


def test_printf():
    _test_output(io.printf,
                 io.enable_printf_messages,
                 io.disable_printf_messages)


def test_verbose():
    _test_output(io.verbose,
                 io.enable_verbose_messages,
                 io.disable_verbose_messages)


def test_debug():
    _test_output(io.debug,
                 io.enable_debug_messages,
                 io.disable_debug_messages)


def test_warning():
    _test_output(io.warning,
                 io.enable_warning_messages,
                 io.disable_warning_messages)


def test_error():
    _test_output(io.error,
                 io.enable_error_messages,
                 io.disable_error_messages)


def test_fatal():
    out = StringIO()
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        io.fatal("foo", file=out)
    # Check default return code.
    assert pytest_wrapped_e.value.code == 1
    assert "fatal: foo\n" == out.getvalue()


def test_fatal_status():
    out = StringIO()
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        io.fatal("foo", file=out, status=10)
    # Check specified return code.
    assert pytest_wrapped_e.value.code == 10
    assert "fatal: foo\n" == out.getvalue()
