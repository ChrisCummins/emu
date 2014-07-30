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
import subprocess

# Resolve and import Libemu
sys.path.append(os.path.abspath(sys.path[0] + "/../libexec/emu"))
from libemu import Util, EmuParser, Source, Stack, StackNotFoundError, Colours

def main(argv, argc):
    parser = EmuParser()
    parser.add_option("-t", "--template-dir", action="store", type="string",
                      dest="template_dir", default=Util.stack_templates)
    parser.add_option("-f", "--force", action="store_true", dest="force",
                      default=False)
    parser.add_option("-i", "--ignore-errors", action="store_true",
                      dest="ignore_errors", default=False)
    parser.add_option("--no-archive", action="store_true",
                      dest="no_archive", default=False)
    (options, args) = parser.parse_args()

    # Fail if no read/write permissions
    Util.readable(options.source_dir, error=True)
    Util.writable(options.source_dir, error=True)

    source = Source(options.source_dir)

    if len(args) < 1:
        # List stacks:
        for stack in source.stacks():
            print Util.colourise(stack.name, Colours.GREEN)
            if options.verbose:
                snapshots = stack.snapshots()
                if stack.head():
                    head_id = stack.head().id.id
                else:
                    head_id = ""

                command = "df -h '{0}'".format(stack.path)
                device = (subprocess.check_output(command, shell=True)
                          .split("\n")[1].split()[0])

                print "Location:        {0}".format(stack.path)
                print "No of snapshots: {0}".format(len(snapshots))
                print "Max snapshots:   {0}".format(stack.max_snapshots())
                print "Head:            {0}".format(head_id)
                print "Device:          {0}".format(device)

    else:
        command = args.pop(0)

        # Add stacks:
        if command == "add":
            if len(args) == 2:
                name = args[0]
                path = args[1]
            else:
                print "Usage: add <name> <path>"
                sys.exit(1)

            Stack.create(source, name, path, options.template_dir,
                         ignore_errors=options.ignore_errors,
                         archive=not options.no_archive,
                         verbose=options.verbose, force=options.force)

        # Remove stacks:
        elif command == "rm":
            if not len(args):
                print "Usage: rm <name ...>"
                sys.exit(1)

            for arg in args:
                try:
                    stack = Util.get_stack_by_name(arg, source.stacks())
                    stack.destroy(force=options.force, verbose=options.verbose)
                except StackNotFoundError as e:
                    print e
                    sys.exit(1)
                sys.exit(1)

        else:
            print "Invalid command. See: emu stack --help"
            sys.exit(1)

    return 0

if __name__ == "__main__":
    argv = sys.argv[1:]
    ret = main(argv, len(argv))
    sys.exit(ret)
