#!/bin/bash

set -e

print_help ()
{
    cat <<EOF
Usage: ./scripts/mkrelease.sh [--version] [--help] <target-version>

Automatic release tool, generates release tarball and replaces all
references to the old version number with the new one <target-version>.
For example, if the current version is 0.2.2 and you would like to make
a release 0.3.0, run:

  $ ./scripts/mkrelease.sh 0.3.0

This will substitute relevant references to 0.2.2 with 0.3.0, and
generate two files:

  ./releases/emu-0.3.0.tar.gz      # The release tarball.
  ./releases/emu-0.3.0.tar.gz.md5  # Release tarball checksum.
EOF
}

print_version ()
{
    echo "version $current_version"
}

current_version=$(cat lib/libemu | grep EMU_VERSION \
    | sed -r 's/.+\sEMU_VERSION="([0-9]+\.[0-9]+\.[0-9]+)"\s*$/\1/')

# Check sanity of current version number.
test -n "$current_version" || { echo "Could not get old version number!" >&2; exit 1; }

# Make sure we have an arg.
test -n "$1" || { print_help; exit 1; }

for arg in $@; do
    case "$arg" in
        "--help")
            print_help
            exit 0
            ;;
        "--version")
            print_version
            exit 0
            ;;
    esac
done

# Check sanity of new version number.
set +e
new_version=$(echo "$1" | grep -E '^[0-9]+\.[0-9]+\.[0-9]+$')
set -e

if [ -z "$new_version" ]; then
    echo "Invalid version number '$1'!" >&2
    exit 2
fi

if [ -f ./releases/emu-$new_version.tar.gz ]; then
    echo "Release tarball './releases/emu-$new_version.tar.gz' already exists!"
    exit 3
fi

# Generate file list.
filelist=$(find . -type f \
    | grep -vE '\.git' \
    | grep -vE '\./releases/emu-[0-9]+\.[0-9]+\.[0-9]+\.tar\.gz' \
    | grep -v 'mkrelease' \
    | grep -v 'mktar')

# update references to version in filelist
for file in $filelist
do
    sed -i "s/$current_version/$new_version/g" $file
done

# Generate man list.
manpage_list=$(find ./share/man -type f)

# Update man page headers.
for f in $manpage_list
do
    base=$(basename $f)
    file=${base%.*}
    ext=${base##*.}
    date=$(date +'%B %d, %Y')

    cat $f | sed "1s/.*/.TH $file $ext  \"$date\" \"version $new_version\" \"Emu Manual\"/" > $f.tmp
    rm -f $f
    mv $f.tmp $f
done

# Finally, lets make the release tarball.
./scripts/mktar.sh
