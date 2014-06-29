#!/bin/bash

print_help ()
{
    cat <<EOF
Usage: ./scripts/todo.sh [directory ...]

Generate a list of all TODO, FIXME, and XXX tags in the current
directory and its subdirectories, or in a list of directories if
specified.
EOF
}

for arg in $@; do
    if [ "$arg" == "--help" ]; then
        print_help
        exit 0
    fi
done

directories=$@

test -z "$directories" && directories=.

file_list=$(find $directories -type f \
    | grep -v .git \
    | grep -v Makefile \
    | grep -v todo)

tmp=".todo"
while [ -f $tmp ]; do
    tmp="$tmp$tmp"
done

for f in $file_list; do
    grep -iHn 'TODO\|FIXME\|XXX' $f >> $tmp
done

if [ -f TODO ]; then
    cat TODO | sed 's/^\s*[-*]\s*//' | sed '/^$/d' >> $tmp
fi

cat $tmp | nl

rm -f $tmp

exit 0
