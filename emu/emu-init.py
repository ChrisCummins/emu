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

# Resolve and import Libemu
import sys
import os
sys.path.append(os.path.abspath(sys.path[0] + "/../libexec/emu"))
from libemu import Libemu

from sys import exit


def emu_init(options):
    def err_cb(*data):
        emu_clean(options)
        print "Failed to initialise emu source!"
        exit(1)

    emu = options.source_dir + "/.emu"

    # Create directory structure
    directories = ["/", "/config", "/hooks", "/stacks"]
    for d in directories:
        Libemu.mkdir(emu + d, mode=0700, verbose=options.verbose)

    # Copy template files
    Libemu.rsync(options.template_dir + "/", emu + "/", err=err_cb,
                 archive=True, verbose=options.verbose,
                 update=options.force)

    print "Initialised source at '{0}'".format(emu)
    return 0


def emu_clean(options):
    emu = options.source_dir + "/.emu"
    Libemu.exists(emu, err=True)
    Libemu.rm(emu, verbose=options.verbose)

    print "Removed source at '{0}'".format(emu)
    return 0


def main(argv, argc):
    parser = Libemu.get_option_parser(name="emu init",
                                      desc="create or reinitialize an existing emu source")

    parser.add_option("-t", "--template-dir", action="store", type="string",
                      dest="template_dir", metavar="DIR",
                      default=Libemu.global_template_dir + "/source-templates",
                      help="Copy templates from the directory DIR")

    parser.add_option("-f", "--force", action="store_true", dest="force",
                      default=False, help="Overwrite existing files")
    parser.add_option("-C", "--clean", action="store_true", dest="clean",
                      default=False,
                      help="Clean the working directory, reversing the effect of an init")

    (options, args) = parser.parse_args()

    # Fail if no read/write permissions
    Libemu.get_user_read_permissions(options.source_dir, err=True)
    Libemu.get_user_write_permissions(options.source_dir, err=True)

    # Perform relevant action
    if options.clean:
        return emu_clean(options)
    else:
        return emu_init(options)


if __name__ == "__main__":
    argv = sys.argv[1:]
    ret = main(argv, len(argv))
    exit(ret)
