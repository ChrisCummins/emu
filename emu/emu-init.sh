#!/bin/bash

source "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/../libexec/emu/libemu"
EMU_ECHO_PREFIX=$(basename "$0")

clean_emu_dir ()
{
    get_source_dir_or_fail

    rm $EMU_VERBOSE -rf "$SOURCE_DIR/$EMU_DIR"
    emu_echo "emptied source in $SOURCE_DIR/$EMU_DIR"
}

create_directories ()
{
    mkdir $EMU_VERBOSE -p "$SOURCE_DIR/$EMU_DIR"
    mkdir $EMU_VERBOSE -p "$SOURCE_DIR/$EMU_DIR/config"
    mkdir $EMU_VERBOSE -p "$SOURCE_DIR/$EMU_DIR/hooks"
    mkdir $EMU_VERBOSE -p "$SOURCE_DIR/$EMU_DIR/stacks"
    chmod 0755 "$SOURCE_DIR/$EMU_DIR/stacks"
}

copy_template_files ()
{
    if [ -n "$EMU_VERBOSE" ]; then
        emu_echo "using template dir '$EMU_SOURCE_TEMPLATE_DIR'"
    fi

    # copy over files from shared templates dir
    rsync \
        $EMU_VERBOSE \
        --archive \
        --human-readable \
        $EMU_TEMPLATE_UPDATE \
        "$EMU_SOURCE_TEMPLATE_DIR/" \
        "$SOURCE_DIR/$EMU_DIR/"
}

init_filesystem ()
{
    create_directories
    copy_template_files
}

emu_init ()
{
    local msg=""

    init_filesystem

    if [ -d "$EMU_DIR" ]
    then
        msg="reinitialized existing source in $SOURCE_DIR/$EMU_DIR"
    else
        msg="initialized source in $SOURCE_DIR/$EMU_DIR"
    fi

    emu_echo "$msg"
}


main ()
{
    EMU_TEMPLATE_UPDATE="-u"

    test -n "$EMU_DEBUG" && set -x
    exit_on_help_version $@

    while getopts ":qvCRt:" OPT
    do
        case $OPT in
            q)
                EMU_QUIET=1
                ;;
            C)
                EMU_DIR_CLEAN=1
                ;;
            v)
                EMU_QUIET=0
                EMU_VERBOSE="-v"
                ;;
            R)
                EMU_TEMPLATE_UPDATE=""
                ;;
            t)
                EMU_SOURCE_TEMPLATE_DIR="$OPTARG"
                if [ ! -d "$EMU_SOURCE_TEMPLATE_DIR" ]
                then
                    emu_error "'$OPTARG' not a directory"
                    exit 1
                fi
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
    while [ "${1:0:1}" = "-" ]
    do
        shift
    done

    SOURCE_DIR=$(pwd -P)
    exit_if_no_dir_permissions "$SOURCE_DIR"

    if [ -z "$EMU_SOURCE_TEMPLATE_DIR" ]
    then
        EMU_SOURCE_TEMPLATE_DIR="$EMU_DEFAULT_SOURCE_TEMPLATES"
    fi

    if (( $EMU_DIR_CLEAN ))
    then
        clean_emu_dir
        exit 0
    fi

    emu_init
    exit 0
}
main $@
