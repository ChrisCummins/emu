#!/bin/bash

FILELIST=$(find . -type f \
    | grep -v .git \
    | grep -v todo)

for f in $FILELIST
do
    grep -iHn 'TODO\|FIXME' $f
done

exit 0
