#!/bin/bash

source "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/../libexec/emu/libemu"
EMU_ECHO_PREFIX=$(basename "$0")

print_status_table() {
    local dir="$1"
    local stacks="$(ls "$dir/$EMU_DIR/stacks")"
    local table=.status-TMP

    echo -e " REMOTE\t LAST SNAPSHOT\t CAPACITY\t SIZE\t DEV\t DISK USAGE" >> $table
    for stack in $stacks; do
        local stack_dir="$(cat $dir/$EMU_DIR/stacks/$stack)"
        local newest="$(ls $stack_dir | sort | head -n1)"
        local count="$(ls $stack_dir | wc -l)"
        local max="$(cat "$stack_dir/$EMU_DIR/config/SNAPSHOT-COUNT")"
        local perc="$(echo "($count / $max) * 100" | bc -l | xargs printf "%1.0f")%"
        local du="$(df -h "$stack_dir" | tail -n1)"
        local dev=$(echo "$du" | awk '{ print $6 }')
        local size=$(du -s -h "$stack_dir" | awk '{ print $1 }')
        local use=$(echo "$du" | awk '{ print $3 }')
        local dsize=$(echo "$du" | awk '{ print $2 }')
        local cap=$(echo "$du" | awk '{ print $5 }')

        echo -e " $stack\t $newest\t ($count/$max) $perc\t $size\t $dev\t ($use/$dsize) $cap" >> $table
    done

    # Print the table.
    cat $table | column -t -s'	'
    rm -f $table
}

main() {
    test -n "$EMU_DEBUG" && set -x
    exit_on_help_version $@

    # Parse short args.
    while getopts ":n" OPT
    do
        case $OPT in
            \?)
                emu_error "invalid option: -$OPTARG"
                exit 1
                ;;
            :)
                emu_error "option -$OPTARG requires an argument"
                exit 1
                ;;
        esac
    done

    # Dispose of args.
    while [ "${1:0:1}" = "-" ]
    do
        shift
    done

    get_source_dir_or_fail
    local dir="$SOURCE_DIR"

    execute_hooks "pre" "$dir"

    print_status_table "$dir"

    exit 0
}
main $@