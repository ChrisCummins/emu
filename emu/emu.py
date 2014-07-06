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
from libemu import Util
from libemu import Libemu


def get_script_path(name):
    script_name = "emu-" + name
    script_path = sys.path[0] + "/" + script_name
    script_exists = Util.exists(script_path)
    if not script_exists:
        print "'{0}' is not an emu command. See 'emu help'".format(name)
        sys.exit(1)
    return script_path


def main(argv, argc):
    # Go to man page if help arg or no args
    if (not argc or
        argv[0] == "-h" or
        argv[0] == "--help"):
        return os.system("man emu")

    # emu help [command] handling
    if (argv[0] == "help"):
        if argc > 1:
            get_script_path(argv[1])
            return os.system("man emu-" + argv[1])
        return os.system("man emu")

    if argv[0] == "--version":
        Util.version_and_quit()

    # Assemble script path and arguments
    script_path = get_script_path(argv[0])
    command = script_path + ' ' + ' '.join(argv[1:])
    return os.system(command)

    # Assemble script path and arguments
    command = script_path + ' ' + ' '.join(argv[1:])

    ret = os.system(command)
    return ret


if __name__ == "__main__":
    argv = sys.argv[1:]
    ret = main(argv, len(argv))
    sys.exit(int(ret % 255))
