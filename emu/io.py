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
"""
Input output module.

Offers several methods for printing messages of differing
severities. The default values are:

    TYPE       DEST     DEFAULT
    printf     stdout   enabled
    verbose    stdout   disabled
    debug      stdout   disabled
    warning    stderr   enabled
    error      stderr   enabled
    fatal      stderr   enabled

Each type of message is independent. That is, you can enable and
disable specific types to your hearts content. If you only want
debugging messages and no errors, have at it. The one exception is
fatal messages, which cannot be disabled and always result in program
termination.
"""
from __future__ import print_function

from sys import exit,stderr


printf_enabled = True
verbose_enabled = False
debug_enabled = False
warning_enabled = True
error_enabled = True


def enable_printf_messages():
    """
    Enable message printing.
    """
    global printf_enabled
    printf_enabled = True


def disable_printf_messages():
    """
    Disable message printing.
    """
    global printf_enabled
    printf_enabled = False


def printf(*args, **kwargs):
    """
    Print a message.

    Arguments:

        *args, **kwargs: Arguments to be passed to print().
    """
    if printf_enabled:
        print(*args, **kwargs)


def enable_verbose_messages():
    """
    Enable verbose message printing.
    """
    global verbose_enabled
    verbose_enabled = True


def disable_verbose_messages():
    """
    Disable verbose message printing.
    """
    global verbose_enabled
    verbose_enabled = False


def verbose(*args, **kwargs):
    """
    Print a verbose message.

    Arguments:

        *args, **kwargs: Arguments to be passed to print().
    """
    if verbose_enabled:
        print(*args, **kwargs)


def enable_debug_messages():
    """
    Enable debugging message printing.
    """
    global debug_enabled
    debug_enabled = True


def disable_debug_messages():
    """
    Disable debugging message printing.
    """
    global debug_enabled
    debug_enabled = False


def debug(*args, **kwargs):
    """
    Print a debugging message.

    Arguments:

        *args, **kwargs: Arguments to be passed to print().
    """
    if debug_enabled:
        print(*args, **kwargs)


def enable_warning_messages():
    """
    Enable warning message printing.
    """
    global warning_enabled
    warning_enabled = True


def disable_warning_messages():
    """
    Disable warning message printing.
    """
    global warning_enabled
    warning_enabled = False


def warning(*args, **kwargs):
    """
    Print a warning message.

    Arguments:

        *args, **kwargs: Arguments to be passed to print().
    """
    if "file" not in kwargs:
        kwargs["file"] = stderr
    if warning_enabled:
        print(*args, **kwargs)


def enable_error_messages():
    """
    Enable error message printing.
    """
    global error_enabled
    error_enabled = True


def disable_error_messages():
    """
    Disable error message printing.
    """
    global error_enabled
    error_enabled = False


def error(*args, **kwargs):
    """
    Print an error message.

    Arguments:

        *args, **kwargs: Arguments to be passed to print().
    """
    if "file" not in kwargs:
        kwargs["file"] = stderr
    if error_enabled:
        print(*args, **kwargs)


def fatal(*args, **kwargs):
    """
    Print a an error message and quit.

    Never returns.

    Arguments:

        *args, **kwargs: Arguments to be passed to print().
        status (int, optional): Exit status.
    """
    status = kwargs.pop("status", 1)
    if "file" not in kwargs:
        kwargs["file"] = stderr
    print("fatal:", *args, **kwargs)
    exit(status)
