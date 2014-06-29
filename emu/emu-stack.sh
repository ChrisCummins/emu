#!/bin/bash

source "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/../libexec/emu/libemu"
EMU_ECHO_PREFIX=$(basename "$0")

init_stack ()
{
    STACK_DIR="$1"
    TEMPLATE_DIR="$EMU_DEFAULT_STACK_TEMPLATES"

    exit_if_no_dir_permissions "$1"
    mkdir $EMU_VERBOSE -p "$STACK_DIR/$EMU_DIR"
    mkdir $EMU_VERBOSE -p "$STACK_DIR/$EMU_DIR/trees"
    mkdir $EMU_VERBOSE -p "$STACK_DIR/$EMU_DIR/nodes"
    mkdir $EMU_VERBOSE -p "$STACK_DIR/$EMU_DIR/config"
    touch "$STACK_DIR/$EMU_DIR/HEAD"
    echo $(pwd) > "$STACK_DIR/$EMU_DIR/SOURCE"
    cp -n $EMU_VERBOSE "$TEMPLATE_DIR/config/SNAPSHOT-COUNT" "$STACK_DIR/$EMU_DIR/config"

    if ! (( $EMU_QUIET ))
    then
        emu_echo "initialized stack at $STACK_DIR/$EMU_DIR"
    fi
}

add_stack ()
{
    local stack_name="$1"
    local stack_path="$2"

    if [ -z "$stack_name" ] || [ -z "$stack_path" ]
    then
        emu_error "must specify <name> <path>"
        exit $EMU_EXIT_INCORRECT_COMMAND
    fi

    if [[ -f "$EMU_DIR/stacks/$stack_name" ]]
    then
        emu_error "stack '$stack_name' already exists"
        exit 1
    fi

    exit_if_no_dir_permissions "$EMU_DIR"

    # get absolute path
    mkdir -p "$stack_path"
    stack_path="$(get_absolute_path "$stack_path")"
    pushd . &>/dev/null
    cd "$stack_path"
    if is_stack
    then
        emu_error "'$stack_path' is already an emu stack"
        exit $EMU_EXIT_ERROR
    fi
    popd &>/dev/null

    echo "$stack_path" > "$EMU_DIR/stacks/$stack_name"

    # initialize stack
    init_stack "$stack_path"
}

rm_stack ()
{
    if [[ ! -f "$EMU_DIR/stacks/$1" ]]
    then
        emu_error "stack '$1' does not exist"
        exit 1
    fi

    if (( $EMU_RM_STACK ))
    then
        rm $EMU_VERBOSE -rf "$(cat $EMU_DIR/stacks/$1)"
    fi

    rm $EMU_VERBOSE -f "$EMU_DIR/stacks/$1"
    if ! (( $EMU_QUIET ))
    then
        emu_echo "stack '$1' removed"
    fi
}

show_stack ()
{
    if [[ $@ == "" ]]
    then
        STACKS="$(ls $EMU_DIR/stacks)"
    else
        FAILURE=0
        for ARG in $@
        do
            if [[ -f "$EMU_DIR/stacks/$ARG" ]]
            then
                STACKS="$STACKS\n$ARG"
            else
                emu_error "stack '$ARG' does not exist"
                FAILURE=1
            fi

            if [[ FAILURE -ne 0 ]]
            then
                emu_panic
                exit $EMU_EXIT_ERROR
            fi

            STACKS="$(echo -e STACKS | tail -n+2)"
        done
    fi

    for STACK in $STACKS
    do
        print_stack_details "$STACK"
    done
}

list_stacks ()
{
    if [ -z $EMU_VERBOSE ]
    then
        ls "$EMU_DIR/stacks"
    else
        local table=.emu-stack.TMP

        for STACK in $(ls "$EMU_DIR/stacks")
        do
            echo -e "$STACK \t$(cat $EMU_DIR/stacks/$STACK)" >> $table
        done

        # Print the table.
        cat $table | column -t -s'	'
        rm -f $table
    fi
}

main ()
{
    test -n "$EMU_DEBUG" && set -x
    exit_on_help_version $@

    while getopts ":qvs:Rt:" OPT
    do
        case $OPT in
            q)
                EMU_QUIET=1
                ;;
            v)
                EMU_VERBOSE="-v"
                ;;
            s)
                EMU_SNAPSHOT_COUNT="$OPTARG"
                ;;
            R)
                EMU_RM_STACK=1
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

    # Dispose of args.
    while [ "${1:0:1}" = "-" ]
    do
        shift
    done

    get_source_dir_or_fail

    if [ ! -d "$SOURCE_DIR/$EMU_DIR/stacks" ]
    then
        emu_error "not an emu source"
        emu_panic
        exit $EMU_EXIT_INCORRECT_COMMAND
    fi

    case "$1" in
        "")
            list_stacks
            ;;
        "add")
            shift
            add_stack $1 $2
            ;;
        "rm")
            shift
            rm_stack $@
            ;;
        "show")
            shift
            show_stack $@
            ;;
        *)
            command_not_found "$1"
            ;;
    esac

    exit 0
}
main $@