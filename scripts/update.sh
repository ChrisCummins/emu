#!/usr/bin/env bash

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

    cd "$(get_project_root)"
    echo -n "Pulling latest upstream changes... "
    git pull >/dev/null
    echo "done"

    echo -n "Getting latest stable version... "
    local latest_stable_release=$(git describe --abbrev=0 --tags)
    echo $latest_stable_release

    echo -n "Uninstalling existing version... "
    sudo make uninstall >/dev/null
    echo "done"

    echo -n "Cleaning source repository... "
    git clean -xfd >/dev/null
    echo "done"

    echo "Building latest version..."
    ./autogen.sh
    ./configure
    make

    echo -n "Installing latest version... "
    sudo make install >/dev/null
    echo "done"

    echo "Running test suite..."
    make test

    echo "Done."
}
main $@
