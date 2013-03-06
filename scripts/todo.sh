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

for f in $file_list; do
    grep -iHn 'TODO\|FIXME\|XXX' $f
done

exit 0
