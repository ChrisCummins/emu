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

# Resolve and import Libemu
sys.path.append(os.path.abspath(sys.path[0] + "/../libexec/emu"))
from libemu import EmuParser, Source, Colours, Util


def main(argv, argc):
    parser = EmuParser()
    parser.add_option("--dont-cache", action="store_true", dest="dont_cache",
                      default=False)
    parser.add_option("--use-cached", action="store_true", dest="use_cached",
                      default=False)
    (options, args) = parser.parse_args()

    snapshots = parser.parse_snapshots(Source(options.source_dir))
    status = 0

    if not len(snapshots):
        print "No snapshots to verify!"
        status = 1

    for snapshot in snapshots:
        if snapshot.verify(cache_results=not options.dont_cache,
                           use_cached=options.use_cached):
            print snapshot, Util.colourise("ok", Colours.OK)
        else:
            status = 2
            print snapshot, Util.colourise("bad", Colours.ERROR)

    return status


if __name__ == "__main__":
    argv = sys.argv[1:]
    ret = main(argv, len(argv))
    sys.exit(ret)
