#!/bin/bash

source "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/../libexec/emu/libemu"
EMU_ECHO_PREFIX=$(basename "$0")

# print the nodes for a stack
#  @param $1 name of stack
print_all_node_details ()
{
    local stack="$1"
    local counter=0

    for node in $(ls "$STACK_DIR/$EMU_DIR/nodes" | sort -r); do
        counter=$((counter+1))
        if [[ $counter -le $EMU_LOG_MAX ]]; then
            print_node_details "$node"
        fi
    done
}

show_stack_log() {
    local in=$(echo "$1" | tr ":" "\n")
    local log_file="$2"
    local stack=""
    local snapshot=""

    if [[ $(echo "$in" | wc -l) -eq 2 ]]; then
        # <stack>:<snapshot> format
        stack=$(echo "$in" | head -n1)
    else
        # not a ':' delimited input
        stack="$arg"
    fi

    if [[ ! -f "$dir/$EMU_DIR/stacks/$stack" ]]; then
        emu_error "stack '$stack' does not exist"
        rm -f $log_file
        emu_panic
        exit $EMU_EXIT_ERROR
    fi

    STACK_DIR="$(cat $dir/$EMU_DIR/stacks/$stack 2>/dev/null)"

    if [ -z "$STACK_DIR" ] || [[ ! -d "$STACK_DIR" ]]; then
        # stack files do not exist
        emu_error "stack '$stack' is corrrupt"
        rm -f $log_file
        emu_panic
        exit $EMU_EXIT_ERROR
    fi

    if [[ $(echo "$in" | wc -l) -eq 2 ]]; then
        # <stack>:<snapshot> format
        snapshot=$(echo "$in" | tail -n1)

        if [ "$snapshot" = "HEAD" ]; then
            snapshot="$(cat "$STACK_DIR/$EMU_DIR/HEAD")"
        fi

        if [[ ! -d "$STACK_DIR/$EMU_DIR/trees/$snapshot" ]]; then
            emu_error "snapshot '$snapshot' does not exist"
            rm -f $log_file
            emu_panic
            exit $EMU_EXIT_ERROR
        fi
    fi

    if [ -z "$snapshot" ]; then
        if [[ $(cat $log_file | wc -l) -gt 0 ]]; then
            echo "" >> $log_file
        fi
        print_stack_details "$stack" >> $log_file
        print_all_node_details "$stack" >> $log_file
    else
        print_node_details "$snapshot" > $log_file
    fi
}

main ()
{
    EMU_LOG_MAX=10000

    test -n "$EMU_DEBUG" && set -x
    exit_on_help_version $@

    while getopts ":n:s" OPT; do
        case $OPT in
            n)
                EMU_LOG_MAX=$OPTARG
                ;;
            s)
                EMU_LOG_SUMMARY=1
                ;;
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

    # dispose of args
    while [ "${1:0:1}" = "-" ]; do
        shift
    done

    get_source_dir_or_fail
    local dir="$SOURCE_DIR"
    execute_hooks "pre" "$dir"

    local arg_list="$@"

    if [ -z "$1" ]; then
        # if no argument is given, generate a stack list of all stacks
        local arg_list="$(ls "$dir/$EMU_DIR/stacks")"
    fi

    if ! (( $(ls "$dir/$EMU_DIR/stacks" | wc -l) )); then
        # there are no stacks
        emu_error "no stacks. See 'emu help stack'"
        emu_panic
        exit $EMU_EXIT_ERROR
    fi

    local log_file=.emu_log
    rm -f $log_file
    touch $log_file

    for arg in $arg_list; do
        show_stack_log $arg $log_file
    done

    less $log_file
    rm -f $log_file

    execute_hooks "post" "$dir"
    exit 0
}
main $@
