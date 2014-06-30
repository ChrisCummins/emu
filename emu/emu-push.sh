#!/bin/bash

source "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/../libexec/emu/libemu"
EMU_ECHO_PREFIX=$(basename "$0")

# Retrieve all stack files
#  @return STACK_FILES List of paths to stack files
get_all_stacks ()
{
    STACK_FILES="$(find $SOURCE_DIR/$EMU_DIR/stacks/ | tail -n+2)"

    if [[ "$STACK_FILES" == "" ]]
    then
        emu_error "no stacks! Add one with 'emu stack add <name> <path>'"
        emu_panic
        exit $EMU_EXIT_INCORRECT_COMMAND
    fi

    # check for all sync files
    for stack_file in $STACK_FILES
    do
        local stack="$(cat $stack_file)"
        if [[ ! -d "$stack/$EMU_DIR" ]]
        then
            emu_error "stack does not exist:\n  $stack\n"
            emu_panic
            exit $EMU_EXIT_ERROR
        fi
    done
}

# convert a list of stacks to stack files
#  @param  $@         List of stacks
#  @return STACK_FILES List of stack files paths
get_stacks ()
{
    STACK_FILES[$#]=$@
    for arg in $@
    do
        STACK_FILE="$(find $SOURCE_DIR/$EMU_DIR/stacks/ -name $arg)"
        if [[ "$STACK_FILE" == "" ]]
        then
            emu_error "stack '$arg' not found!"
            emu_panic
            exit $EMU_EXIT_INCORRECT_COMMAND
        fi
        STACK_FILES="$STACK_FILES\n$STACK_FILE"
    done
    STACK_FILES="$(echo -e $STACK_FILES | tail -n+2)"
}

# generate a snapshot hash
#  @param  $1   Path to stack directory
#  @return HASH A 40 digit snapshot UID
generate_hash ()
{
    HASH=$(printf '%x\n' $(date +'%s') | tail -c9)
    HASH=$HASH$(hash_directory "$1/$EMU_DIR/trees/new")

    # check if hash exists, and if so, wait
    if [[ -f "$1/$EMU_DIR/nodes/$HASH" ]]
    then
        sleep 1
        generate_hash "$1"
    fi
}

# generate a snapshot name
#  @param  $1       Path to stack directory
#  @var    HASH     The 40 digit snapshot UID
#  @return SNAPSHOT A snapshot name
generate_snapshot_name ()
{
    SNAPSHOT=$(date -d @$(printf '%d' 0x${HASH:0:8}) +'%Y-%m-%d %H.%M.%S')
}

# generate a snapshot node file
#  @param $1    Path to stack directory
#  @var   $HEAD The UID of the parent snapshot
#  @var   $HASH The 40 digit snapshot UID
generate_node ()
{
    local node="$1/$EMU_DIR/nodes/$HASH"
    touch "$node"
    cat <<EOF >> "$node"
Snapshot $SNAPSHOT
Parent   $HEAD
Date     $(date)
Source   $(cat $1/$EMU_DIR/SOURCE)
Size     $(du -sh "$1/$EMU_DIR/trees/$HASH" | sed -r 's/([0-9a-zA-Z]+)\s.*/\1/')
EOF
    chmod 0640 "$node"
}

# fetch the head of the stack tree, if there is one
#  @param  $1         Path to stack directory
#  @return HEAD       The UID of the HEAD snapshot
#  @return RSYNC_LINK The rsync link command, pointed to head
get_rsync_link ()
{
    HEAD="$(cat $1/$EMU_DIR/HEAD)"
    if [[ "$HEAD" != "" ]] && [[ -d "$1/$EMU_DIR/trees/$HEAD" ]]
    then
        RSYNC_LINK="--link-dest=$1/$EMU_DIR/trees/$HEAD"
    else
        RSYNC_LINK=""
    fi
}

# push the latest snapshot to HEAD
#  @param $1   Path to stack directory
#  @var   HASH The UID of the latest snapshot
push_head ()
{
    rm -f "$1/$EMU_DIR/HEAD"
    echo "$HASH" > "$1/$EMU_DIR/HEAD"
}

# fetch the parent of the current snapshot
#  @param  $1 Path to stack directory
#  @param  $2 Starting hash
#  @return    Next hash, or empty string if NULL
get_snapshot_parent ()
{
    echo "$(cat $1/$EMU_DIR/nodes/$2 2>/dev/null | grep Parent | sed -r 's/Parent +//')"
}

# Fetch the child of the current snapshot
#  @param  $1            Path to stack directory
#  @param  $2            Hash of starting point
#  @param  $3            Target hash
#  @return SNAPSHOT_HASH The hash of the snapshot's child
get_snapshot_child ()
{
    local next_snapshot_hash="$2"
    while [[ "$next_snapshot_hash" != "$3" ]]
    do
        SNAPSHOT_HASH="$next_snapshot_hash"
        next_snapshot_hash="$(get_snapshot_parent $1 $SNAPSHOT_HASH)"
    done
}

# deletes a snapshot
#  @param $1 path to stack directory
#  @param $2 snapshot to delete
#  @param $3 name of stack
remove_snapshot ()
{
    local stack_name="$3"

    get_snapshot_child "$1" "$(cat $1/$EMU_DIR/HEAD)" "$2"
    cat "$1/$EMU_DIR/nodes/$SNAPSHOT_HASH" | sed -r 's/^(Parent\s+).*/\1/i' > "$1/.emu/nodes/$SNAPSHOT_HASH.tmp"
    mv -f "$1/.emu/nodes/$SNAPSHOT_HASH.tmp" "$1/.emu/nodes/$SNAPSHOT_HASH"
    emu_echo "$stack_name: removing '$2'"
    rm -f $EMU_VERBOSE "$1/$EMU_DIR/nodes/$2"
    rm -f $EMU_VERBOSE "$1/$EMU_DIR/nodes/$2.MSG"
    rm -rf $EMU_VERBOSE "$1/$EMU_DIR/trees/$2"
    rm -rf $EMU_VERBOSE "$1/$(date -d @$(printf '%d' 0x5${2:0:8}) +'%Y-%m-%d %T')"
}

# remove the oldest in tree in a set of snapshots
#  @param $1 Path to stack directory
#  @param $2 name of the stack
pop_tail ()
{
    local stack_dir="$1"
    local stack_name="$2"

    # Get the root snapshot (one with no child).
    get_snapshot_child "$stack_dir" "$(cat $stack_dir/$EMU_DIR/HEAD)"
    remove_snapshot "$stack_dir" "$SNAPSHOT_HASH" "$stack_name"
}

# push the latest snapshot to HEAD
#  @param $1 Path to stack directory
#  @param $2 name of the stack
pop_tails ()
{
    local stack_dir="$1"
    local stack_name="$2"

    while [[ $(stack_snapshot_count "$stack_dir") -gt $(stack_max_snapshots "$stack_dir") ]]
    do
        next_snapshot_hash="$(cat $stack_dir/$EMU_DIR/HEAD)"
        pop_tail "$stack_dir" "$stack_name"
    done
}

# push the a snapshot on stack
#  @param  $1 Path to stack directory
#  @param  $2 Name of stack
#  @return    Integer success value (non-zero indicates failure)
push_snapshot_on_stack ()
{
    local stack_dir="$1"
    local stack_name="$2"

    lock_dir "$stack_dir"
    get_rsync_link "$stack_dir"

    if [ $EMU_DRY_RUN ]
    then
        rsync_dry_run="--dry-run"
    else
        pop_tails "$stack_dir" "$stack_name"
    fi

    emu_echo "$stack_name: pushing snapshot ($(stack_snapshot_count $stack_dir) of $(stack_max_snapshots $stack_dir))"

    rsync \
        $EMU_VERBOSE \
        $EMU_PROGRESS \
        $rsync_dry_run \
        --delete \
        --delete-excluded \
        --archive \
        --human-readable \
        --exclude="$SOURCE_DIR/$EMU_DIR/*" \
        --exclude-from="$SOURCE_DIR/$EMU_DIR/excludes" \
        "$RSYNC_LINK" \
        "$SOURCE_DIR/" "$stack_dir/$EMU_DIR/trees/new"
    if (( $? ))
    then
        unlock_dir "$stack_dir"
        return 1
    fi

    generate_hash "$stack_dir"
    generate_snapshot_name "$stack_dir"
    if [ ! $EMU_DRY_RUN ]
    then
        mv "$stack_dir/$EMU_DIR/trees/new" "$stack_dir/$SNAPSHOT"
        ln -s $EMU_VERBOSE "$stack_dir/$SNAPSHOT" "$stack_dir/$EMU_DIR/trees/$HASH"
        generate_node "$stack_dir"
        push_head "$stack_dir"

        if [ -n "$EMU_SNAPSHOT_MESSAGE" ]
        then
            echo "$EMU_SNAPSHOT_MESSAGE" > "$stack_dir/$EMU_DIR/nodes/$HASH.MSG"
        fi
    fi

    unlock_dir "$stack_dir"
    emu_echo "$stack_name: new snapshot '$SNAPSHOT'"
    emu_echo "$stack_name: HEAD at $HASH"

    test -n "$EMU_VERIFY_SNAPSHOT" && emu verify "$stack_name:$HASH"

    return 0
}

# push snapshots to all stack files
#  @var $STACK_FILES List of paths to stack files
push_snapshots ()
{
    local snapshot_failed=0

    for stack_file in $STACK_FILES
    do
        local stack="$(cat $stack_file)"
        local stack_name="$(basename $stack_file)"

        push_snapshot_on_stack "$stack" "$stack_name"
        if (( $? ))
        then
            snapshot_failed=1
            emu_error "snapshot to '$stack_name' failed"
        fi
    done

    return $snapshot_failed
}

main ()
{
    test -n "$EMU_DEBUG" && set -x
    exit_on_help_version $@

    while getopts ":nMvpfFV" OPT
    do
        case $OPT in
            n)
                EMU_DRY_RUN=1
                ;;
            M)
                if [ -z $EDITOR ]
                then
                    emu_error "EDITOR variable not specified"
                    exit $EMU_EXIT_INCORRECT_COMMAND
                fi

                $EDITOR EMU_SNAPSHOT_MSG
                EMU_SNAPSHOT_MESSAGE=$(cat EMU_SNAPSHOT_MSG)
                rm -f EMU_SNAPSHOT_MSG
                ;;
            v)
                EMU_VERBOSE="-v"
                ;;
            p)
                EMU_VERBOSE="-v"
                EMU_PROGRESS="-ph"
                ;;
            f)
                EMU_LOCK_FORCE=1
                ;;
            F)
                EMU_LOCK_FORCE=1
                EMU_LOCK_KILL=1
                ;;
            V)
                EMU_VERIFY_SNAPSHOT=1
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

    get_source_dir_or_fail
    execute_hooks "pre" "$SOURCE_DIR"

    if [[ "$@" == "" ]]
    then
        get_all_stacks
    else
        get_stacks $@
    fi

    lock_dir "$SOURCE_DIR"

    push_snapshots
    if (( $? ))
    then
        emu_error "at least one snapshot failed"
        emu_panic
        exit $EMU_EXIT_ERROR
    fi

    unlock_dir "$SOURCE_DIR"
    execute_hooks "post" "$SOURCE_DIR"
}
main $@
