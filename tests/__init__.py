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
from __future__ import print_function

import unittest

# Extension of unittest's TestCase.
class TestCase(unittest.TestCase):

    @staticmethod
    def _print(obj, **kwargs):
        if hasattr(obj, "__iter__"):
            if isinstance(obj, dict):
                print(obj, **kwargs)
            elif not isinstance(obj, str):
                print([str(x) for x in obj], **kwargs)
        else:
            print(str(obj), **kwargs)

    # A convenience method to assert that expected result equals
    # actual result. The benefit over just calling assertTrue() is
    # that it prints the expected and actual values if the test fails.
    def _test(self, expected, actual, approximate=False, places=7):
        print("Expected: ", end="")
        self._print(expected)
        print("Actual:   ", end="")
        self._print(actual)
        try:
            if approximate:
                self.assertAlmostEqual(expected, actual, places=places)
            else:
                self.assertTrue(actual == expected)
            print("OK\n")
        except AssertionError as e:
            print("FAIL")
            raise(e)
