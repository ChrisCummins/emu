#!/bin/bash

source "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/../libexec/emu/libemu"
EMU_ECHO_PREFIX=$(basename "$0")

clean_dir_lock() {
    local dir="$1"
    local lock="$dir/$EMU_DIR/LOCK"

    if [ -f "$lock" ]; then
        pid=$(cat $lock | grep -i 'pid:' | sed -r 's/^\s*PID:\s*//i')
        date=$(cat $lock | grep -i 'date:' | sed -r 's/^\s*DATE:\s*//i')

        if [ -z "$EMU_DRY_RUN" ]; then
            rm -f "$lock"
            emu_echo "Removed lock '$pid' ($date)"
        else
            emu_echo "Lock '$pid' will be removed ($date)"
        fi
    fi
}

clean_orphan_trees() {
    local dir="$1"

    for t in $(ls "$dir/$EMU_DIR/trees"); do
        if [ ! -f "$dir/$EMU_DIR/nodes/$t" ]; then
            if [ -z "$EMU_DRY_RUN" ]; then
                rm -rf "$dir/$EMU_DIR/trees/$t"
                emu_echo "Removed orphan tree '$t'"
            else
                emu_echo "Orphan tree '$t' will be removed"
            fi
        fi
    done
}

clean_orphan_nodes() {
    local dir="$1"

    for n in $(ls "$dir/$EMU_DIR/nodes"); do
        if [ ! -d "$dir/$EMU_DIR/trees/$n" ]; then
            if [ -z "$EMU_DRY_RUN" ]; then
                rm -f "$dir/$EMU_DIR/nodes/$n"
                emu_echo "Removed orphan node '$n'"
            else
                emu_echo "Orphan node '$n' will be removed"
            fi
        fi
    done
}

clean_in_progress() {
    local dir="$1"
    local new="$dir/$EMU_DIR/trees/new"

    if [ -d "$new" ]; then
        if [ -z "$EMU_DRY_RUN" ]; then
            rm -rf "$new"
            emu_echo "Removed directory '$new'"
        else
            emu_echo "Directory '$new' will be removed"
        fi
    fi
}

clean_broken_symlinks() {
    local dir="$1"

    for l in $(ls "$dir"); do
        if [ -L "$l" ]; then
            if readlink -q "$l" &>/dev/null ; then
                if [ -z "$EMU_DRY_RUN" ]; then
                    rm -f "$l"
                    emu_echo "Removed broken link '$l'"
                else
                    emu_echo "Broken link '$l' will be removed"
                fi
            fi
        fi
    done
}

clean_stack() {
    local dir="$1"

    execute_hooks "pre" "$dir"
    clean_dir_lock "$dir"
    clean_orphan_nodes "$dir"
    clean_orphan_trees "$dir"
    clean_in_progress "$dir"
    clean_broken_symlinks "$dir"

    test -z "$EMU_DRY_RUN" && emu_echo "Working directory is clean"
}

clean_source() {
    local dir="$1"

    execute_hooks "pre" "$dir"
    clean_dir_lock "$dir"

    test -z "$EMU_DRY_RUN" && emu_echo "Working directory is clean"
}

main() {
    test -n "$EMU_DEBUG" && set -x
    exit_on_help_version $@

    # Parse short args.
    while getopts ":n" OPT
    do
        case $OPT in
            n)
                EMU_DRY_RUN=1
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

    # Dispose of args.
    while [ "${1:0:1}" = "-" ]
    do
        shift
    done

    dir="$(pwd)"

    get_source_dir
    get_stack_dir

    if [ -n "$STACK_DIR" ]; then
        clean_stack "$STACK_DIR"
    elif [ -n "$SOURCE_DIR" ]; then
        clean_source "$SOURCE_DIR"
    else
        emu_error "'$dir' is neither a stack or a source"
        exit $EMU_EXIT_ERROR
    fi

    exit 0
}
main $@
