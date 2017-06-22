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
#
import os
import pytest
import sqlite3
import sys
import tarfile

from contextlib import contextmanager
from io import StringIO
from pathlib import Path

import emu
from emu import io


class Data404(Exception):
    pass


# Test decorators:
# ... = pytest.mark.skipif(..., reason="...")


def data_path(*components, exists=True) -> str:
    """
    Return absolute path to unittest data file. Data files are located in
    <package>/test/data.

    Arguments:
        *components (str): Relative path.
        exists (bool, optional): If True, require that file exists.

    Returns:
        str: Absolute path.

    Raises:
        Data404: If path doesn't exist and 'exists' is True.
    """
    path = os.path.join(*components)

    abspath = os.path.join(os.path.dirname(__file__), "data", path)
    if exists and not os.path.exists(abspath):
        raise Data404(abspath)
    return abspath


def data_str(*components) -> str:
    """
    Return contents of unittest data file as a string.

    Arguments:
        *components (str): Relative path.

    Returns:
        str: File contents.

    Raises:
        Data404: If path doesn't exist.
    """
    path = data_path(*components, exists=True)

    with open(data_path(path)) as infile:
        return infile.read()


def archive(*components):
    """
    Returns a text archive, unpacking if necessary.

    Arguments:
        *components (str): Relative path.

    Returns:
        str: Path to archive.
    """
    path = data_path(*components, exists=False)

    if not fs.isdir(path):
        tar.unpack_archive(path + ".tar.bz2")
    return path


class DevNullRedirect(object):
    """
    Context manager to redirect stdout and stderr to devnull.

    Examples:
        >>> with DevNullRedirect(): print("this will not print")
    """
    def __init__(self):
        self.stdout = None
        self.stderr = None

    def __enter__(self):
        self.stdout = sys.stdout
        self.stderr = sys.stderr

        sys.stdout = StringIO()
        sys.stderr = StringIO()

    def __exit__(self, *args):
        sys.stdout = self.stdout
        sys.stderr = self.stderr


@contextmanager
def chdir(path: Path):
    """
    Changes working directory and returns to previous on exit

    By @Lukas http://stackoverflow.com/a/42441759
    """
    prev_cwd = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(prev_cwd)


def module_path():
    return os.path.dirname(emu.__file__)


def coverage_report_path():
    return os.path.join(module_path(), ".coverage")


def coveragerc_path():
    return data_path("coveragerc")


@contextmanager
def test_env():
    """
    Manages the environment used for tests.
    """
    # Setup environment:
    # os.environ[...] = ...

    try:
        yield
    finally:
        # Restore old environment:
        # os.environ[...] = ...
        pass


def testsuite():
    """
    Run the test suite.

    Returns:
        int: Test return code. 0 if successful.
    """
    with test_env():
        with chdir(module_path()):  # run from module directory
            assert os.path.exists(coveragerc_path())

            args = ["--doctest-modules", "--cov=emu",
                    "--cov-config", coveragerc_path()]

            # unless verbose, don't print coverage report
            if io.is_verbose():
                args.append("--verbose")
            else:
                args.append("--cov-report=")

            ret = pytest.main(args)

            assert os.path.exists(coverage_report_path())

        if io.is_verbose():
            print("coverage path:", coverage_report_path())
            print("coveragerc path:", coveragerc_path())

    return ret
