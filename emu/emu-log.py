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

import os
import re
import subprocess
import sys
import tempfile
from sys import exit

# Resolve and import Libemu
sys.path.append(os.path.abspath(sys.path[0] + "/../libexec/emu"))
from libemu import EmuParser, Util, Colours, Source

def main(argv, argc):
    parser = EmuParser()
    parser.add_option("-n", "--limit", action="store", type="int",
                      dest="limit", default=0)
    parser.add_option("-s", "--short-log", action="store_true", dest="short",
                      default=False)
    (options, args) = parser.parse_args()

    snapshots = parser.parse_snapshots(Source(options.source_dir))

    # We don't need to proceed if there are no snapshots:
    if not len(snapshots):
        print "No snapshots found."
        return 0

    # Setup pagination
    tmp_path = tempfile.mkstemp()[1]
    tmp_file = open(tmp_path, 'a')
    sys.stdout = tmp_file

    # Zero or negative limit values means show all snapshots
    if options.limit <= 0:
        options.limit = len(snapshots)

    # Reverse so that newest is first
    snapshots.reverse()

    # Determine whether we need to print stack names or not:
    print_stack_names = False
    current_stack = snapshots[0].stack
    for snapshot in snapshots[:options.limit]:
        if snapshot.stack != current_stack:
            print_stack_names = True

    # Print logs:
    current_stack = None
    no_of_snapshots = len(snapshots[:options.limit])
    i = 0
    for snapshot in snapshots[:options.limit]:
        i += 1
        if print_stack_names and snapshot.stack != current_stack:
            current_stack = snapshot.stack
            print Util.colourise("{0}:".format(current_stack.name),
                                 Colours.INFO)
        # Log:
        id = Util.colourise(snapshot.id.id, Colours.SNAPSHOT)
        if options.short:
            print "{0}  {1}".format(id, snapshot.node("name"))
        else:
            node = dict(snapshot.node().items("Node"))

            print "snapshot       {0}".format(id)
            for prop in node:
                if not re.match("^(snapshot|path|source|stack)$", prop):
                    print "{:<14} {:<50}".format(" ".join(prop.split("-")).capitalize() + ":",
                                                 node[prop])
            if i < no_of_snapshots:
                print

    # Flush pagination
    tmp_file.flush()
    tmp_file.close()
    p = subprocess.Popen(['less', tmp_path], stdin=subprocess.PIPE)
    p.communicate()
    sys.stdout = sys.__stdout__

    return 0


if __name__ == "__main__":
    argv = sys.argv[1:]
    ret = main(argv, len(argv))
    exit(ret)
