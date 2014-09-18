#!/usr/bin/env python2.7
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
from libemu import Util, Emu, EmuParser, Source, SourceCreateError

def main(argv, argc):
    parser = EmuParser()
    parser.add_option("-S", "--source-dir", action="store", type="string",
                      dest="source_dir", default=os.getcwd())
    parser.add_option("-t", "--template-dir", action="store", type="string",
                      dest="template_dir", default=Emu.source_templates)
    parser.add_option("-f", "--force", action="store_true", dest="force",
                      default=False)
    (options, args) = parser.parse_args()

    # Fail if no read/write permissions
    Util.readable(options.source_dir, error=True)
    Util.writable(options.source_dir, error=True)

    # Perform initialisation
    try:
        Source.create(options.source_dir, options.template_dir,
                      verbose=options.verbose, force=options.force)
        return 0
    except SourceCreateError as e:
        print e
        return 1


if __name__ == "__main__":
    argv = sys.argv[1:]
    ret = main(argv, len(argv))
    exit(ret)
