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
        if test -f README; then
            pwd
            return
        fi
        cd ..
    done

    echo "fatal: Unable to locate project base directory." >&2
    exit 3
}

# Given a version string in the form <major>.<minor>.<micro>, return
# the major component.
#
#     @return Major component as an integer, e.g. '5'
get_major() {
    echo "$1" | sed -r 's/^([0-9]+)\.[0-9]+\.[0-9]+$/\1/'
}

# Given a version string in the form <major>.<minor>.<micro>, return
# the minor component.
#
#     @return Minor component as an integer, e.g. '5'
get_minor() {
    echo "$1" | sed -r 's/^[0-9]+\.([0-9]+)\.[0-9]+$/\1/'
}

# Given a version string in the form <major>.<minor>.<micro>, return
# the micro component.
#
#     @return Micro component as an integer, e.g. '5'
get_micro() {
    echo "$1" | sed -r 's/^[0-9]+\.[0-9]+\.([0-9]+)$/\1/'
}

# Find and return the current version string in the form
# <major>.<minor>.<micro>
#
#     @return Current version string, e.g. '0.1.4'
get_current_version() {
    cd "$(get_project_root)"
    grep 'README for emu version ' README \
        | sed 's/README for emu version //'
}

# Replace the project version with a new one.
#
#     @param $1 The new version string
set_new_version() {
    local new=$1

    local major="$(get_major "$new")"
    local minor="$(get_minor "$new")"
    local micro="$(get_micro "$new")"

    cd "$(get_project_root)"

    echo "Setting new version... README"
    test -f README || { echo "fatal: 'README' not found!"; exit 3; }
    sed -r -i 's/(\s*README for emu version )([0-9\.]+)/\1'"$major.$minor.$micro"'/' README
    sed -r -i 's/(\s*This directory contains version )([0-9\.]+)/\1'"$major.$minor.$micro"'/' README

    echo "Setting new version... setup.py"
    test -f setup.py || { echo "fatal: 'setup.py' not found!"; exit 3; }
    sed -r -i 's/(version=")([0-9\.]+)/\1'"$major.$minor.$micro"'/' setup.py

    echo "Setting new version... emu/__init__.py"
    test -f emu/__init__.py || { echo "fatal: 'emu/__init__.py' not found!"; exit 3; }
    sed -r -i 's/(\s*version\s*=\s*Version\(\s*)([0-9]+)(,\s*)([0-9]+)(,\s*)([0-9]+)(,\s*)dirty(\s*=\s*)True/\1'"$major"'\3'"$minor"'\5'"$micro"'\7dirty\8False/' emu/__init__.py

    echo "Updating manpage headers..."
    for f in $(find man -type f); do
        echo "    $f"
        sed -ri 's/^(.TH emu 1 ).*/\1'"$(date +'%B %d, %Y')"' "version '$major.$minor.$micro'" "Emu Manual"/' $f
    done
}

# Make the git version bump commit.
#
#     @param $1 The new version string
make_version_bump_commit() {
    local new_version=$1

    cd "$(get_project_root)"

    echo "Creating version bump commit... '$new_version'"
    git add setup.py
    git add README
    git add emu/__init__.py
    git add man
    git commit --allow-empty -m "Bump release version for '$new_version'" >/dev/null
    git tag $new_version -a -m "Release $new_version"
}

# Make a commit to set the library version dirty flag
#
make_development_version_commit() {
    cd "$(get_project_root)"

    echo "Creating dirty version commit... '$new_version*'"
    sed -r -i 's/(\s*version\s*=\s*Version\(\s*[0-9]+,\s*[0-9]+,\s*[0-9]+,\s*dirty\s*=\s*)False/\1True/' emu/__init__.py
    git add emu/__init__.py
    git commit -m "Set version dirty flag" >/dev/null
}

# Push the version commit and release tag to git remotes.
#
#      @param $@ List of remotes to push to
push_to_remotes() {
    for remote in $@; do
        echo "Pushing branch $remote/master"
        git push $remote master >/dev/null
        echo "Pushing tag $remote/$new_version"
        git push $remote $new_version >/dev/null
    done
}

# Perform the new release.
#
#     @param $1 New version string
do_mkrelease() {
    local new_version=$1

    echo -n "Getting current version... "
    local current_version=$(get_current_version)
    echo "'$current_version'"

    echo "Setting new version... '$new_version'"

    set_new_version "$new_version"
    make_version_bump_commit "$new_version"
    make_development_version_commit "$new_version"
    push_to_remotes "mary origin"
}

# Given a version string in the form <major>.<minor>.<micro>, verify
# that it is correct.
#
#     @return 0 if version is valid, else 1
verify_version() {
    local version="$1"

    local major="$(get_major "$version")"
    local minor="$(get_minor "$version")"
    local micro="$(get_micro "$version")"

    test -n "$major" || return 1;
    test -n "$minor" || return 1;
    test -n "$micro" || return 1;

    return 0;
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

    # Check for new version argument
    if test -z "$1"; then
        usage
        exit 1
    fi

    if [ "$1" = "major" ]; then
        local version="$(get_current_version)"
        local major="$(get_major "$version")"
        major=$((major+1))
        local minor=0
        local micro=0
        version="$major.$minor.$micro"
    fi

    if [ "$1" = "minor" ]; then
        local version="$(get_current_version)"
        local major="$(get_major "$version")"
        local minor="$(get_minor "$version")"
        minor=$((minor+1))
        local micro=0
        version="$major.$minor.$micro"
    fi

    if [ "$1" = "micro" ]; then
        local version="$(get_current_version)"
        local major="$(get_major "$version")"
        local minor="$(get_minor "$version")"
        local micro="$(get_micro "$version")"
        micro=$((micro+1))
        version="$major.$minor.$micro"
    fi

    if [ -z "$version" ]; then
        local version="$1"
    fi

    # Sanity-check on supplied version string
    if ! verify_version "$version"; then
        echo "Invalid version string!" >&2
        exit 1
    fi

    do_mkrelease "$version"
}
main $@
