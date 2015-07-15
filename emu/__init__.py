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

import calendar
import time
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import getpass
from ConfigParser import ConfigParser as _ConfigParser

from datetime import datetime
from optparse import OptionParser
from os import path
from pkg_resources import resource_filename
from sys import exit


def print_version_and_quit(*data):
    """
    Print an emu version message and exit.

    Never returns.
    """
    print(Meta.versionstr())
    exit(0)


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


def isprocess(pid, error=False):
    """
    Check that a process is running.

    Arguments:

        pid (int): Process ID to check.

    Returns:

        True if the process is running, else false.
    """
    try:
        # Don't worry folks, no processes are harmed in the making of
        # this system call:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


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

    def __init__(self, source_dir_arg=True):
        # Instantiate superclass
        OptionParser.__init__(self, add_help_option=False)

        # Allow overriding of default handlers:
        self.set_conflict_handler("resolve")

        # Set default parser arguments:
        if source_dir_arg:
            self.add_option("-S", "--source-dir", action="store", type="string",
                            dest="source_dir",
                            default=find_source_dir(os.getcwd()))
        self.add_option("--version", action="callback",
                        callback=print_version_and_quit)
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
                        print(e)
                        exit(1)
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
                        print(e)
                        exit(1)

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
                        print(e)
                        exit(1)
                else:
                    raise e


####################
# Emu source class #
####################
class Source:

    def __init__(self, path):
        if not path:
            print("fatal: Not an emu source (or any parent directory)")
            exit(1)

        self.path = path
        self.lock = Lockfile(Util.concat_paths(self.path, "/.emu/LOCK"))

        def err_cb(e):
            s = "fatal: Malformed emu source"
            if e:
                s += ". {0}".format(e)
            print(s)
            exit(1)

        # Sanity checks:
        Util.readable(self.path,                                      error=err_cb)
        Util.readable(Util.concat_paths(self.path, "/.emu/"),         error=err_cb)
        Util.readable(Util.concat_paths(self.path, "/.emu/config"),   error=err_cb)
        Util.readable(Util.concat_paths(self.path, "/.emu/excludes"), error=err_cb)
        Util.readable(Util.concat_paths(self.path, "/.emu/hooks/"),   error=err_cb)
        Util.readable(Util.concat_paths(self.path, "/.emu/sinks/"),  error=err_cb)


    # checkout() - Restore source to snapshot
    #
    # Transfer the contents of snapshot tree to source directory.
    def checkout(self, snapshot, dry_run=False, force=False, verbose=False):

        def err_cb(e):
            Util.printf("Woops! Something went wrong.",
                        prefix=sink.name, colour=Colours.ERROR)
            if e:
                print(e)

            try:
                sink.lock.unlock(force=force, verbose=True)
                self.lock.unlock(force=force, verbose=True)
            except Exception:
                pass

            Util.printf("Failed to checkout snapshot {0}!"
                        .format(Util.colourise(snapshot.id.id, Colours.GREEN)),
                        prefix=sink.name, colour=Colours.ERROR)

            exit(1)

        print("Checking out {0}".format(snapshot.id))

        sink = snapshot.sink
        exclude = ["/.emu"]
        exclude_from = [Util.concat_paths(self.path, "/.emu/excludes")]

        self.lock.lock(force=force, verbose=verbose)
        sink.lock.lock(force=force, verbose=verbose)

        if not dry_run:
            # Perform file transfer:
            Util.rsync(Util.concat_paths(snapshot.tree, "/"), self.path,
                       dry_run=dry_run, exclude=exclude,
                       exclude_from=exclude_from,
                       delete=True, error=err_cb,
                       verbose=verbose)

        # Set new HEAD:
        sink.head(head=snapshot, dry_run=dry_run, error=err_cb)

        sink.lock.unlock(force=force, verbose=verbose)
        self.lock.unlock(force=force, verbose=verbose)

        print("Source restored from {0}"
              .format(Util.colourise(snapshot.name, Colours.SNAPSHOT_NEW)))


    # sinks() - Get a source's sinks
    #
    # Returns a list of Sink objects.
    def sinks(self):
        try:
            return self._sinks
        except AttributeError:
            try:

                # Generate list of sinks:
                self._sinks = []
                for name in Util.ls(Util.concat_paths(self.path, "/.emu/sinks"),
                                    must_exist=True):
                    self._sinks.append(Sink(name, self))
                return self._sinks

            except SinkNotFoundError as e:
                print(e)
                exit(1)


    # clean() - Clean up the source
    #
    def clean(self, dry_run=False, verbose=False, recursive=False):
        if verbose:
            print("Cleaning source at '{0}'...".format(self.path))

        Util.rm(self.lock.path, dry_run=dry_run, verbose=True)

        # Clean sinks:
        if recursive:
            for sink in self.sinks():
                sink.clean(dry_run=dry_run, verbose=verbose)

        print("Source is clean.")

    def __repr__(self):
        return self.path


    # create() - Create a new source
    #
    # Creates the directory structure and files for an emu source, and
    # returns an instance.
    @staticmethod
    def create(sourcedir, template_dir, verbose=False, force=False):

        # Tidy up in case of error:
        def err_cb(*data):
            Util.rm(source_dir, verbose=verbose)
            raise SourceCreateError(source_dir)

        if not path.exists(sourcedir):
            raise SourceCreateError(sourcedir)

        # Create directory structure
        source_dir = Util.concat_paths(sourcedir, "/.emu")
        directories = ["/", "/hooks", "/sinks"]
        for d in directories:
            Util.mkdir(source_dir + d, mode=0700, verbose=verbose, error=err_cb)

        # Copy template files
        Util.rsync(Util.concat_paths(template_dir, "/"),
                   Util.concat_paths(source_dir, "/"),
                   error=err_cb, archive=True, update=force,
                   verbose=verbose, quiet=not verbose)

        print("Initialised source at '{0}'".format(sourcedir))

        return Source(sourcedir)


#####################
# Emu snapshot sink #
#####################
class Sink:

    def __init__(self, name, source):

        def err_cb(e):
            print("Non-existent or malformed emu sink.")
            if e:
                print(e)
            exit(1)

        self.name = name
        self.source = source
        self.path = Util.read("{0}/.emu/sinks/{1}".format(self.source.path,
                                                           self.name),
                              error=err_cb)
        self.lock = Lockfile(Util.concat_paths(self.path, "/.emu/LOCK"))

        # Sanity checks:
        Util.readable(Util.concat_paths(self.path, "/.emu/"),       error=err_cb)
        Util.readable(Util.concat_paths(self.path, "/.emu/nodes/"), error=err_cb)
        Util.readable(Util.concat_paths(self.path, "/.emu/trees/"), error=err_cb)
        Util.readable(Util.concat_paths(self.path, "/.emu/HEAD"),   error=err_cb)

        config_path = Util.concat_paths(self.path, "/.emu/config")
        self.config = SinkConfig(config_path)


    # snapshots() - Return a list of all snapshots
    #
    def snapshots(self):
        ids = Util.ls(Util.concat_paths(self.path, "/.emu/nodes"), must_exist=True)
        snapshots = []
        for id in ids:
            snapshots.append(Snapshot(SnapshotID(self.name, id), self))
        return snapshots


    # head() - Get/Set the current sink head
    #
    # Returns the snapshot pointed to by the HEAD file, or None if
    # headless. If 'head' is provided, set this snapshot to be the new
    # head. If 'delete' is True, it deletes the current head.
    def head(self, head=None, dry_run=False, delete=False, error=True):
        head_pointer = Util.concat_paths(self.path, "/.emu/HEAD")
        most_recent_link = Util.concat_paths(self.path, "/Most Recent Backup")

        # Option 1 of 3: Set a new HEAD pointer.
        if head:
            old_head = self.head()
            # Check that the new HEAD is different from the current
            # HEAD pointer:
            head_is_different = not old_head or (old_head.id != head.id)

            # If the new HEAD is the same as the current one, then do
            # nothing:
            if not head_is_different:
                return

            # Else write a new HEAD pointer:
            if not dry_run:
                Util.write(head_pointer, head.id.id + "\n",
                           error=error)

                # Create a new "Most Recent Backup" link:
                if path.exists(most_recent_link):
                    Util.rm(most_recent_link, error=error)
                Util.ln_s(head.name, most_recent_link, error=error)

            Util.printf("HEAD at {0}".format(head.id.id),
                        prefix=self.name, colour=Colours.OK)

        # Option 2 of 3: Delete the HEAD pointer, leaving the sink
        #              headless.
        elif delete:
            if not dry_run:
                Util.rm(most_recent_link, error=error)
                Util.write(head_pointer, "", error=error)

            Util.printf("now in headless state",
                        prefix=self.name, colour=Colours.OK)

        # Option 3 of 3: Fetch the HEAD snapshot, or None if headless.
        else:
            pointer = Util.read(head_pointer, error=error)
            if pointer:
                id = SnapshotID(self.name, pointer)
                return Util.get_snapshot_by_id(id, self.snapshots())
            else:
                return None


    # tail() - Return the oldest snapshot in the current branch
    #
    # Traverse each snapshot's parent until we reach a null pointer,
    # starting from the HEAD.
    def tail(self):
        head = self.head()

        if head:
            return head.branch()[-1]
        else:
            return None


    def push(self, force=False, ignore_errors=False, archive=True,
             owner=False, dry_run=False, verbose=False):

        # We fetch the checksum problem first to ensure that if
        # there's any problems with the config, they are discovered
        # now:
        checksum_program = self.config.checksum_program()

        # Remove old snapshots first:
        i = len(self.snapshots())
        while i >= self.config.max_snapshots():
            self.snapshots()[0].destroy(dry_run=dry_run, force=force,
                                        verbose=verbose)
            if dry_run:
                i -= 1
            else:
                i = len(self.snapshots())

        Util.printf("pushing snapshot ({0} of {1})"
                    .format(len(self.snapshots()) + 1, self.config.max_snapshots()),
                    prefix=self.name, colour=Colours.OK)
        Snapshot.create(self, force=force, ignore_errors=ignore_errors,
                        archive=archive, owner=owner, dry_run=dry_run,
                        checksum_program=checksum_program,
                        verbose=verbose)

        return 0

    # squash() - Merge multiple snapshots
    #
    def squash(self, snapshots, dry_run=False, force=False, verbose=False):

        # Sanity check to ensure that target snapshots are all from
        # this sink:
        for snapshot in snapshots:
            if snapshot.sink != self:
                print("fatal: Cannot merge snapshots across multiple sinks.")
                exit(1)

        # Return if we have nothing to do:
        if len(snapshots) < 2:
            Util.printf("nothing to squash",
                        prefix=self.name, colour=Colours.OK)
            return

        # Merge target snapshots into staging area:
        for snapshot in snapshots:
            link_dests = []
            for other in snapshots[-20:]:
                if other != snapshot:
                    link_dests.append(other.tree)

            Util.printf("merging snapshot {0}"
                        .format(Util.colourise(snapshot.name,
                                               Colours.SNAPSHOT_NEW)),
                        prefix=self.name, colour=Colours.OK)
            Util.rsync(Util.concat_paths(snapshot.tree, "/"),
                       Util.concat_paths(self.path, "/.emu/trees/new"),
                       dry_run=dry_run, link_dest=link_dests,
                       error=True, verbose=verbose, quiet=not verbose)

        # Check that merge was successful:
        new_tree = Util.concat_paths(self.path, "/.emu/trees/new")
        if not dry_run and not os.path.exists(new_tree):
            print("Failed to create new tree " + new_tree)
            exit(1)

        Util.printf("merged {0} snapshots".format(len(snapshots)),
                    prefix=self.name, colour=Colours.OK)

        # Then destroy all of the merged snapshots:
        for snapshot in snapshots:
            snapshot.destroy(dry_run=dry_run, force=force, verbose=verbose)

        # Now create a snapshot from merging tree:
        snapshot = Snapshot.create(self, resume=True, force=force,
                                   dry_run=dry_run, verbose=verbose)

        # Set new HEAD:
        self.head(head=snapshot, dry_run=dry_run)


    # destroy() - Remove a sink from source
    #
    # Note that this only removes the sink pointer from the source,
    # it does not modify the sink.
    def destroy(self, force=False, verbose=False):
        source = self.source

        source.lock.lock(force=force, verbose=verbose)
        self.lock.lock(force=force, verbose=verbose)

        # Delete sink pointer:
        Util.rm("{0}/.emu/sinks/{1}".format(source.path, self.name),
                must_exist=True, error=True, verbose=verbose)

        print("Removed sink {0}".format(Util.colourise(self.name,
                                                       Colours.RED)))

        self.lock.unlock(force=force, verbose=verbose)
        source.lock.unlock(force=force, verbose=verbose)


    # clean() - Clean up the sink
    #
    def clean(self, dry_run=False, verbose=False):
        if verbose:
            print("Cleaning sink {0} at '{1}'..."
                  .format(Util.colourise(self.name, Colours.BLUE), self.path))

        Util.rm(self.lock.path, dry_run=dry_run, verbose=True)

        # Check for orphan node files:
        trees = Util.ls(Util.concat_paths(self.path, "/.emu/trees"))
        for f in Util.ls(Util.concat_paths(self.path, "/.emu/nodes")):
            if f not in trees:
                path = Util.concat_paths(self.path, "/.emu/nodes/", f)

                if not dry_run:
                    Util.rm(path, must_exist=True)
                print("Deleted orphan node file '{0}'"
                      .format(Util.colourise(path, Colours.RED)))

        # Check for orphan trees:
        nodes = Util.ls(Util.concat_paths(self.path, "/.emu/nodes"))
        for f in Util.ls(Util.concat_paths(self.path, "/.emu/trees")):
            if f not in nodes:
                path = Util.concat_paths(self.path, "/.emu/trees/", f)

                if not dry_run:
                    Util.rm(path, must_exist=True)
                print("Deleted orphan tree '{0}'"
                      .format(Util.colourise(path, Colours.RED)))

        # Delete broken symlinks in sink:
        for f in Util.ls(self.path):
            path = "{0}/{1}".format(self.path, f)

            if os.path.islink(path):
                try:
                    # Compose absolute path of link destination:
                    dst = "{0}/{1}".format(self.path, os.readlink(path))

                    # Delete link if link destination doesn't exist:
                    if not os.path.exists(dst):
                        if not dry_run:
                            os.unlink(path)
                        print("Deleted broken symlink '{0}'"
                              .format(Util.colourise(path, Colours.RED)))
                except Exception as e:
                    pass

        # Check for orphan HEAD:
        head_pointer = Util.concat_paths(self.path, "/.emu/HEAD")
        pointer = Util.read(head_pointer)
        head_node = Util.concat_paths(self.path, "/.emu/nodes/", pointer)
        if not os.path.exists(head_node):
            print("Deleted orphan HEAD '{0}'"
                  .format(Util.colourise(pointer, Colours.RED)))
            self.head(delete=True, dry_run=dry_run)

        print("Sink {0} is clean."
              .format(Util.colourise(self.name, Colours.BLUE)))


    def __str__(self):
        return "{0}  {1}".format(self.name, self.path)


    # create() - Create a new sink
    #
    # Creates the directory structure and files for an emu sink, and
    # returns an instance.
    @staticmethod
    def create(source, name, path, template_dir, archive=True,
               ignore_errors=False, verbose=False, force=False):

        # Tidy up in case of error:
        def err_cb(e):
            if e:
                print(e)
            try:
                Util.rm(emu_dir, verbose=False)
            except Exception:
                pass
            try:
                source.lock.unlock(force=force, verbose=False)
            except Exception:
                pass
            exit(1)

        # Create sink directory if required:
        Util.mkdir(path, verbose=verbose, error=err_cb)

        # Check that sink directory exists:
        if not os.path.exists(path):
            err_cb(Error("Path does not exist " + path))
        Util.writable(path, error=err_cb)

        regex = r"^[a-zA-Z]+$"
        if not re.match(regex, name):
            err_cb("Invalid sink name {0}!\n\n"
                   "Sink names must consist solely of letters A-Z."
                   .format(Util.colourise(name, Colours.ERROR)))

        # Resolve relative paths:
        path = os.path.abspath(path)

        # Check that there isn't already an identical sink:
        for sink in source.sinks():
            if sink.name == name:
                err_cb("A sink named {0} already exists!"
                       .format(Util.colourise(name, Colours.ERROR)))
            if sink.path == path:
                err_cb("Sink {0} is already at '{1}'!"
                       .format(Util.colourise(sink.name, Colours.ERROR),
                               path))

        source.lock.lock(force=force, verbose=verbose)

        # Create directory structure:
        emu_dir = Util.concat_paths(path, "/.emu")
        directories = ["/", "/trees", "/nodes"]
        for d in directories:
            Util.mkdir(Util.concat_paths(emu_dir, d), mode=0700,
                       verbose=verbose, error=err_cb)

        # Ignore rsync errors if required:
        if ignore_errors:
            rsync_error = False
        else:
            rsync_error = err_cb

        # Copy template files:
        Util.rsync(Util.concat_paths(template_dir, "/"),
                   Util.concat_paths(emu_dir, "/"),
                   error=rsync_error, archive=archive, update=force,
                   verbose=verbose, quiet=not verbose)

        # Create HEAD:
        Util.write(Util.concat_paths(emu_dir, "/HEAD"), "", error=err_cb)

        # Create pointer:
        Util.write("{0}/.emu/sinks/{1}".format(source.path, name),
                   path + "\n", error=err_cb)

        source.lock.unlock(force=force, verbose=verbose)

        print(("Initialised sink {0} "
               "at '{1}'").format(Util.colourise(name, Colours.INFO), path))

        return Sink(name, source)


#########################
# Source snapshot class #
#########################
class Snapshot:

    def __init__(self, id, sink):

        tree_path = Util.concat_paths(sink.path, "/.emu/trees/", id.id)
        node_path = Util.concat_paths(sink.path, "/.emu/nodes/", id.id)

        self.id = id
        self.sink = sink

        self.tree = tree_path
        self.node = Node(node_path)
        self.name = self.node.name()

        def err_cb(e):
            print("Non-existent or malformed snapshot '{0}'".format(self.id))
            if e:
                print(e)
            exit(1)

        # Sanity checks:
        Util.readable(Util.concat_paths(self.sink.path, "/", self.name),
                      error=err_cb)
        Util.readable(Util.concat_paths(self.sink.path, "/.emu/trees/", self.id.id),
                      error=err_cb)


    # verify() - Verify the contents of snapshot
    #
    # Verify the checksum by computing it again and comparing. The
    # result of this verification is then cached in the node, under
    # the "Tree" section:
    #
    #   [Tree]
    #   Status: (CLEAN|DIRTY)
    #   Last-Verified: <timestamp>
    #
    # If "cache_results" is true, then update nodes with verification
    # results. If "use_cached" is True, then retrieve these values
    # from the node (if present).
    def verify(self, cache_results=True, use_cached=False):

        if use_cached and self.node.has_status():
            return self.node.status()

        else:

            # We compute a new checksum and compare that against the
            # ID:
            program = self.node.checksum_program()
            worker_thread = Checksum(self.tree, program=program)
            clean = worker_thread.get() == self.id.checksum

            # Update the node with status and last-verified info:
            if cache_results:
                date = Date()
                self.node.status(value=clean)
                self.node.last_verified(value=date)

            return clean


    # nth_parent() - Return the nth parent of snapshot
    #
    # Traverse each snapshot's parent until we have travelled 'n'
    # nodes from the starting point.
    def nth_parent(self, n, truncate=False, error=False):
        parent = self.parent()

        try:

            if n > 0:
                if parent:
                    return parent.nth_parent(n - 1, truncate=truncate,
                                             error=error)
                elif not truncate:
                    id = SnapshotID(self.sink.name,
                                    self.id.id + Util.n_index_to_tilde(n))
                    raise SnapshotNotFoundError(id)
                else:
                    return self
            else:
                return self

        except SnapshotNotFoundError as e:
            if error:
                if hasattr(error, '__call__'):
                    # Execute error callback if provided:
                    error(e)
                else:
                    # Else fatal error:
                    print(e)
                    exit(1)
            else:
                raise e


    # branch() - Return every snapshot in branch as array
    #
    # Traverse each snapshot's parent, returning an ordered array
    # starting the current snapshot (self), and each successive
    # parent snapshot.
    def branch(self):
        branch = [self]

        current = self
        next = self.parent()

        while next:
            branch.append(next)
            current = next
            next = next.parent()

        return branch


    # nth_child() - Return the nth child of snapshot
    #
    # Traverse each snapshot's child until we have travelled 'n' nodes
    # from the starting point.
    def nth_child(self, n, truncate=False, error=False):
        head = self.sink.head()

        if not head:
            id = SnapshotID(self.sink.name, "HEAD")
            raise SnapshotNotFoundError(id)

        branch = head.branch()

        # Iterate over snapshots in order to get the index of self:
        index_of_self = None
        i = 0
        for snapshot in branch:
            if snapshot == self:
                index_of_self = i
                break
            else:
                i += 1

        try:
            if index_of_self == None:
                # If we have no "index_of_self", then the snapshot is not
                # in the branch:
                raise SnapshotNotFoundError(self.id)

            if n >= len(branch):
                # Out of range check:
                raise IndexError

            return branch[index_of_self - n]
        except IndexError:
            id = SnapshotID(self.sink.name, "TAIL~{0}".format(n))
            raise SnapshotNotFoundError(id)


    # parent() - Get/set snapshot's parent
    #
    def parent(self, value=None, delete=False):
        if value != None:
            self.node.parent(value=value.id.id)
        elif delete:
            self.node.parent(value="")
        else:
            parent_id = self.node.parent()

            if parent_id:
                return Snapshot(SnapshotID(self.sink.name, parent_id), self.sink)
            else:
                return None


    # destroy() - Destroy a snapshot
    #
    # If 'dry_run' is True, don't make any actual changes. If 'force'
    # is True, ignore locks.
    def destroy(self, dry_run=False, force=False, verbose=False):
        Util.printf("removing snapshot {0}"
                    .format(Util.colourise(self.name, Colours.SNAPSHOT_DELETE)),
                    prefix=self.sink.name, colour=Colours.OK)

        sink = self.sink

        # We don't actually need to modify anything on a dry run:
        if dry_run:
            return

        sink.lock.lock(force=force, verbose=verbose)

        # If current snapshot is HEAD, then set parent HEAD:
        head = sink.head()
        if head and head.id == self.id:
            new_head = head.parent()

            # Remove old "Most Recent Backup" link:
            Util.rm(Util.concat_paths(sink.path, "/Most Recent Backup"),
                    verbose=verbose)

            if new_head:
                # Update head:
                sink.head(head=new_head, dry_run=dry_run)
            else:
                # Remove head:
                sink.head(delete=True, dry_run=dry_run)

        # Re-allocate parent references from all other snapshots:
        new_parent = self.parent()
        for snapshot in sink.snapshots():
            parent = snapshot.parent()
            if parent and parent.id == self.id:
                if new_parent:
                    snapshot.parent(value=new_parent)
                else:
                    snapshot.parent(delete=True)

        # Delete snapshot files:
        Util.rm(Util.concat_paths(sink.path, "/", self.name),
                must_exist=True, error=True, verbose=verbose)
        Util.rm(self.tree, must_exist=True, error=True, verbose=verbose)
        Util.rm("{0}/.emu/nodes/{1}".format(sink.path, self.id.id),
                must_exist=True, error=True, verbose=verbose)

        sink.lock.unlock(force=force, verbose=verbose)


    # diff() - Compare snapshot checksums
    #
    # Returns True if other snapshot has identical checksum.
    def diff(self, other):
        return self.id.checksum == other.id.checksum


    def __repr__(self):
        return str(self.id)

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        try:
            return self.id == other.id
        except AttributeError:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        try:
            return self.id > other.id
        except AttributeError:
            return False

    def __ge__(self, other):
        try:
            return self.id >= other.id
        except AttributeError:
            return False

    def __lt__(self, other):
        try:
            return self.id < other.id
        except AttributeError:
            return False

    def __le__(self, other):
        try:
            return self.id <= other.id
        except AttributeError:
            return False

    # create() - Create a new snapshot
    #
    # If 'force' is True, ignore locks. If 'dry_run' is True, don't
    # make any actual changes. If 'resume' is True then don't perform
    # the file transfer from source to staging area.
    @staticmethod
    def create(sink, resume=False, transfer_from_source=True, force=False,
               ignore_errors=False, archive=True, owner=True,
               checksum_program="sha1sum", dry_run=False, verbose=False):

        # If two snapshots are created in the same second and with the
        # same checksum, then their IDs will be identical. To prevent
        # this, we need to wait until the timestamp will be different.
        def _get_unique_id(checksum):
            # Generate an ID from date and checksum:
            date = Date()
            id = SnapshotID(sink.name, date.hex() + checksum)
            try:
                # See if a snapshot with that ID already exists:
                Util.get_snapshot_by_id(id, sink.snapshots())
                # If id does, wait for a bit and try again:
                time.sleep(0.05)
                return _get_unique_id(checksum)
            except SnapshotNotFoundError:
                # If the ID is unique, return it:
                return (id, date)

        def err_cb(e):
            Util.printf("Woops! Something went wrong.",
                        prefix=sink.name, colour=Colours.ERROR)
            if e:
                print(e)

            # Tidy up any intermediate files which may have been created:
            try:
                Util.rm(name_link, verbose=True)
            except Exception:
                pass
            try:
                Util.rm(tree, verbose=True)
            except Exception:
                pass
            try:
                Util.rm(node_path, verbose=True)
            except Exception:
                pass
            try:
                if sink.head().id == id:
                    sink.head(delete=true, verbose=True)
            except Exception:
                pass
            try:
                source.lock.unlock(force=force, verbose=True)
                sink.lock.unlock(force=force, verbose=True)
            except Exception:
                pass
            try:
                if source.head().id == id:
                    source.head(delete=True)
            except Exception:
                pass

            Util.printf("Failed to create new snapshot!",
                        prefix=sink.name, colour=Colours.ERROR)
            exit(1)

        source = sink.source
        staging_area = Util.concat_paths(sink.path, "/.emu/trees/new")
        exclude = ["/.emu"]
        exclude_from = [Util.concat_paths(source.path, "/.emu/excludes")]
        link_dests = []

        source.lock.lock(force=force, verbose=verbose)
        sink.lock.lock(force=force, verbose=verbose)

        # Ignore rsync errors if required:
        if ignore_errors:
            rsync_error = False
        else:
            rsync_error = err_cb

        if not resume:
            # Use up to 20 of the most recent snapshots as link
            # destinations:
            for snapshot in sink.snapshots()[-20:]:
                link_dests.append(snapshot.tree)

            # Perform file transfer:
            transfer_time = Util.rsync(Util.concat_paths(source.path, "/"),
                                       staging_area, archive=archive,
                                       owner=owner, dry_run=dry_run,
                                       link_dest=link_dests, exclude=exclude,
                                       exclude_from=exclude_from, delete=True,
                                       delete_excluded=True, error=rsync_error,
                                       verbose=verbose)

            # Print "transfer complete" message:
            if transfer_time > 10:
                Util.printf(("File transfer complete ({time:.2f}s), "
                             "creating snapshot.".format(time=transfer_time)),
                            prefix=sink.name, colour=Colours.INFO)

        # Assert that we have a staging area to work with:
        if not dry_run:
            Util.readable(staging_area, error=err_cb)

        if dry_run:
            checksum = "0" * 32
        else:
            # Create worker threads to compute the snapshot checksum
            # and disk usage:
            checksum_t = Checksum(staging_area, program=checksum_program,
                                  verbose=verbose)
            du_t = DiskUsage(staging_area, verbose=verbose)

            # Blocking:
            checksum = checksum_t.get()
            size = du_t.get()

        (id, date) = _get_unique_id(checksum)
        name = date.snapshotfmt()
        tree = Util.concat_paths(sink.path, "/.emu/trees/", id.id)
        name_link = Util.concat_paths(sink.path, "/", name)

        if not dry_run:
            # Move tree into position
            Util.mv(staging_area, tree,
                    verbose=verbose, must_exist=True, error=err_cb)

            # Make name symlink:
            Util.ln_s(".emu/trees/{0}".format(id.id),
                      name_link, verbose=verbose, error=err_cb)

        # Get parent node ID:
        if sink.head():
            head_id = sink.head().id.id
        else:
            head_id = ""

        if not dry_run:
            # Create node:
            node_path = "{0}/.emu/nodes/{1}".format(sink.path, id.id)
            node = _ConfigParser()
            node.add_section("Snapshot")
            node.set("Snapshot", "snapshot",      id.id)
            node.set("Snapshot", "parent",        head_id)
            node.set("Snapshot", "name",          name)
            node.set("Snapshot", "date",          date)
            node.set("Snapshot", "checksum",      checksum_program)
            node.set("Snapshot", "size",          size)
            node.add_section("Tree")
            node.add_section("Sink")
            node.set("Sink",     "source",        sink.source.path)
            node.set("Sink",     "sink",          id.sink_name)
            node.set("Sink",     "path",          sink.path)
            node.set("Sink",     "snapshot-no",   len(sink.snapshots()) + 1)
            node.set("Sink",     "max-snapshots", sink.config.max_snapshots())
            node.add_section("Emu")
            node.set("Emu",      "emu-version",   Meta.version)
            node.set("Emu",      "user",          getpass.getuser())
            node.set("Emu",      "uid",           os.getuid())
            with open(node_path, "wb") as node_file:
                node.write(node_file)

        # Update HEAD:
        if not dry_run:
            snapshot = Snapshot(SnapshotID(sink.name, id.id), sink)
            sink.head(head=snapshot, dry_run=dry_run, error=err_cb)

        source.lock.unlock(force=force, verbose=verbose)
        sink.lock.unlock(force=force, verbose=verbose)

        Util.printf("new snapshot {0}"
                    .format(Util.colourise(name, Colours.SNAPSHOT_NEW)),
                    prefix=sink.name, colour=Colours.OK)

        if not dry_run:
            return snapshot


#####################################
# Unique global snapshot identifier #
#####################################
class SnapshotID:
    def __init__(self, sink_name, id):
        self.sink_name = sink_name
        self.id = id
        self.timestamp = id[:8]
        self.checksum = id[8:]

    def __repr__(self):
        return self.sink_name + ":" + self.id

    def __key__(self):
        return (self.sink_name, self.id)

    def __hash__(self):
        return hash(self.__key__())

# Snapshot IDs can be compared using the standard operators. Snapshots
# are first sorted alphabetically by sink, then chronologically by timestamp.

    def __eq__(self, other):
        if other.id:
            return self.id == other.id and self.sink_name == other.sink_name
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        # If snapshots have same sink, sort chronologically:
        if self.sink_name == other.sink_name:
            date, other_date = int(self.timestamp, 16), int(other.timestamp, 16)
            return date > other_date
        # Else sort alphabetically:
        else:
            sinks = [self.sink_name, other.sink_name]
            sinks.sort()
            if sinks[0] == self.sink_name:
                return True
            else:
                return False

    def __ge__(self, other):
        return self.__gt__(other) or self.__eq__(other)

    def __lt__(self, other):
        return not self.__ge__(other)

    def __le__(self, other):
        return self.__lt__(other) or self.__eq__(other)


#################################
# Three digit version numbering #
#################################
class Version:

    def __init__(self, major, minor, micro, dirty=False):
        self.major = major
        self.minor = minor
        self.micro = micro
        self.dirty = dirty


    def __repr__(self):
        s = "{0}.{1}.{2}".format(self.major, self.minor, self.micro)
        if self.dirty:
            s += "*"
        return s

    # Numerical comparison operators:
    def __eq__(self, other):
        return (self.major == other.major and
                self.minor == other.minor and
                self.micro == other.micro and
                self.dirty == other.dirty)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        if self.major > other.major:
            return True
        elif self.minor > other.minor:
            return True
        else:
            return self.micro > other.micro

    def __ge__(self, other):
        return self.__gt__(other) or self.__eq__(other)

    def __lt__(self, other):
        return not self.__ge__(other)

    def __le__(self, other):
        return self.__lt__(other) or self.__eq__(other)


    @staticmethod
    def from_str(string):
        # Regex for matching version strings:
        regex = r"^(?P<major>[0-9]+)\.(?P<minor>[0-9]+)\.(?P<micro>[0-9]+)$"

        # Match version string, or through Version Error if no match:
        match = re.match(regex, string)
        if not match:
            raise VersionError("Invalid version string '{0}'!".format(string))
        major = match.group("major")
        minor = match.group("minor")
        micro = match.group("micro")

        return Version(major, minor, micro)


######################
# Emu metadata class #
######################
class Meta:

    #
    # Version and copyright information:
    #
    version = Version(0, 2, 1, dirty=True)
    copyright = { "start": 2012, "end": 2015, "authors": ["Chris Cummins"]}

    #
    # Template paths:
    #
    templates = resource_filename(__name__, "templates/")
    source_templates = os.path.abspath(templates + "/source-templates")
    sink_templates = os.path.abspath(templates + "/sink-templates")


    @staticmethod
    def versionstr():
        try:
            return Meta._versionstr
        except AttributeError:
            version = Meta.version

            start = Meta.copyright["start"]
            end = Meta.copyright["end"]
            if start != end:
                copyright = "{0}-{1}".format(start, end)
            else:
                copyright = end

            authors = ", ".join(Meta.copyright["authors"])

            # Create version string:
            Meta._versionstr = ("emu version {0}\n"
                                "Copyright (c) {1} {2}"
                                .format(version, copyright, authors))

            return Meta.versionstr()


#######################################
# Standardised emu config file parser #
#######################################
class ConfigParser(_ConfigParser):

    def __init__(self, path):
        _ConfigParser.__init__(self)

        self.path = path

        file_exists = Util.readable(self.path)
        if not file_exists:
            print("fatal: Config file '{0}' not found".format(self.path))
            exit(1)

        self.read(self.path)


    # flush() - Write config properties to disk
    #
    def flush(self):
        with open(self.path, "wb") as config_file:
            self.write(config_file)

    # section() - Set/get items as dictionary
    #
    def section(self, section, value=None):
        # Set a new section:
        if value != None:
            if self.has_section(section):
                self.remove_section()
            self.add_section(section)

            for prop, value in values:
                self.add(section, prop, value)

        # Get section:
        else:
            if self.has_section(section):
                return dict(self.items(section))
            else:
                # Else add this section and recurse:
                self.add_section(section)
                return self.section(section)


    def get_string(self, section, prop):
        try:
            return self.get(section, prop)
        except Exception as e:
            print("fatal: No property '{0}:{1}' in config file '{2}'"
                  .format(section, prop, self.path))
            exit(1)


    def set_string(self, section, prop, value):
        self.set(section, prop, str(value))
        self.flush()


    def get_bool(self, section, prop):
        value = self.get_string(section, prop)

        if value.lower() == "true":
            return True
        elif value.lower() == "false":
            return False
        else:
            print("Boolean configuration property '{0}:{1}' in config file "
                  "'{2}' is neither \"true\" or \"false\""
                  .format(section, prop, self.path))
            exit(1)


    def set_bool(self, section, prop, value):
        if value:
            self.set(section, prop, "true")
        else:
            self.set(section, prop, "false")
        self.flush()


    def get_int(self, section, prop):
        try:
            value = self.get_string(section, prop)
            return int(value)
        except ValueError:
            print("fatal: Value '{0}' for configuration property '{0}:{1}' "
                  "in file '{2}' is not an integer"
                  .format(value, section, prop, self.path))
            exit(1)


    def set_int(self, section, prop, n):
        try:
            self.set(section, prop, int(n))
            self.flush()
        except ValueError:
            print("fatal: Value '{0}' for configuration property '{0}:{1}' "
                  "in file '{2}' is not an integer"
                  .format(n, section, prop, self.path))


    def get_status(self, section, prop):
        value = self.get_string(section, prop)

        if value.lower() == "clean":
            return True
        elif value.lower() == "dirty":
            return False
        else:
            print("Configuration property '{0}:{1}' in config file "
                  "'{2}' is neither \"clean\" or \"dirty\""
                  .format(section, prop, self.path))
            exit(1)


    def set_status(self, section, prop, value):
        if value:
            self.set(section, prop, "clean")
        else:
            self.set(section, prop, "dirty")
        self.flush()


    def get_checksum_program(self, section, prop):
        value = self.get_string(section, prop)
        return Util.verify_checksum_program(value)


    def set_checksum_program(self, section, prop, value):
        self.set_string(Util.verify_checksum_program(value))


###########################
# Global Emu config class #
###########################
class UserConfig(ConfigParser):

    @staticmethod
    def _create(path):
        cfg = _ConfigParser()

        # Populate config with default values:
        cfg.add_section("general")
        cfg.set("general", "colour", "true")

        # Write config settings to file:
        with open(path, "wb") as cfg_file:
            cfg.write(cfg_file)


    def __init__(self, path):

        file_exists = Util.readable(path)

        # The first time the user invokes emu, there won't be a config
        # file, so we create one:
        if not file_exists:
            UserConfig._create(path)

        ConfigParser.__init__(self, path)


    # use_colour() - Return True is UI should use colour
    #
    def use_colour(self):
        return self.get_bool("general", "colour")


    # default_source() - Return the default source directory
    #
    def default_source(self):
        s, p = "general", "default-source"

        if self.has_option(s, p):
            return self.get_string(s, p)
        else:
            # Add an empty value if non-existent:
            self.set_string(s, p, "")
            return None


    # TODO: The Emu config class should use a singleton pattern in
    # order to require only one disk read per process.
    @staticmethod
    def instance():
        return UserConfig(os.path.expanduser("~/.emuconfig"))


#############################
# Sink configuration parser #
#############################
class SinkConfig(ConfigParser):

    def __init__(self, path):
        ConfigParser.__init__(self, path)

    def max_snapshots(self, n=None):
        s, p = "Snapshots", "max-number"

        if n != None:
            # Option 1 of 2: Set the maximum number of snapshots.
            self.set_int(s, p, n)
        else:
            # Option 2 of 2: Get the maximum number of snapshots.
            return self.get_int(s, p)


    def checksum_program(self, value=None):
        s, p = "Snapshots", "checksum"

        if value != None:
            # Option 1 of 3: Set the checksum program.
            self.set_checksum_program(s, p, value)
        elif self.has_option(s, p):
            # Option 2 of 3: Get the checksum program.
            return self.get_checksum_program(s, p)
        else:
            # Option 3 of 3: Set default and recurse.
            self.set_checksum_program(s, p, "sha1sum")
            return self.checksum_program()


########################
# Snapshot Node Parser #
########################
class Node(ConfigParser):

    def __init__(self, path):
        ConfigParser.__init__(self, path)


    def name(self):
        s, p ="Snapshot", "name"
        return self.get_string(s, p)


    def has_status(self):
        s, p = "Tree", "Status"
        return self.has_option(s, p)


    def status(self, value=None):
        s, p = "Tree", "Status"

        if value != None:
            self.set_status(s, p, value)
        elif self.has_option(s, p):
            return self.get_status(s, p)
        else:
            return False


    def checksum_program(self, value=None):
        s, p = "Snapshot", "checksum"

        if value != None:
            self.set_checksum_program(s, p, value)
        elif self.has_option(s, p):
            return self.get_checksum_program(s, p)
        else:
            return "sha1sum"


    def last_verified(self, value=None):
        s, p ="Tree", "Last-Verified"

        if value != None:
            self.set_string(s, p, value)
        else:
            self.get_string(s, p)


    def parent(self, value=None):
        s, p = "Snapshot", "parent"

        if value != None:
            self.set_string(s, p, value)
        else:
            return self.get_string(s, p)


##############################################
# Utility static class with helper functions #
##############################################
class Util:
    # readable() - Check that the user has read permissions for path
    #
    # If 'error' is True and 'path' is not readable, then exit fatally
    # with error code. If 'error' is a callback function, then execute
    # it on no read permissions.
    @staticmethod
    def readable(path, error=False):
        if not os.path.exists(path) and error:
            exit(1)
        read_permission = os.access(path, os.R_OK)
        if error and not read_permission:
            e = ("No read permissions for '{0}'!"
                 .format(Util.colourise(path, Colours.ERROR)))

            if hasattr(error, '__call__'):
                # Execute error callback if provided
                error(e)
            else:
                # Else fatal error
                print(e)
                exit(1)
        return read_permission


    # writable() - Check that the user has write permissions for path
    #
    # If 'error' is True and 'path' is not writable, then exit fatally
    # with error code. If 'error' is a callback function, then execute
    # it on no write permissions.
    @staticmethod
    def writable(path, error=False):
        if not os.path.exists(path) and error:
            exit(1)
        write_permission = os.access(path, os.W_OK)
        if error and not write_permission:
            e = ("No write permissions for '{0}'!"
                 .format(Util.colourise(path, Colours.ERROR)))

            if hasattr(error, '__call__'):
                # Execute error callback if provided
                error(e)
            else:
                # Else fatal error
                print(e)
                exit(1)
        return write_permission


    # rm() - Recursively remove files
    #
    # Argument 'error' can either by a boolean that dictates whether
    # to exit fatally on error, or a callback function to execute. If
    # 'must_exist' is True, then error if the file doesn't exist. This
    # function returns boolean on whether a file was deleted or not.
    @staticmethod
    def rm(path, must_exist=False, error=False,
           dry_run=False, verbose=False):
        exists = os.path.exists(path)

        if exists:
            Util.writable(path, error=error)

            try:
                if os.path.islink(path):
                    type = "link"
                    if not dry_run:
                        os.unlink(path)
                elif os.path.isdir(path):
                    type = "directory"
                    if not dry_run:
                        shutil.rmtree(path)
                else:
                    type = "file"
                    if not dry_run:
                        os.remove(path)

                if verbose:
                    print("Deleted {0} '{1}'".format(type, path))
                return True

            # Failed to remove path:
            except Exception as e:
                if hasattr(error, '__call__'):
                    # Execute error callback if provided
                    error(e)
                elif error:
                    # Fatal error if required
                    print("Failed to delete '{0}'."
                          .format(Util.colourise(path, Colours.ERROR)))
                    exit(1)
                else:
                    return False

        # Path does not exist:
        else:
            return False


    # ls() - List a directory's contents
    #
    # Returns an alphabetically sorted list of a directory's contents.
    # Argument 'error' can either by a boolean that dictates whether
    # to exit fatally on error, or a callback function to execute. If
    # 'must_exist' is True, then error if the file doesn't exist.
    @staticmethod
    def ls(path, must_exist=False, error=False):
        exists = os.path.exists(path)
        readable = Util.readable(path, error=error)

        if exists and readable:
            return sorted(os.listdir(path))
        else:
            return []


    # mv() - Move a file
    #
    # Returns true if file is moved, else False. Argument 'error' can
    # either by a boolean that dictates whether to exit fatally on
    # error, or a callback function to execute. If 'must_exist' is
    # True, then error if the file doesn't exist.
    @staticmethod
    def mv(src, dst, must_exist=False, error=False, verbose=False):
        exists = os.path.exists(src)
        readable = Util.readable(src, error=error)

        if exists and readable:
            try:
                shutil.move(src, dst)

                if verbose:
                    print("Moved '{0}' -> '{1}'".format(src, dst))

                return True
            except Exception as e:
                # Error in file move:
                if hasattr(error, '__call__'):
                    # Execute error callback if provided
                    error(e)
                elif error:
                    # Fatal error if required
                    print("Failed to move '{0}' to '{1}'.".format(src, dst))
                    exit(1)
                else:
                    return False

        # Source does not exist or unreadable:
        else:
            return False


    # ln_s() - Create a symbolic link
    #
    # Returns True is symbolic link is created, else False. Argument
    # 'error' can either by a boolean that dictates whether to exit
    # fatally on error, or a callback function to execute.
    @staticmethod
    def ln_s(src, dst, error=False, verbose=False):

        try:
            os.symlink(src, dst)

            if verbose:
                print("Link '{0}' -> '{1}'".format(src, dst))

        except Exception as e:
            # Error in operation:
            if hasattr(error, '__call__'):
                # Execute error callback if provided
                error(e)
            elif error:
                # Fatal error if required
                print("Failed to move '{0}' to '{1}'.".format(src, dst))
                exit(1)


    # mkdir() - Create a directory and all required parents
    #
    # Returns True if directory is created, else False. Argument
    # 'error' can either by a boolean that dictates whether to exit
    # fatally on error, or a callback function to execute.
    @staticmethod
    def mkdir(path, mode=0777, fail_if_already_exists=False,
              error=False, verbose=False):
        exists = os.path.exists(path)

        if exists:
            return False
        else:
            try:
                os.makedirs(path, mode)

                if verbose:
                    print("Created directory '{0}' with mode 0{1:o}"
                          .format(path, mode))

                return True
            except Exception as e:
                # Error in operation:
                if hasattr(error, '__call__'):
                    # Execute error callback if provided
                    error(e)
                elif error:
                    # Fatal error if required
                    print("Failed to create directory '{0}'.".format(path))
                    exit(1)
                else:
                    return False


    # par_dir() - Return parent directory of path
    #
    # Returns the absolute path of a given directory's parent.
    @staticmethod
    def par_dir(path):
        return os.path.abspath(os.path.join(path, os.pardir))


    # concat_paths() - Concatenate a set of paths
    #
    # Joins a set of paths into a single one.
    @staticmethod
    def concat_paths(*paths):
        s = ""
        for path in paths:
            # Don't create paths with two forward slashes: "//".
            if (len(s) and len(path) and
                s[-1] == "/" and path[0] == "/"):
                s += path[1:]
            else:
                s += path
        return s


    # p_exec() - Execute a child subprocess
    #
    # Returns a subprocess instance generated by Popen. If 'wait' is
    # True, process will block until subprocess hash
    # completed. Argument 'error' can either by a boolean that
    # dictates whether to exit fatally on error, or a callback
    # function to execute. The 'stdin', 'stdout', and 'stderr'
    # arguments are handlers for their respective IO streams.
    @staticmethod
    def p_exec(args, stdin=None, stdout=None, stderr=None,
               wait=True, error=False, verbose=False):

        if isinstance(args, basestring):
            args = shlex.split(args)

        if verbose:
            print("Executing '{0}'.".format(" ".join(args)))

        process = subprocess.Popen(args, stdin=stdin, stdout=stdout,
                                   stderr=stderr)

        if wait:
            process.wait()

        if error and process.returncode:
            e = ("Process '{0}' exited with return value {1}."
                 .format(Util.colourise(" ".join(args), Colours.ERROR),
                         Util.colourise(process.returncode, Colours.ERROR)))
            # Error in operation:
            if hasattr(error, '__call__'):
                # Execute error callback if provided
                error(e)
            elif error:
                # Fatal error if required
                print(e)
                exit(1)

        return process


    # rsync() - Execute rsync file transfer and return elapsed time
    #
    # The 'archive', 'update', 'dry_run', 'link_dest', 'delete', and
    # 'delete_excluded' arguments correspond to their respective rsync
    # flags. 'exclude' and 'exclude_from' arguments accept either a
    # list of paths and patterns or a single string.
    @staticmethod
    def rsync(src, dst, archive=True, update=False,
              hard_links=True, keep_dirlinks=True, dry_run=False,
              link_dest=None, owner=True,
              exclude=None, exclude_from=None,
              delete=False, delete_excluded=False, wait=True,
              stdout=None, stderr=None, args=None,
              error=False, verbose=False, quiet=False):

        rsync_flags = ["rsync", "--human-readable", "--recursive"]

        if archive:
            rsync_flags.append("--archive")

        if not owner:
            rsync_flags += ["--no-owner", "--no-group"]

        if update:
            rsync_flags.append("--update")

        if hard_links:
            rsync_flags.append("--hard-links")

        if keep_dirlinks:
            rsync_flags.append("--keep-dirlinks")

        if dry_run:
            rsync_flags += ["--dry-run",
                            "--itemize-changes"]

        if isinstance(link_dest, basestring):
            # Single link dest:
            rsync_flags += ["--link-dest", link_dest]
        elif link_dest:
            # List of link dests:
            for dest in link_dest:
                rsync_flags += ["--link-dest", dest]

        if isinstance(exclude, basestring):
            # Single exclude pattern:
            rsync_flags += ["--exclude", exclude]
        elif exclude:
            # List of exclude patterns:
            for pattern in exclude:
                rsync_flags += ["--exclude", pattern]

        if isinstance(exclude_from, basestring):
            # Single exclude path:
            rsync_flags += ["--exclude-from", exclude_from]
        elif exclude_from:
            # List of exclude paths:
            for path in exclude_from:
                rsync_flags += ["--exclude-from", path]

        if delete:
            rsync_flags.append("--delete")

        if delete_excluded:
            rsync_flags.append("--delete-excluded")

        if args:
            rsync_flags += args

        if not quiet:
            rsync_flags.append("--verbose")

        # Add source and destination operands after flags:
        rsync_flags += [src, dst]

        # Record file transfer start time.
        start_time = time.time()

        # Perform rsync.
        Util.p_exec(rsync_flags, stdout=stdout, stderr=stderr,
                    wait=wait, error=error, verbose=verbose)

        # Return elapsed rsync time.
        return time.time() - start_time


    # read() - Return the contents of a file
    #
    # If 'strip' is True, then strip leading and trailing whitespace
    # from the returned contents.
    @staticmethod
    def read(path, strip=True, error=True):
        Util.readable(path, error=error)
        try:
            with open(path, "r") as f:
                contents = f.read()
                if strip:
                    contents = contents.strip()
                return contents
        except Exception as e:
            if error:
                if hasattr(error, '__call__'):
                    # Execute error callback if provided:
                    error(e)
                else:
                    # Else fatal error:
                    print("Failed to read '{0}'"
                          .format(Util.colourise(path, Colours.ERROR)))
                    exit(1)
            else:
                raise e


    # write() - Write string to a file, overwriting any existing contents
    #
    # If 'strip' is True, then strip leading and trailing whitespace
    # from the returned contents.
    @staticmethod
    def write(path, data, error=True):
        exists = os.path.exists(path)
        if exists:
            Util.writable(path, error=error)

        try:
            with open(path, "w") as f:
                f.write(data)
        except Exception as e:
            if error:
                if hasattr(error, '__call__'):
                    # Execute error callback if provided:
                    error(e)
                else:
                    # Else fatal error:
                    print("Failed to write '{0}'"
                          .format(Util.colourise(path, Colours.ERROR)))
                    exit(1)
            else:
                raise e


    # Look up a sink by name, or raise SinkNotFoundError():
    #
    @staticmethod
    def get_sink_by_name(name, sinks):
        for sink in sinks:
            if sink.name == name:
                return sink

        raise SinkNotFoundError(name)


    # Look up a snapshot by id, or raise SnapshotNotFoundError():
    #
    @staticmethod
    def get_snapshot_by_id(id, snapshots):
        for snapshot in snapshots:
            if snapshot.id == id:
                return snapshot

        raise SnapshotNotFoundError(id)


    # tilde_to_n_index() - Convert tilde notation into an n-index
    #
    # Converts a tilde notation string into its corresponding n-index,
    # e.g. "~" returns 1, "~2" returns 2, etc.
    @staticmethod
    def tilde_to_n_index(tilde):
        if re.match(r"~\d+", tilde):
            return int(re.sub(r"~", "", tilde))
        else:
            return 1


    # n_index_to_tilde() - Convert an n-index into tilde notation
    #
    # Converts an integer n-index into corresponding tilde notation,
    # e.g. 1 returns "~", 2 returns "~2", etc.
    @staticmethod
    def n_index_to_tilde(n_index):
        tilde = ""
        if n_index > 0:
            tilde += "~"
            n_index -= 1
            if n_index:
                tilde += str(n_index)
        return tilde


    @staticmethod
    def verify_checksum_program(program):
        regex = r"^(md5|sha1)sum$"
        if re.search(regex, program.lower()):
            return program
        else:
            print("fatal: Invalid checkum program '{0}'"
                  .format(Util.colourise(program, Colours.ERROR)))
            exit(1)


    # printf() - Format and print a message
    #
    # If both 'colour' and 'prefix' are provided, then colourise only
    # the prefix. If no 'prefix' is provided, colourise the whole
    # message.
    @staticmethod
    def printf(msg, prefix=None, colour=None):

        if prefix:
            if colour:
                prefix = Util.colourise(prefix, colour)

            prefix = "{0}: ".format(prefix)

        print(str(prefix) + msg)


    # colourise() - Colourise a string
    #
    # Returns the given string wrapped in colour escape codes, if this
    # property is enabled in the global configuration file.
    @staticmethod
    def colourise(string, colour):
        if UserConfig.instance().use_colour():
            return colour + str(string) + Colours.RESET
        else:
            return str(string)


    @staticmethod
    def help_and_quit(*data):
        script = sys.argv[0]                # Name of the current script
        basename = os.path.basename(script) # Basename of current script
        cmd = "man {0}".format(basename)    # Man page invocation

        Util.p_exec(cmd, error=True)
        exit(0)


##################
# Lockfile class #
##################
class Lockfile:

    def __init__(self, path):
        self.path = path


    # read() - Return lockfile PID and timestamp
    #
    def read(self):
        contents = Util.read(self.path).split()
        pid = int(contents[0])
        timestamp = datetime.fromtimestamp(int(contents[1]))
        return (pid, timestamp)


    # lock() - Assign lockfile to current process
    #
    def lock(self, force=False, error=True, verbose=False):
        if verbose:
            print("Writing lockfile '{0}'".format(self.path))

        if os.path.exists(self.path) and not force:
            # Error state, lock exists:
            e = LockfileError(self)

            if error:
                if hasattr(error, '__call__'):
                    # Execute error callback if provided:
                    error(e)
                else:
                    # Else fatal error:
                    print(e)
                    exit(1)
            else:
                raise e
        else:
            # No lockfile, create new:
            Util.write(self.path, "{0} {1}\n".format(os.getpid(),
                                                     int(time.time())),
                       error=error)


    # unlock() - Free lockfile from current process
    #
    def unlock(self, force=False, error=True, verbose=False):
        if verbose:
            print("Removing lockfile '{0}'".format(self.path))

        exists = os.path.exists(self.path)
        if exists:
            (pid, timestamp) = self.read()
            owned_by_self = pid == os.getpid()
        else:
            owned_by_self = False

        if owned_by_self or force:
            # Destory lockfile:
            Util.rm(self.path, must_exist=True)
        else:
            # Error state, lock either is owned by different process
            # or does not exist:
            e = LockfileError(self)

            if error:
                if hasattr(error, '__call__'):
                    # Execute error callback if provided:
                    error(e)
                else:
                    # Else fatal error:
                    print(e)
                    exit(1)
            else:
                raise e


#############################
# Date representation class #
#############################
class Date:

    REPR_FORMAT = "%A %B %d %H:%M:%S %Y"
    SNAPSHOT_FORMAT = "{0}-{1:02d}-{2:02d} {3:02d}.{4:02d}.{5:02d}"

    def __init__(self):
        self.date = time.localtime()


    # hex() - Return hex formatted date timestamp
    #
    def hex(self):
        return "{0:x}".format(calendar.timegm(self.date))


    # snapshotfmt() - Return snapshot name formatted date
    #
    def snapshotfmt(self):
        return (self.SNAPSHOT_FORMAT
                .format(self.date.tm_year, self.date.tm_mon, self.date.tm_mday,
                        self.date.tm_hour, self.date.tm_min, self.date.tm_sec))


    def __repr__(self):
        return time.strftime(self.REPR_FORMAT, self.date)


#############################
# Shell escape colour codes #
#############################
class Colours:
    RESET   = '\033[0m'
    GREEN   = '\033[92m'
    YELLOW  = '\033[93m'
    BLUE    = '\033[94m'
    RED     = '\033[91m'

    OK      = GREEN
    INFO    = BLUE
    WARNING = YELLOW
    ERROR   = RED

    SNAPSHOT_DELETE = RED
    SNAPSHOT_NEW    = BLUE
    SNAPSHOT        = GREEN


##################
# Worker threads #
##################
class Checksum():

    def __init__(self, path, program="sha1sum", verbose=False):
        self.verbose = verbose
        self.start = time.time()

        if self.verbose:
            print("Creating {0} checksum worker thread...".format(program))

        # Record the starting working directory:
        cwd = os.getcwd()

        # Set working directory to path:
        os.chdir(path)

        # Create a /dev/null pipe:
        with open(os.devnull, 'w') as devnull:

            # Create processes
            self.p1 = subprocess.Popen(["find", ".", "-type", "f",
                                        "-printf", "'%T@ %p\n'"],
                                       stdout=subprocess.PIPE,
                                       stderr=devnull)
            try:
                self.p2 = subprocess.Popen([program],
                                           stdin=self.p1.stdout,
                                           stdout=subprocess.PIPE)
            except OSError:
                print("Invalid checksum program '{0}'!"
                      .format(Util.colourise(program, Colours.RED)))
                exit(1)

        # Return to previous working directory:
        os.chdir(cwd)


    # get() - Return the path checksum
    #
    def get(self):
        (stdout, stderr) = self.p2.communicate()

        if self.verbose:
            print("Checksum worker thread complete in {0:.1f}s."
                  .format(time.time() - self.start))

        return stdout.split()[0][:32]


class DiskUsage():

    def __init__(self, path, verbose=False):
        self.verbose = verbose
        self.start = time.time()

        if self.verbose:
            print("Creating disk usage worker thread...")

        # Create a /dev/null pipe:
        with open(os.devnull, 'w') as devnull:

            # Create processes
            self.p1 = subprocess.Popen(["du", "--summarize",
                                        "--human-readable", path],
                                       stdout=subprocess.PIPE,
                                       stderr=devnull)


    # get() - Return the disk size
    #
    def get(self):
        (stdout, stderr) = self.p1.communicate()

        if self.verbose:
            print("Disk usage worker thread complete in {0:.1f}s."
                  .format(time.time() - self.start))

        return stdout.split()[0]


###############
# Error types #
###############
class Error(Exception):
    """
    Base error case.
    """
    pass


class InvalidArgsError(Error):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg


class InvalidSnapshotIDError(InvalidArgsError):
    def __init__(self, id):
        self.id = id
    def __str__(self):
        return ("Invalid snapshot identifier '{0}!'"
                .format(Util.colourise(self.id, Colours.ERROR)))


class InvalidBranchError(InvalidArgsError):
    def __init__(self, head, tail):
        self.head = head
        self.tail = tail
    def __str__(self):
        return ("Could not create a branch history between snapshots {0} and {1}!"
                .format(Util.colourise(self.head, Colours.ERROR),
                        Util.colourise(self.tail, Colours.ERROR)))


class SinkNotFoundError(Error):
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return ("Sink '{0}' not found!"
                .format(Util.colourise(self.name, Colours.ERROR)))


class SnapshotNotFoundError(Error):
    def __init__(self, id):
        self.id = id
    def __str__(self):
        return ("Snapshot '{0}:{1}' not found!"
                .format(self.id.sink_name,
                        Util.colourise(self.id.id, Colours.ERROR)))


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
        self.stopdir = path.abspath(stopdir)

    def __repr__(self):
        return "Not an emu source (or any parent up to {})".format(self.stopdir)

    def __str__(self):
        return self.__repr__()


class SourceCreateError(Error):
    def __init__(self, source_dir):
        self.source_dir = source_dir
    def __str__(self):
        return ("Failed to create source at '{0}'!"
                .format(self.source_dir))


class LockfileError(Error):
    def __init__(self, lock):
        self.lock = lock
    def __str__(self):
        (pid, timestamp) = self.lock.read()
        string = ("Failed to modify lock '{0}'!\n"
                  .format(Util.colourise(self.lock.path, Colours.ERROR)))
        string += ("Lock was claimed by process {0} at {1}.\n"
                   .format(Util.colourise(pid, Colours.INFO),
                           Util.colourise(timestamp, Colours.INFO)))
        if isprocess(pid):
            string += "It looks like the process is still running."
        else:
            string += "It looks like the process is no longer running.\n"
        string += "\nTo ignore this lock and overwrite, use option '--force'."
        return string


class VersionError(Error):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg


###################
# Signal handlers #
###################

# If a Python process is interrupted (Ctrl+C), a KeyboardInterrupt
# exception is thrown. In order to prevent having to wrap *every*
# possible point of interruption in a try-except block, we can
# register a SIGINT handler. In our case, we don't need it to do
# anything other than acknowledge the signal, as the err_cb() methods
# are used for tidying up.
def _sigint_handler(signum, frame):
    print("emu: received SIGINT")
signal.signal(signal.SIGINT, _sigint_handler)