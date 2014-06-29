#!/bin/bash

source "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/../libexec/emu/libemu"
EMU_ECHO_PREFIX=$(basename "$0")

help_command ()
{
    local command="$1"

    if [ -n "$command" ]
    then
        local exec=emu-$command
        command -v $exec >/dev/null 2>&1 || { command_not_found "$command"; }
        $exec --help
        exit 0
    else
        print_help
        exit 0
    fi
}

test -n "$EMU_DEBUG" && set -x

# We cant use exit_on_help_version() since we only want to test $1.
case $1 in
    "--help")
        print_help
        exit 0
        ;;
    "--version")
        print_version
        exit 0
        ;;
esac

# get arguments
while getopts ":hv" OPT
do
    case $OPT in
        \?)
            emu_error "invalid option: -$OPTARG"
            exit $EXIT_INVALID_ARGS
            ;;
        :)
            emu_error "option -$OPTARG requires an argument"
            exit $EXIT_INVALID_ARGS
            ;;
    esac
done

# get command
command="$1"
shift

if [ -z "$command" ]; then
    man emu
    exit 0
fi

# parse commands
case $command in
    "help")
        help_command $@
        exit 0
        ;;
    "version")
        version
        exit 0
        ;;
    *)
        # execute command
        exec=emu-$command
        command -v $exec >/dev/null 2>&1 || { command_not_found "$command"; }
        $exec $@
        exit $?
        ;;
esac