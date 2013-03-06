#!/bin/bash

set -e

version=$(cat lib/libemu | grep EMU_VERSION \
    | sed -r 's/.+\sEMU_VERSION="([0-9]+\.[0-9]+\.[0-9]+)"\s*$/\1/')

test -n "$version" || { echo "Could not get version number!" >&2; exit 2; }

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
