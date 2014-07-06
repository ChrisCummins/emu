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
import sys
from sys import exit

# Resolve and import Libemu
sys.path.append(os.path.abspath(sys.path[0] + "/../libexec/emu"))
from libemu import EmuParser
from libemu import Libemu
from libemu import Source
from libemu import SourceCreateError

def main(argv, argc):
    parser = EmuParser()
    source = Source(parser.options().source_dir)

    for stack in parser.parse_stacks(source):
        snapshots = stack.snapshots()
        print stack.name
        print "Location:        {0}".format(stack.path)
        print "No of snapshots: {0}".format(len(snapshots))
        print "Max snapshots:   {0}".format(stack.max_snapshots())
        if len(snapshots):
            print "Last snapshot:   {0}".format(snapshots[len(snapshots) - 1].id)
        sys.stdout.write("Size:            ")
        sys.stdout.flush()
        os.system("du -sh '" + stack.path + "' | awk '{{print $1}}'")

        sys.stdout.write("Device:          ")
        sys.stdout.flush()
        os.system("df -h '" + stack.path + "' | tail -n1 | awk '{{print $6}}'")
        print

    return 0


if __name__ == "__main__":
    argv = sys.argv[1:]
    ret = main(argv, len(argv))
    exit(ret)
