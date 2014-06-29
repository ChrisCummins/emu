#!/bin/bash

source "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/../libexec/emu/libemu"
EMU_ECHO_PREFIX=$(basename "$0")

main ()
{
    test -n "$EMU_DEBUG" && set -x
    exit_on_help_version $@

    set -e
    emu peek $@
    set +e

    get_source_dir_or_fail
    local dir="$SOURCE_DIR"

    execute_hooks "pre" "$dir"

    local in=$(echo "$1" | tr ":" "\n")

    if [[ $(echo "$in" | wc -l) -ne 2 ]]; then
        if [[ $(ls "$dir/$EMU_DIR/stacks" | wc -l) -eq 1 ]]; then
            local stack="$(ls $dir/$EMU_DIR/stacks)"
        else
            emu_error "invalid snapshot"
            emu_panic
            exit $EMU_EXIT_INCORRECT_COMMAND
        fi
    fi

    if [ -z "$stack" ]; then
        local stack=$(echo "$in" | head -n1)
    fi

    local stack_dir="$(cat $dir/$EMU_DIR/stacks/$stack 2>/dev/null)"
    if [[ ! -d "$stack_dir" ]]; then
        emu_error "stack '$stack' does not exist"
        emu_panic
        exit $EMU_EXIT_ERROR
    fi

    local snapshot=$(echo "$in" | tail -n1)
    if [ "$snapshot" = "HEAD" ]; then
        local snapshot="$(cat "$stack_dir/$EMU_DIR/HEAD")"
    fi

    local snapshot_dir="$stack_dir/$EMU_DIR/trees/$snapshot"
    if [[ ! -d "$snapshot_dir" ]]; then
        emu_error "snapshot '$snapshot' does not exist"
        emu_panic
        exit $EMU_EXIT_ERROR
    fi

    # FIXME

    execute_hooks "post" "$dir"
}
main $@
