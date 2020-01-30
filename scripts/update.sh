#!/usr/bin/env bash
#
# Copyright (C) 2012-2020 Chris Cummins.
#
# This file is part of emu.
#
# Emu is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# Emu is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public
# License for more details.
#
# You should have received a copy of the GNU General Public License
# along with emu.  If not, see <http://www.gnu.org/licenses/>.

# Print program usage
usage() {
    echo "Usage: $0 <major|minor|micro|<version-string>>"
    echo ""
    echo "Create automated release bumps for major, minor, or micro versions, "
    echo "or specify a new version string. Current version: $(get_current_version)."
}

# Lookup the root directory for the project. If unable to locate root,
# exit script.
#
#     @return The absolute path to the project root directory
get_project_root() {
    while [[ "$(pwd)" != "/" ]]; do
        if test -f configure.ac; then
            pwd
            return
        fi
        cd ..
    done

    echo "fatal: Unable to locate project base directory." >&2
    exit 3
}

main() {
    # Set debugging output if DEBUG=1
    test -n "$DEBUG" && {
        set -x
    }

    # Check for help argument and print usage
    for arg in $@; do
        if [ "$arg" = "--help" ] || [ "$arg" = "-h" ]; then
            usage
            exit 0
        fi
    done

    set -e

    echo -n "Uninstalling existing version... "
    sudo make uninstall &>/dev/null
    echo "done"

    cd "$(get_project_root)"
    echo -n "Pulling latest upstream changes... "
    git checkout master &>/dev/null
    git pull &>/dev/null
    echo "done"

    echo -n "Getting latest stable version... "
    local latest_stable_release=$(git describe --abbrev=0 --tags)
    echo $latest_stable_release

    echo -n "Cleaning source repository... "
    git clean -xfd &>/dev/null
    echo "done"

    echo -n "Configuring build... "
    ./autogen.sh &>/dev/null
    ./configure &>/dev/null
    echo "done"

    echo -n "Building release $latest_stable_release... "
    make &>/dev/null
    echo "done"

    echo -n "Installing build $latest_stable_release... "
    sudo make install &>/dev/null
    echo "done"

    echo "Running test suite..."
    make test

    echo "Done."
}
main $@
