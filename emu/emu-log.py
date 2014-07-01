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
import subprocess
import sys
import tempfile
from sys import exit

# Resolve and import Libemu
sys.path.append(os.path.abspath(sys.path[0] + "/../libexec/emu"))
from libemu import Libemu
from libemu import Source
from libemu import SourceCreateError

def main(argv, argc):
    parser = Libemu.get_option_parser(name="emu init",
                                      desc="create or reinitialize an existing emu source")
    parser.add_option("-t", "--template-dir", action="store", type="string",
                      dest="template_dir", metavar="DIR",
                      default=Libemu.global_template_dir + "/source-templates",
                      help="Copy templates from the directory DIR")
    parser.add_option("-f", "--force", action="store_true", dest="force",
                      default=False, help="Overwrite existing files")
    (options, args) = parser.parse_args()

    Libemu.die_if_not_source(options.source_dir)

    snapshots = Libemu.get_snapshots(args, options.source_dir)

    # Setup pagination
    tmp_path = tempfile.mkstemp()[1]
    tmp_file = open(tmp_path, 'a')
    sys.stdout = tmp_file

    for snapshot in snapshots:
        print snapshot.log()

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
