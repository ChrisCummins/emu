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
import re
import sys
import os

# Resolve and import libemu:
sys.path.append(os.path.abspath(sys.path[0] + "/../libexec/emu"))
from libemu import EmuParser
from libemu import Source


def main(argv, argc):
    parser = EmuParser()
    parser.add_option("-d", "--dry-run", action="store_true",
                      dest="dry_run", default=False)
    parser.add_option("-f", "--force", action="store_true",
                      dest="force", default=False)
    (options, args) = parser.parse_args()
    source = Source(options.source_dir)
    target = parser.parse_snapshots(source,
                                    accept_stack_names=False,
                                    accept_no_args=False,
                                    single_arg=True,
                                    require=True)[0]
    stack = target.stack

    # Delete all other snapshots:
    for snapshot in stack.snapshots():
        if snapshot.id != target.id:
            snapshot.destroy(dry_run=options.dry_run,
                             force=options.force,
                             verbose=options.verbose)

    # Set new HEAD:
    stack.head(head=target, dry_run=options.dry_run)

    return 0


if __name__ == "__main__":
    argv = sys.argv[1:]
    ret = main(argv, len(argv))
    sys.exit(ret)