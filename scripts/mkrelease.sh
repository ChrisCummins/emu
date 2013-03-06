#!/bin/bash

VERSION=$1
OLD_VERSION=$(cat lib/libemu | grep EMU_VERSION \
    | sed -r 's/.+\sEMU_VERSION="([0-9]\.[0-9]\.[0-9])"\s*$/\1/')

# check for correct args
if [ -z $VERSION ]
then
    cat <<EOF
Usage: mkrelease.sh [--version] [--help] <new-version-number>

Automatic release tool, generates release tarball and replaces all
references to the old version number with the new one. For example, if
the current version is 0.2.2 and you would like to make a release 0.3.0,
run:

  $ ./scripts/mkrelease.sh 0.3.0

This will substitute relevant references to 0.2.2 with 0.3.0, and
generate two files:

  ./releases/emu-0.3.0.tar.gz      # The release tarball.
  ./releases/emu-0.3.0.tar.gz.md5  # Release tarball checksum.
EOF
    exit 1
fi

# check that old version number is valid
if [[ -z "$OLD_VERSION" ]]
then
    echo "Could not get old version number!"
    exit 1
fi

# generate file list
FILELIST=$(find . -type f \
    | grep -v '.git' \
    | grep -v 'releases/emu-*.tar.gz' \
    | grep -v 'releases/emu-*.tar.gz.md5' \
    | grep -v 'mkrelease' \
    | grep -v 'mktar')

# update references to version in filelist
for file in $FILELIST
do
    sed -i "s/$OLD_VERSION/$VERSION/g" $file
done

# generate man list
MANLIST=$(find ./share/man -type f)

# update man page headers
for f in $MANLIST
do
    base=$(basename $f)
    file=${base%.*}
    ext=${base##*.}
    date=$(date +'%B %d, %Y')
    cat $f | sed "1s/.*/.TH $file $ext  \"$date\" \"version $VERSION\" \"Emu Manual\"/" > $f.tmp
    rm -f $f
    mv $f.tmp $f
done
