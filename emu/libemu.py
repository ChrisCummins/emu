#!/usr/bin/env python
#
# Copyright 2014 Chris Cummins.
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
import calendar
import time
import os
import re
import shlex
import shutil
import subprocess
import sys
from ConfigParser import ConfigParser
from optparse import OptionParser
from sys import exit
from datetime import datetime


class Node:
    def __init__(self, path):
        with open(path, 'r') as f:
            node = f.read()
            self.data = {}
            for l in node.rstrip().split('\n'):
                p = re.split(r"\W+", l, 1)
                self.data[p[0]] = p[1]


class Snapshot:
    def __init__(self, shash, stack_name, stack_dir):
        self.id = shash
        self.stack = stack_name
        self.stack_dir = stack_dir
        self.checksum = self.id[8:]
        self.node = stack_dir + "/.emu/nodes/" + shash
        self.tree = stack_dir + "/.emu/trees/" + shash

        if not (Util.exists(self.node) and os.path.isdir(self.tree)):
            raise SnapshotNotFoundError(SnapshotID(stack_name, shash))

        self.snapshot = self.get_node().data['Snapshot']


    _valid = None
    def verify(self):
        if self._valid == None:
            checksum = Libemu.hash_dir(self.tree)
            self._valid = checksum == self.checksum
        return self._valid

    def __repr__(self):
        return self.stack + ":" + self.id

    def get_node(self):
        try:
            return self._node
        except AttributeError:
            self._node = Node(self.node)
            return self.get_node()

    def log(self, short=False):
        def full_log(id, node):
            s =  "snapshot " + id + "\n"
            s += "Date:    " + node.data['Date'] + "\n"
            s += "Size:    " + node.data['Size'] + "\n"
            return s
        def short_log(id, node):
            s = id + "  " + node.data['Date']
            return s

        node = Node(self.node)
        if short:
            return short_log(self.id, node)
        else:
            return full_log(self.id, node)


    # nth_child() - Return the nth child of snapshot
    #
    # Traverse each snapshot's until we have travelled 'n' nodes from
    # the starting point.
    def nth_child(self, n, truncate=False, error=False):
        parent_id = self.get_node().data["Parent"]

        try:

            if n > 0:
                if parent_id:
                    parent = Snapshot(parent_id, self.stack, self.stack_dir)
                    return parent.nth_child(n - 1, truncate, error)
                elif not truncate:
                    raise SnapshotNotFoundError(SnapshotID(self.stack,
                                                           self.id + Util.n_index_to_tilde(n)))
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
                    print e
                    sys.exit(1)
            else:
                raise e


    def destroy(self, verbose=False):
        Util.printf("destroying snapshot {0}".format(Util.colourise(self.snapshot,
                                                                    Colours.SNAPSHOT_DELETE)),
                    prefix=self.stack, colour=Colours.OK)
        Util.rm(self.tree, must_exist=True, error=True, verbose=verbose)
        Util.rm(self.node, must_exist=True, error=True, verbose=verbose)
        Util.rm(self.stack_dir + "/" + self.snapshot,
                must_exist=True, error=True, verbose=verbose)
        # TODO: Check HEAD and reallocate if necessary
        # TODO: Remove parent references from all other snapshots

    @staticmethod
    def create(stack, dry_run=False, verbose=False):
        head = stack.get_head()
        head_id = ""

        if head:
            link_dest = head.tree
            head_id = head.id
        else:
            link_dest = None

        exclude = [stack.source + "/.emu"]
        exclude_from = [stack.source + "/.emu/excludes"]

        Util.rsync(stack.source + "/", stack.path + "/.emu/trees/new",
                   dry_run=dry_run, link_dest=link_dest,
                   exclude=exclude, exclude_from=exclude_from,
                   delete=True, delete_excluded=True,
                   error=True, verbose=verbose)

        checksum = Libemu.hash_dir(stack.path + "/.emu/trees/new")
        date = time.gmtime()
        sid = "{0:x}".format(calendar.timegm(date)) + checksum
        name = "{0}-{1:02d}-{2:02d} {3:02d}.{4:02d}.{5:02d}".format(date.tm_year,
                                                                    date.tm_mon,
                                                                    date.tm_mday,
                                                                    date.tm_hour,
                                                                    date.tm_min,
                                                                    date.tm_sec)

        # Move tree into position
        Util.mv(stack.path + "/.emu/trees/new", stack.path + "/" + name,
                verbose=verbose, must_exist=True, error=True)

        # Make trees symlink
        Util.ln_s(stack.path + "/" + name, stack.path + "/.emu/trees/" + sid,
                  verbose=verbose, error=True)

        # Get size
        size = Libemu.run("du", "-h", "-s").split()[0]

        # Create node
        with open(stack.path + "/.emu/nodes/" + sid, 'w') as f:
            f.write("Snapshot " + name + "\n" +
                    "Parent   " + head_id + "\n" +
                    "Date     " + time.strftime("%A %B %d %H:%M:%S %Y", date) + "\n" +
                    "Source   " + stack.source + "\n" +
                    "Size     " + size + "\n")

        # Update HEAD
        with open(stack.path + "/.emu/HEAD", 'w') as f:
            f.write(sid + "\n")

        return Snapshot(sid, stack.stack, stack.path)




class Stack:
    re = r"^([^:]+)?(:(([a-f0-9]+)|(HEAD(~([0-9]+)?)?)))?$"

    def _stack(self):
        try:
            return re.sub(self.re, r"\1", self.sid)
        except:
            return ""

    def _snapshot(self):
        try:
            s = re.sub(self.re, r"\3", self.sid)

            # HEAD~ syntax
            if re.match(r"^HEAD.*", s):
                index = 0
                if re.match(r"HEAD~.*", s):
                    index += 1
                    if re.match(r".*\d+", s):
                        index += int(re.sub(r"HEAD~", r"", s)) - 1
                ids = Util.ls(self.path + "/.emu/nodes", must_exist=True)
                try:
                    return ids[index]
                except IndexError:
                    SnapshotNotFoundError(SnapshotID(self.stack, s))

            return s
        except:
            return ""

    def _path(self):
        try:
            pointer = self.source + "/.emu/stacks/" + self.stack
            with open(pointer, 'r') as f:
                path = f.read().strip()
                if not Util.exists(path):
                    raise
                return path
        except:
            raise StackNotFoundError(self.sid)

    def get_snapshots(self):
        if len(self.snapshot):
            ids = [self.snapshot]
        else:
            ids = Util.ls(self.path + "/.emu/nodes", must_exist=True)
        snapshots = []
        for id in ids:
            snapshots.append(Snapshot(id, self.stack, self.path))
        return snapshots


    def get_head(self):
        snapshots = self.get_snapshots()
        if len(snapshots):
            return snapshots[len(snapshots) - 1]


    def get_config(self):
        try:
            return self._config
        except AttributeError:
            self._config = ConfigParser()
            self._config.read(self.path + "/.emu/config")
            return self.get_config()

    def get_config_prop(self, section, prop, err=True):
        try:
            return self.get_config().get(section, prop)
        except:
            if err:
                Util.printf("Error parsing config file!", Colours.ERROR)
                Util.printf("Could not find property '{0}' in section '{1}'".format(prop, section),
                            Colours.ERROR)
                sys.exit(1)
            return ""

    def get_max_snapshots(self):
        try:
            return self._max_snapshots
        except AttributeError:
            self._max_snapshots = int(self.get_config_prop('Snapshots', 'Max Number'))
            return self.get_max_snapshots()

    def get_disk_usage(self):
        try:
            return self._du
        except AttributeError:
            self._du = Libemu.du(self.path)
            return self.get_disk_usage()


    def lock(self, verbose=False):
        return 501


    def unlock(self, verbose=False):
        return 501


    def push(self, dry_run=False, verbose=False):
        self.lock()

        # Remove old snapshots first
        while len(self.get_snapshots()) >= int(self.get_max_snapshots()):
            self.get_snapshots()[0].destroy(verbose)

        Util.printf("pushing snapshot ({0} of {1})".format(len(self.get_snapshots()) + 1,
                                                           self.get_max_snapshots()),
                    prefix=self.stack, colour=Colours.OK)
        snapshot = Snapshot.create(self, verbose=verbose)

        self.unlock()
        Util.printf("HEAD at {0}".format(snapshot.id),
                    prefix=self.stack, colour=Colours.OK)
        Util.printf("new snapshot {0}".format(Util.colourise(snapshot.snapshot,
                                                             Colours.SNAPSHOT_NEW)),
                    prefix=self.stack, colour=Colours.OK)
        return 0


    def __init__(self, snapshot_id, source_dir, allow_snapshot_id=True):

        # Throw an exception if we have get stack:snapshot syntax and
        # we don't want it:
        if re.search(r":", snapshot_id) and not allow_snapshot_id:
            raise StackNotFoundError(snapshot_id)

        self.sid = snapshot_id
        self.source = source_dir
        self.stack = self._stack()
        self.path = self._path()
        self.snapshot = self._snapshot()

    def __str__(self):
        return self.stack + " " + self.path


class SourceCreateError(Exception):
    def __init__(self, source_dir):
        self.source_dir = source_dir
    def __str__(self):
        return "Failed to create source at '{0}'!".format(self.source_dir)


class SourceLockError(Exception):
    def __init__(self, source_dir):
        self.source_dir = source_dir
    def __str__(self):
        return "Failed to lock source '{0}'!".format(self.source_dir)


class Source:
    def __init__(self, source_dir):
        self.path = source_dir
        Util.exists(self.path, error=True)
        Util.exists(self.path + "/.emu", error=True)
        Util.exists(self.path + "/.emu/stacks", error=True)


    def checkout(self, snapshot):
        # TODO: checkout snapshot
        return 501


    def lock(self, verbose=False):
        return 501


    def unlock(self, verbose=False):
        return 501


    # stacks() - Get a source's stacks
    #
    # Returns a list of Stack objects.
    def stacks(self):
        try:
            return self._stacks
        except AttributeError:
            try:

                # Generate list of stacks:
                self._stacks = []
                for name in Util.ls(self.path + "/.emu/stacks", must_exist=True):
                    self._stacks.append(Stack(name, self.path))
                return self._stacks

            except StackNotFoundError as e:
                print e
                sys.exit(1)


    @staticmethod
    def create(path, template_dir, verbose=False, force=False):
        def err_cb(*data):
            Util.rm(source_root, verbose=verbose)
            raise SourceCreateError(source_root)

        # Create directory structure
        source_root = path + "/.emu"
        directories = ["/", "/hooks", "/stacks"]
        for d in directories:
            Util.mkdir(source_root + d, mode=0700, verbose=verbose, error=True)

        # Copy template files
        Util.rsync(template_dir + "/", source_root + "/", error=err_cb,
                   archive=True, verbose=verbose, update=force)

        return Source(path)


class Libemu:

    @staticmethod
    def run(*args):
        proc = subprocess.Popen(args, stdout=subprocess.PIPE)
        out = []
        for line in proc.stdout:
            out.append(line)

        return "\n".join(out)


    @staticmethod
    def die_if_not_source(path):
        if not (os.path.isdir(path + "/.emu") and
                Util.exists(path + "/.emu/config")):
            print "No emu source found!"
            sys.exit(1)


    @staticmethod
    def hash_dir(path):
        command = ("cd {0} && find . -type f -printf '%T@ %p\n' 2>/dev/null | "
                   "grep -v ' ./.emu/' | md5sum | awk '{{print $1}}'").format(path)

        return subprocess.check_output(command, shell=True).rstrip()


#####################################
# Unique global snapshot identifier #
#####################################
class SnapshotID:
    def __init__(self, stack_name, id):
        self.stack_name = stack_name
        self.id = id
        self.timestamp = id[:8]
        self.checksum = id[8:]

    def __str__(self):
        return self.stack_name + ":" + self.id


##############################################
# Utility static class with helper functions #
##############################################
class Util:

    #
    # Version information:
    #
    version = { "major": 0, "minor": 0, "micro": 8 }
    version_string = "{0}.{1}.{2}".format(version["major"],
                                          version["minor"],
                                          version["micro"])


    #
    # Template paths:
    #
    source_templates = os.path.abspath(sys.path[0] + "/../share/emu/templates/source-templates")
    stack_templates = os.path.abspath(sys.path[0] + "/../share/emu/templates/stack-templates")


    # exists() - Check that a path exists
    #
    # If 'error' is True and 'path' does not exist, then exit fatally
    # with error code. If 'error' is a callback function, then execute
    # it on no path existing.
    @staticmethod
    def exists(path, error=False):
        exists = os.path.exists(path)
        if error and not exists:
            if hasattr(err, '__call__'):
                # Execute error callback if provided
                error(e)
            else:
                # Else fatal error
                print "'" + path + "' not found!"
                sys.exit(1)
        return exists


    # readable() - Check that the user has read permissions for path
    #
    # If 'error' is True and 'path' is not readable, then exit fatally
    # with error code. If 'error' is a callback function, then execute
    # it on no read permissions.
    @staticmethod
    def readable(path, error=False):
        read_permission = os.access(path, os.R_OK)
        if error and not read_permission:
            if hasattr(error, '__call__'):
                # Execute error callback if provided
                error(e)
            else:
                # Else fatal error
                print "No read permissions for directory '" + path + "'!"
                sys.exit(1)
        return read_permission


    # writable() - Check that the user has write permissions for path
    #
    # If 'error' is True and 'path' is not writable, then exit fatally
    # with error code. If 'error' is a callback function, then execute
    # it on no write permissions.
    @staticmethod
    def writable(path, error=False):
        write_permission = os.access(path, os.W_OK)
        if error and not write_permission:
            if hasattr(error, '__call__'):
                # Execute error callback if provided
                error(e)
            else:
                # Else fatal error
                print "No read permissions for directory '" + path + "'!"
                sys.exit(1)
        return write_permission


    # rm() - Recursively remove files
    #
    # Argument 'error' can either by a boolean that dictates whether
    # to exit fatally on error, or a callback function to execute. If
    # 'must_exist' is True, then error if the file doesn't exist. This
    # function returns boolean on whether a file was deleted or not.
    @staticmethod
    def rm(path, must_exist=False, error=False, verbose=False):
        exists = Util.exists(path, error=must_exist)

        if exists:
            Util.writable(path, error=error)

            try:
                if os.path.islink(path):
                    os.unlink(path)
                    type = "link"
                elif os.path.isdir(path):
                    shutil.rmtree(path)
                    type = "directory"
                else:
                    os.remove(path)
                    type = "file"

                if verbose:
                    print "Deleted {0} '{1}'".format(type, path)
                return True

            # Failed to remove path:
            except:
                if hasattr(error, '__call__'):
                    # Execute error callback if provided
                    error(e)
                elif error:
                    # Fatal error if required
                    print "Failed to delete '" + path + "'."
                    sys.exit(1)
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
        exists = Util.exists(path, error=must_exist)
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
        exists = Util.exists(src, error=must_exist)
        readable = Util.readable(src, error=error)

        if exists and readable:
            try:
                shutil.move(src, dst)

                if verbose:
                    print "Moved '{0}' -> '{1}'".format(src, dst)

                return True
            except:
                # Error in file move:
                if hasattr(error, '__call__'):
                    # Execute error callback if provided
                    error(e)
                elif error:
                    # Fatal error if required
                    print "Failed to move '{0}' to '{1}'.".format(src, dst)
                    sys.exit(1)
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
        exists = Util.exists(src, error=error)

        if exists:
            try:
                os.symlink(src, dst)

                if verbose:
                    print "Link '{0}' -> '{1}'".format(src, dst)

                return True
            except:
                # Error in operation:
                if hasattr(error, '__call__'):
                    # Execute error callback if provided
                    error(e)
                elif error:
                    # Fatal error if required
                    print "Failed to move '{0}' to '{1}'.".format(src, dst)
                    sys.exit(1)
                else:
                    return False

        # Source does not exist:
        else:
            return False


    # mkdir() - Create a directory and all required parents
    #
    # Returns True if directory is created, else False. Argument
    # 'error' can either by a boolean that dictates whether to exit
    # fatally on error, or a callback function to execute.
    @staticmethod
    def mkdir(path, mode=0777, fail_if_already_exists=False,
              error=False, verbose=False):
        exists = Util.exists(path, fail_if_already_exists)

        if exists:
            return False
        else:
            try:
                os.makedirs(path, mode)

                if verbose:
                    print "Created directory '{0}' with mode 0{1:o}".format(path, mode)

                return True
            except:
                # Error in operation:
                if hasattr(error, '__call__'):
                    # Execute error callback if provided
                    error(e)
                elif error:
                    # Fatal error if required
                    print "Failed to create directory '{0}'.".format(path)
                    sys.exit(1)
                else:
                    return False


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
            print "Executing '{0}'.".format(" ".join(args))

        process = subprocess.Popen(args, stdin=stdin, stdout=stdout,
                                   stderr=stderr)

        if wait:
            process.wait()

        if error and process.returncode:
            # Error in operation:
            if hasattr(error, '__call__'):
                # Execute error callback if provided
                error(e)
            elif error:
                # Fatal error if required
                print "Failed to execute '{0}'.".format(" ".join(args))
                sys.exit(1)

        return process


    # rsync() - Execute rsync file transfer
    #
    # The 'archive', 'update', 'dry_run', 'link_dest', 'delete', and
    # 'delete_excluded' arguments correspond to their respective rsync
    # flags. 'exclude' and 'exclude_from' arguments accept either a
    # list of paths and patterns or a single string.
    @staticmethod
    def rsync(src, dst, archive=True, update=False,
              dry_run=False, link_dest=None,
              exclude=None, exclude_from=None,
              delete=False, delete_excluded=False, wait=True,
              stdout=None, stderr=None, args=None,
              error=False, verbose=False, quiet=False):

        rsync_flags = ["rsync"]

        if archive:
            rsync_flags.append("--archive")

        if update:
            rsync_flags.append("--update")

        if dry_run:
            rsync_flags.append("--dry-run")

        if link_dest:
            rsync_flags += ["--link-dest", link_dest]

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
            rsync_flags += ["--verbose",
                            "--human-readable",
                            "--progress"]

        # Add source and destination operands after flags:
        rsync_flags += [src, dst]

        return Util.p_exec(rsync_flags, stdout=stdout, stderr=stderr,
                           wait=wait, error=error, verbose=verbose)


    # Look up a stack by name, or raise StackNotFoundError():
    @staticmethod
    def get_stack_by_name(name, stacks):
        for stack in stacks:
            if stack.stack == name:
                return stack

        raise StackNotFoundError(name)


    # Look up a snapshot by id, or raise SnapshotNotFoundError():
    @staticmethod
    def get_snapshot_by_id(id, snapshots):
        for snapshot in snapshots:
            if snapshot.id == id.id:
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


    # printf() - Format and print a message
    #
    # If both 'colour' and 'prefix' are provided, then colourise only
    # the prefix. If no 'prefix' is provided, colourise the whole
    # message.
    @staticmethod
    def printf(msg, prefix=None, colour=None):
        string = Colours.RESET

        if colour:
            string += colour

        if prefix:
            string += prefix + Colours.RESET + ": "

        string += msg + Colours.RESET

        print string


    # colourise() - Colourise a string
    #
    # Returns the given string wrapped in colour escape codes.
    @staticmethod
    def colourise(string, colour):
        return colour + string + Colours.RESET


    @staticmethod
    def version_and_quit(*data):
        print "emu version", Libemu.version_string
        exit(0)


    @staticmethod
    def help_and_quit(*data):
        Util.p_exec("man " + os.path.basename(sys.argv[0]), error=True)
        exit(0)


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


##############################
# Command line option parser #
##############################
class EmuParser(OptionParser):

    def __init__(self):
        # Instantiate superclass
        OptionParser.__init__(self, add_help_option=False)

        # Set default parser arguments:
        self.add_option("-S", "--source-dir", action="store", type="string",
                        dest="source_dir", default=os.getcwd())
        self.add_option("--version", action="callback",
                        callback=Util.version_and_quit)
        self.add_option("-v", "--verbose", action="store_true",
                        dest="verbose", default=False)
        self.add_option("-h", "--help", action="callback",
                        callback=Util.help_and_quit)


    # options() - Set/Get the parser options
    def options(self, *options):
        if options:
            self._options = options

        try:
            return self._options
        except AttributeError:
            (self._options, self._args) = self.parse_args()
            return self.options()


    # args() - Set/Get the parser arguments
    #
    def args(self, *args):
        if args:
            self._args = args

        try:
            return self._args
        except AttributeError:
            (self._options, self._args) = self.parse_args()
            return self.args()


    # parse_stacks() - Parse the arguments for stack identifiers
    #
    # Parses the command line arguments and searches for stack
    # identifiers, returning a list of Stack objects for each of the
    # named stacks. If 'accept_no_stacks' is True, then if no
    # arguments are provided, all stacks will be returned. If an
    # argument does not correspond with a stack, then a
    # StackNotFoundError is raised.
    def parse_stacks(self, source, accept_no_stacks=True, error=True):

        try:
            return self._stacks
        except AttributeError:
            try:

                # Return all stacks if no args:
                if accept_no_stacks and not len(self.args()):
                    return source.stacks()
                else:
                    # Else parse arguments:
                    self._stacks = []
                    for arg in self.args():
                        self._stacks.append(Util.get_stack_by_name(arg,
                                                                   source.stacks()))
                    return self._stacks

            except StackNotFoundError as e:
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


    # parse_snapshots() - Parse the arguments for snapshot identifiers
    #
    # Parses the command line arguments and searches for snapshot IDs,
    # returning a list of Snapshot objects for each of the identified
    # snapshots. If 'accept_stack_names' is True, then if a stack is
    # only named, then a list of all of its snapshots will be used,
    # instead of having to identify a single one. 'If
    # 'accept_no_stacks' is True, then a list of all stacks will be
    # used if no arguments are provided.
    def parse_snapshots(self, source, accept_stack_names=True,
                        accept_no_stacks=True, error=True):

        try:
            return self._snapshots
        except AttributeError:
            try:

                self._snapshots = []
                args = self.args()

                # If no args are given, generate a list of all stack names:
                if accept_no_stacks and not len(args):
                    for stack in source.stacks():
                        args.append(stack.stack)

                # Iterate over each arg, resolving to snapshot(s):
                for arg in args:
                    regex = r"^(?P<stack>[^:]+)((:?)|(:((?P<id>[a-f0-9]{40})|(?P<head>HEAD))(?P<index>~([0-9]+)?)?))?$"
                    match = re.match(regex, arg)

                    if not match:
                        raise InvalidSnapshotIDError(arg)

                    # Regex components:
                    stack_match = match.group("stack")
                    id_match = match.group("id")
                    head_match = match.group("head")
                    index_match = match.group("index")

                    stack = Util.get_stack_by_name(stack_match, source.stacks())

                    # Resolve tilde index notation:
                    n_index = 0
                    if index_match:
                        n_index = Util.tilde_to_n_index(index_match)

                    if id_match:
                        # If there's an ID, then match it:
                        snapshot = Util.get_snapshot_by_id(SnapshotID(stack_match, id_match),
                                                           stack.get_snapshots())
                        self._snapshots.append(snapshot.nth_child(n_index, error=True))
                    elif head_match:
                        # Calculate the HEAD index and traverse:
                        head = stack.get_head()
                        if head:
                            self._snapshots.append(head.nth_child(n_index, error=True))
                    elif accept_stack_names:
                        # If there's no ID then match all snapshots
                        self._snapshots += stack.get_snapshots()
                    else:
                        InvalidSnapshotIDError(arg)

                return self._snapshots

            except (InvalidSnapshotIDError,
                    StackNotFoundError,
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


###############
# Error types #
###############
class InvalidSnapshotIDError(Exception):
    def __init__(self, id):
        self.id = id

    def __str__(self):
        return "Invalid snapshot identifier '{0}!'".format(Util.colourise(self.id,
                                                                          Colours.ERROR))


class StackNotFoundError(Exception):
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return "Stack '{0}' not found!".format(Util.colourise(self.name,
                                                              Colours.ERROR))


class SnapshotNotFoundError(Exception):
    def __init__(self, id):
        self.id = id

    def __str__(self):
        return "Snapshot '{0}:{1}' not found!".format(self.id.stack_name,
                                                      Util.colourise(self.id.id,
                                                                    Colours.ERROR))


class StackLockError(Exception):
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return "Failed to lock stack '{0}'!".format(Util.colourise(self.name,
                                                                   Colours.ERROR))
