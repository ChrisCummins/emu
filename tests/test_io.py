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
from unittest import main
from tests import TestCase

import re
import os
from os import path
from StringIO import StringIO

import emu
from emu import io


class TestIO(TestCase):

    # colourise()
    # def test_colourise(self):
    #     self._test("\033[91mHello, World!\033[0m",
    #                io.colourise(io.Colours.RED, "Hello, World!"))

    def _test_output(self, print_fn, enable_fn, disable_fn):
        out = StringIO()
        disable_fn()
        print_fn("foo", file=out)
        self._test("", out.getvalue())

        out = StringIO()
        enable_fn()
        print_fn("foo", file=out)
        self._test("foo\n", out.getvalue())

        out = StringIO()
        disable_fn()
        print_fn("foo", file=out)
        self._test("", out.getvalue())

        out = StringIO()
        enable_fn()
        print_fn("foo", file=out)
        self._test("foo\n", out.getvalue())

    # printf()
    def test_printf(self):
        self._test_output(io.printf,
                          io.enable_printf_messages,
                          io.disable_printf_messages)

    # verbose()
    def test_verbose(self):
        self._test_output(io.verbose,
                          io.enable_verbose_messages,
                          io.disable_verbose_messages)

    # debug()
    def test_debug(self):
        self._test_output(io.debug,
                          io.enable_debug_messages,
                          io.disable_debug_messages)

    # warning()
    def test_warning(self):
        self._test_output(io.warning,
                          io.enable_warning_messages,
                          io.disable_warning_messages)

    # error()
    def test_error(self):
        self._test_output(io.error,
                          io.enable_error_messages,
                          io.disable_error_messages)

    # fatal()
    def test_fatal(self):
        out = StringIO()
        with self.assertRaises(SystemExit) as ctx:
            io.fatal("foo", file=out)
        # Check default return code.
        self.assertEqual(ctx.exception.code, 1)
        self._test("fatal: foo\n", out.getvalue())

    def test_fatal_status(self):
        out = StringIO()
        with self.assertRaises(SystemExit) as ctx:
            io.fatal("foo", file=out, status=10)
        # Check specified return code.
        self.assertEqual(ctx.exception.code, 10)
        self._test("fatal: foo\n", out.getvalue())


if __name__ == '__main__':
    main()
