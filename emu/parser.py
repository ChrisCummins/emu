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

from optparse import OptionParser

from . import InvalidArgsError
from . import InvalidBranchError
from . import InvalidSnapshotIDError
from . import SinkNotFoundError
from . import SnapshotID
from . import SnapshotNotFoundError
from . import Util


def _get_source_dir():
    """
    Attempt to determine the source directory, by iterating up the
    directory tree, starting from the current working
    directory. If no source is found, fail.
    """
    base_source_dir = os.getcwd()
    source_dir = base_source_dir
    while True:
        # Check if emu directory exists in current directory:
        emu_dir = Util.concat_paths(source_dir, "/.emu")
        is_source = Util.readable(emu_dir)
        if is_source:
            return source_dir

        # If not, then get the parent directory and repeat:
        new_source_dir = Util.par_dir(source_dir)

        # If the parent and current directories are equal (i.e. we
        # have hit the root of the filesystem), then revert to the
        # default emu source dir from config:
        if new_source_dir == source_dir:
            return None

        source_dir = new_source_dir

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
                        dest="source_dir", default=_get_source_dir())
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
