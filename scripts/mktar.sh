#!/bin/bash

VERSION=$(cat lib/libemu | grep EMU_VERSION | sed -r 's/.+EMU_VERSION="(\w\.\w\.\w)".*/\1/')

# create a release tarball
cd ..
tar vczf \
    emu-$VERSION.tar.gz emu \
    --exclude='emu/.git/*' \
    --exclude='emu/releases/emu-*.tar.gz' \
    --exclude='emu/releases/emu-*.tar.gz.md5'

# generate md5
md5sum emu-$VERSION.tar.gz > emu-$VERSION.tar.gz.md5
mv -v emu-$VERSION.tar.gz emu/releases
mv -v emu-$VERSION.tar.gz.md5 emu/releases
