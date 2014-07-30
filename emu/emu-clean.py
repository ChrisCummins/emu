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
from libemu import EmuParser, Util, Colours, Source, StackNotFoundError

def main(argv, argc):
    parser = EmuParser()
    parser.add_option("-d", "--dry-run", action="store_true",
                      dest="dry_run", default=False)
    parser.add_option("-r", "--recursive", action="store_true",
                      dest="recursive", default=False)
    (options, args) = parser.parse_args()

    source = Source(options.source_dir)

    if len(args):
        for arg in args:
            try:
                stack = Util.get_stack_by_name(arg, source.stacks())
                stack.clean(verbose=options.verbose, dry_run=options.dry_run)
            except StackNotFoundError as e:
                print e
                sys.exit(1)
    else:
        source.clean(recursive=options.recursive, verbose=options.verbose,
                     dry_run=options.dry_run)

    return 0


if __name__ == "__main__":
    argv = sys.argv[1:]
    ret = main(argv, len(argv))
    exit(ret)
