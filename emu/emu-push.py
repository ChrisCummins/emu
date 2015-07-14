#!/usr/bin/env python2.7
#
# Copyright 2015 Chris Cummins.
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

import emu as libemu
from libemu import EmuParser, Source


def main(argv, argc):
    parser = EmuParser()
    parser.add_option("-d", "--dry-run", action="store_true",
                      dest="dry_run", default=False)
    parser.add_option("-f", "--force", action="store_true",
                      dest="force", default=False)
    parser.add_option("-i", "--ignore-errors", action="store_true",
                      dest="ignore_errors", default=False)
    parser.add_option("--no-archive", action="store_true",
                      dest="no_archive", default=False)
    parser.add_option("--no-owner", action="store_true",
                      dest="no_owner", default=False)
    (options, args) = parser.parse_args()

    source = Source(options.source_dir)
    sinks = parser.parse_sinks(source)

    # Fail if source has no sinks:
    if not len(sinks):
        print "Source has no sinks!"
        sys.exit(1)

    status = 0
    for sink in sinks:
        status ^= sink.push(force=options.force,
                            ignore_errors=options.ignore_errors,
                            archive=not options.no_archive,
                            owner=not options.no_owner,
                            dry_run=options.dry_run,
                            verbose=options.verbose)

    return status


if __name__ == "__main__":
    argv = sys.argv[1:]
    ret = main(argv, len(argv))
    sys.exit(ret)
