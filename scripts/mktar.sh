#!/bin/bash

set -e

print_help ()
{
    cat <<EOF
Usage: ./scripts/mktar.sh [--version] [--help]

Automatic packaging tool, generates a versioned release tarball and
checksum. For example, if the current version is 0.3.0, then the
script will generate two files:

  ./releases/emu-0.3.0.tar.gz      # The release tarball.
  ./releases/emu-0.3.0.tar.gz.md5  # Release tarball checksum.
EOF
}

print_version ()
{
    echo "version $version"
}

version=$(cat lib/libemu | grep EMU_VERSION \
    | sed -r 's/.+\sEMU_VERSION="([0-9]+\.[0-9]+\.[0-9]+)"\s*$/\1/')

test -n "$version" || { echo "Could not get version number!" >&2; exit 2; }

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

# Create a release tarball.
cd ..
tar czf \
    emu-$version.tar.gz emu \
    --exclude='emu/.git/*' \
    --exclude='emu/releases/emu-*.tar.gz' \
    --exclude='emu/releases/emu-*.tar.gz.md5'

# Generate MD5.
md5sum emu-$version.tar.gz > emu-$version.tar.gz.md5
mv emu-$version.tar.gz emu/releases
mv emu-$version.tar.gz.md5 emu/releases

echo "Generated ./releases/emu-$version.tar.gz"
echo "Generated ./releases/emu-$version.tar.gz.md5"
