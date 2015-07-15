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
import re
import os
from os import path

from optparse import OptionParser

from . import InvalidArgsError
from . import InvalidBranchError
from . import InvalidSnapshotIDError
from . import SinkNotFoundError
from . import SnapshotID
from . import SnapshotNotFoundError
from . import Util


class Error(Exception):
    """
    Base error case.
    """
    pass


class SourceNotFoundError(Error):
    """
    Thrown if an emu source is not found.

    Attributes:

        stopdir (str): The directory in which we stopped searching for
          a source.
    """

    def __init__(self, stopdir):
        """
        Create a source not found error.

        Arguments:

            stopdir (str): The directory at which we stopped searching
              for a source.
        """
        self.stopdir = stopdir

    def __repr__(self):
        return "Not an emu source (or any parent up to {})".format(self.stopdir)

    def __str__(self):
        return self.__repr__()


def isroot(dirpath):
    """
    Return whether a directory is the filesystem root.

    Note that this does not check the argument to ensure that it
    exists.

    Arguments:

        dirpath (str): Path of directory to check.

    Returns:

        bool: True if directory is an emu source, else false.
    """
    parent_dir = path.join(dirpath, os.pardir)
    return path.exists(dirpath) and path.samefile(dirpath, parent_dir)


def issource(dirpath):
    """
    Return whether a directory is an emu source.

    Note that this does not check the argument to ensure that it
    exists.

    Arguments:

        dirpath (str): Path of directory to check.

    Returns:

        bool: True if directory is an emu source, else false.
    """
    # TODO: Check for the presence of additional files which are known
    # to exist in an emu dir.
    emudir = path.join(dirpath, ".emu")
    sinksdir = path.join(emudir, "sinks")
    return path.isdir(emudir) and path.isdir(sinksdir)


def issubdir(left, right):
    """
    Return if a path is a subdirectory of another.

    Arguments:

        left (str): The directory to test.
        right (str): The alleged parent directory.

    Returns:

        bool: True if left is subdirectory of right, else false.
    """
    child_path = path.realpath(left)
    parent_path = path.realpath(right)

    if len(child_path) < len(parent_path):
        return False

    for i in range(len(parent_path)):
        if parent_path[i] != child_path[i]:
            return False

    return True


def can_traverse_up(dirpath, barriers=[]):
    """
    Return whether we can traverse up a directory.

    Arguments:

        dirpath (str): Path of directory to check.
        barriers (list of str, optional): A list of paths which cannot
          be traversed above.

    Returns:

        bool: True if we can traverse up, else false.
    """
    return (path.exists(dirpath) and not isroot(dirpath)
            and not any(issubdir(dirpath, barrier) for barrier in barriers))


def find_source_dir(dirpath, barriers=[]):
    """
    Walk up a tree to find a source's root directory.

    Attempt to determine the source directory by iterating up the
    directory tree starting at a given base.

    Arguments:

        dirpath (str): The path to begin traversing back from.
        barriers (list of str, optional): A list of paths which cannot
          be traversed above.

    Returns:

        str: Absolute path to the source directory.

    Raises:

        SourceNotFoundError: If no source is found.
    """
    if issource(dirpath):
        return path.abspath(dirpath)
    elif can_traverse_up(dirpath, barriers=barriers):
        return find_source_dir(path.join(dirpath, os.pardir))
    else:
        raise SourceNotFoundError(dirpath)


def _parse_snapshot_id(string, sink):
    regex = (r"((?P<id>[a-f0-9]{40})|"
             "(?P<head>HEAD)|"
             "(?P<tail>TAIL))"
             "(?P<n_index>~([0-9]+)?)?")

    match = re.match(regex, string)

    if not match:
        raise InvalidSnapshotIDError(arg)

    # Regex components:
    id_match = match.group("id")
    head_match = match.group("head")
    tail_match = match.group("tail")
    n_index_match = match.group("n_index")

    # Resolve tilde index notation:
    n_index = 0
    if n_index_match:
        n_index = Util.tilde_to_n_index(n_index_match)

    # Match snapshot identifier:
    if id_match:
        # If there's an ID, then match it:
        id = SnapshotID(sink.name, id_match)
        snapshot = Util.get_snapshot_by_id(id, sink.snapshots())
        return snapshot.nth_parent(n_index, error=True)

    elif head_match:
        # Calculate the HEAD index and traverse:
        head = sink.head()
        if head:
            return head.nth_parent(n_index, error=True)

    elif tail_match:
        # Calculate the TAIL index and traverse
        tail = sink.tail()

        if tail:
            return tail.nth_child(n_index, error=True)

    else:
        raise InvalidSnapshotIDError(arg)


def _parse_arg(arg, source, accept_sink_names=True):
    #_parse_snapshot_id(string, sink)

    regex = (r"^(?P<sink>[a-zA-Z]+)"
             "(:(?P<src>([a-f0-9]{40}|HEAD|TAIL)(~[0-9]*)?)"
             "(?P<branch>.."
             "(?P<dst>([a-f0-9]{40}|HEAD|TAIL)(~[0-9]*)?)?)?)?")

    match = re.match(regex, arg)

    if not match:
        raise InvalidSnapshotIDError(arg)

    # Regex components:
    sink_match = match.group("sink")
    src_match = match.group("src")
    branch_match = match.group("branch")
    dst_match = match.group("dst")

    sink = Util.get_sink_by_name(sink_match, source.sinks())

    snapshots = []
    src, dst = None, None

    if src_match:
        src = _parse_snapshot_id(src_match, sink)
        snapshots.append(src)
    elif accept_sink_names:
        return sink.snapshots()
    else:
        raise InvalidArgsError("One or more snapshots must be "
                               "specified using "
                               "<sink>:<snapshot>")

    if dst_match:
        dst = _parse_snapshot_id(dst_match, sink)

    # If we have a ".." suffix to indicate branch notation, then
    # we start from the indicated node and work back, creating a
    # branch history.
    if branch_match:

        # We start from the indicated node and work back, stopping
        # if/when we reach the terminating snapshot.
        node = src.parent()
        while node and node != dst:
            snapshots.append(node)
            node = node.parent()

        # If the last snapshot doesn't match the terminating
        # snapshot, then we were unable to create a branch
        # history.
        if dst and snapshots[-1].parent() != dst:
            raise InvalidBranchError(src, dst)

    if dst:
        snapshots.append(dst)

    return snapshots


class Parser(OptionParser):
    """
    Command line option parser.
    """

    def __init__(self):
        # Instantiate superclass
        OptionParser.__init__(self, add_help_option=False)

        # We allow user to override the default handlers by adding
        # their own:
        self.set_conflict_handler("resolve")

        # Set default parser arguments:
        self.add_option("-S", "--source-dir", action="store", type="string",
                        dest="source_dir",
                        default=find_source_dir(os.getcwd()))
        self.add_option("--version", action="callback",
                        callback=Util.version_and_quit)
        self.add_option("-v", "--verbose", action="store_true",
                        dest="verbose", default=False)
        self.add_option("-h", "--help", action="callback",
                        callback=Util.help_and_quit)

    def options(self, *options):
        """
        Set/Get the parser options.
        """
        if options:
            self._options = options

        try:
            return self._options
        except AttributeError:
            (self._options, self._args) = self.parse_args()
            return self.options()

    def args(self, *args):
        """
        Set/Get the parser arguments.
        """
        if args:
            self._args = args

        try:
            return self._args
        except AttributeError:
            (self._options, self._args) = self.parse_args()
            return self.args()

    def parse_sinks(self, source, accept_no_args=True, error=True):
        """
        Parse the arguments for sink identifiers.

        Parses the command line arguments and searches for sink
        identifiers, returning a list of Sink objects for each of the
        named sinks. If 'accept_no_args' is True, then if no arguments
        are provided, all sinks will be returned. If an argument does
        not correspond with a sink, then a SinkNotFoundError is
        raised.
        """
        try:
            return self._sinks
        except AttributeError:
            try:

                # Return all sinks if no args:
                if accept_no_args and not len(self.args()):
                    return source.sinks()
                else:
                    # Else parse arguments:
                    self._sinks = []
                    for arg in self.args():
                        self._sinks.append(
                            Util.get_sink_by_name(arg, source.sinks())
                        )
                    return self._sinks

            except SinkNotFoundError as e:
                if error:
                    if hasattr(error, '__call__'):
                        # Execute error callback if provided:
                        error(e)
                    else:
                        # Else fatal error:
                        print e
                        sys.exit(1)
                else:
                    raise e

    def parse_snapshots(self, source, accept_sink_names=True,
                        accept_no_args=True, single_arg=False,
                        require=False, error=True):
        """
        Parse the arguments for snapshot identifiers.

        Parses the command line arguments and searches for snapshot
        IDs, returning a list of Snapshot objects for each of the
        identified snapshots. If 'accept_sink_names' is True, then if
        a sink is only named, then a list of all of its snapshots will
        be used, instead of having to identify a single one. 'If
        'accept_no_args' is True, then a list of all sinks will be
        used if no arguments are provided.
        """
        try:
            return self._snapshots
        except AttributeError:
            try:

                snapshots = []
                args = self.args()

                # Check first if we're only accepting a single arg:
                if single_arg and not len(args) == 1:
                    e = "Only a single argument accepted!"

                    if hasattr(error, '__call__'):
                        # Execute error callback if provided:
                        error(e)
                    else:
                        # Else fatal error:
                        print e
                        sys.exit(1)

                # If no args are given, generate a list of all sink names:
                if accept_no_args and not len(args):
                    for sink in source.sinks():
                        args.append(sink.name)

                # Iterate over each arg, resolving to snapshot(s):
                for arg in args:
                    snapshots += _parse_arg(
                        arg, source, accept_sink_names=accept_sink_names
                    )

                # We don't need to proceed if there are no snapshots:
                if require and not len(snapshots):
                    if len(args) > 0:
                        raise InvalidArgsError("No snapshots found.")
                    else:
                        raise InvalidArgsError("One or more snapshots must be "
                                               "specified using "
                                               "<sink>:<snapshot>")

                # Cast to set and back to remove duplicates:
                snapshots = list(set(snapshots))

                # Sort the snapshots into reverse chronological order:
                snapshots.sort()
                snapshots.reverse()

                self._snapshots = snapshots
                return self._snapshots

            except (InvalidArgsError,
                    SinkNotFoundError,
                    SnapshotNotFoundError) as e:
                if error:
                    if hasattr(error, '__call__'):
                        # Execute error callback if provided:
                        error(e)
                    else:
                        # Else fatal error:
                        print e
                        sys.exit(1)
                else:
                    raise e
