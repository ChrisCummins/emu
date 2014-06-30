#!/bin/bash

source "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/../libexec/emu/libemu"
EMU_ECHO_PREFIX=$(basename "$0")

main ()
{
    test -n "$EMU_DEBUG" && set -x
    exit_on_help_version $@

    get_source_dir_or_fail
    execute_hooks "pre" "$SOURCE_DIR"

    local input=$(echo "$1" | tr ":" "\n")

    if [[ $(echo "$input" | wc -l) -ne 2 ]]
    then
        if [[ $(ls "$SOURCE_DIR/$EMU_DIR/stacks" | wc -l) -eq 1 ]]
        then
            # If there's only 1 stack, use that.
            local stack="$(ls $SOURCE_DIR/$EMU_DIR/stacks)"
        else
            emu_error "invalid snapshot"
            emu_panic
            exit $EMU_EXIT_INCORRECT_COMMAND
        fi
    fi

    if [ -z "$stack" ]
    then
        local stack=$(echo "$input" | head -n1)
    fi

    local stack_dir="$(cat $SOURCE_DIR/$EMU_DIR/stacks/$stack 2>/dev/null)"
    if [[ ! -d "$stack_dir" ]]
    then
        emu_error "stack '$stack' does not exist"
        emu_panic
        exit $EMU_EXIT_INCORRECT_COMMAND
    fi

    local snapshot=$(echo "$input" | tail -n1)
    local node="$stack_dir/$EMU_DIR/trees/$snapshot"
    if [[ ! -d "$node" ]]
    then
        emu_error "snapshot '$snapshot' does not exist"
        emu_panic
        exit $EMU_EXIT_INCORRECT_COMMAND
    fi

    set -e
    verify_node "$node"
    set +e
    emu_echo "pass"

    exit 0
}
main $@
