#!/usr/bin/env bash
#
# Copyright (C) 2012-2020 Chris Cummins.
#
# This file is part of emu.
#
# Emu is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# Emu is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public
# License for more details.
#
# You should have received a copy of the GNU General Public License
# along with emu.  If not, see <http://www.gnu.org/licenses/>.

print_help ()
{
    cat <<EOF
Usage: ./scripts/todo.sh

Generate a list of all TODO, FIXME, and XXX tags in the repository.
EOF
}

for arg in $@; do
    if [ "$arg" == "--help" ] \
        || [ "$arg" == "help" ] \
        || [ "$arg" == "-h" ]; then
        print_help
        exit 0
    fi
done

file_list=$(git ls-files)

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
