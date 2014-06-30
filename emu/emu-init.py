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
import shutil

import calendar
import json
import subprocess
import re
import stat
import os
import sys
import time
import datetime
import dateutil.relativedelta
from git import Repo
from sys import argv
from sys import exit
from os.path import expanduser

from optparse import OptionParser

## Libemu

class Libemu:
    prefix = "/usr/local"
    global_template_dir = prefix + "/share/emu/templates"
    version = {
        "major": 0,
        "minor": 0,
        "micro": 8
    }
    version_string = (str(version["major"]) + "." +
                      str(version["minor"]) + "." +
                      str(version["micro"]))


    @staticmethod
    def show_version_and_quit(*data):
        print "emu version", Libemu.version_string
        exit(0)


    @staticmethod
    def get_option_parser(name="", desc=""):
        string = ""

        if len(name):
            string = name + " [options] "
            if len(desc):
                string += "- " + desc

        if (len(string)):
            parser = OptionParser(string)
        else:
            parser = OptionParser()

        parser.add_option("-S", "--source-dir", action="store", type="string",
                          dest="source_dir", default=os.getcwd(), metavar="DIR",
                          help="Specify the emu working directory")
        parser.add_option("-V", "--version", action="callback",
                          callback=Libemu.show_version_and_quit,
                          help="Show version information")
        parser.add_option("-v", "--verbose", action="store_true",
                          dest="verbose", default=False,
                          help="Increase verbosity")
        return parser


    @staticmethod
    def get_user_read_permissions(path, err=False):
        r = os.access(path, os.R_OK)
        if err and not r:
            if hasattr(err, '__call__'):
                err() # Error callback
            else:
                print "No read permissions for directory '" + path + "'!"
                exit(1)
        return r


    @staticmethod
    def get_user_write_permissions(path, err=False):
        w = os.access(path, os.W_OK)
        if err and not w:
            if hasattr(err, '__call__'):
                err() # Error callback
            else:
                print "No write permissions for directory '" + path + "'!"
                exit(1)
        return w


    @staticmethod
    def exists(path, err=False):
        exists = os.path.exists(path)
        if err and not exists:
            if hasattr(err, '__call__'):
                err() # Error callback
            else:
                print "'" + path + "' not found!"
                exit(1)
        return exists


    @staticmethod
    def mkdir(path, mode=0777, verbose=False):
        try:
            os.makedirs(path, mode)
            created = True
        except OSError:
            # OSError is thrown if the file already exists. Note that
            # just because it exists, it does not necessarily have the
            # correct permissions, so let's set the mode just in case.
            os.chmod(path, mode)
            created = False
        if verbose and created:
            print "Created directory '{0}' with mode 0{1:o}".format(path, mode)
        return created


    @staticmethod
    def rm(path, verbose=False):
        Libemu.get_user_write_permissions(path, err=True)
        if os.path.isdir(path):
            shutil.rmtree(path)
            if verbose:
                print "Recursively deleted '{0}'".format(path)
            return True
        elif os.path.exists(path):
            os.remove(path)
            if verbose:
                print "Deleted file '{0}'".format(path)
            return True
        else:
            return False


    @staticmethod
    def rsync(src, dest, verbose=False, err=False,
              archive=True, update=False, delete=False):
        cmd = "rsync"

        if verbose:
            cmd += " --verbose --human-readable"
        if archive:
            cmd += " --archive"
        if update:
            cmd += " --update"
        if delete:
            cmd += " --delete"

        ret = os.system(cmd + " '" + src + "' '" + dest + "'")

        if err and ret != 0:
            if hasattr(err, '__call__'):
                err() # Error callback
            else:
                print "Rsync transfer failed!"
                exit(1)

        return ret


### Init


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
