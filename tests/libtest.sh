#!/bin/bash

set -ax

### Test variables.
EMU_TEST_DIR=/tmp/emu
EMU_DEBUG=1

## EXIT CODES
EXIT_ASSERT_FAIL=5

assert ()
{
    if [ $(test "$1") ]
    then
        exit $EXIT_ASSERT_FAIL
    fi
}

assert_not ()
{
    if ! [ $(test "$1") ]
    then
        exit $EXIT_ASSERT_FAIL
    fi
}

assert_zero ()
{
    if (( $1 ))
    then
        exit $EXIT_ASSERT_FAIL
    fi
}

assert_non_zero ()
{
    if ! (( $1 ))
    then
        exit $EXIT_ASSERT_FAIL
    fi
}

assert_success ()
{
    set +e
    $($1)
    RETURN=$?
    if (( $RETURN ))
    then
        exit $EXIT_ASSERT_FAIL
    fi
    set -e
}

assert_fail ()
{
    set +e
    $($1)
    RETURN=$?
    if ! (( $RETURN ))
    then
        exit $EXIT_ASSERT_FAIL
    fi
    set -e
}

assert_is_dir ()
{
    echo "Assert '$1' is dir"
    if [ ! -d "$1" ]
    then
        exit $EXIT_ASSERT_FAIL
    fi
}

assert_is_not_dir ()
{
    if [ -d "$1" ]
    then
        exit $EXIT_ASSERT_FAIL
    fi
}

assert_is_file ()
{
    if [ ! -f "$1" ]
    then
        exit $EXIT_ASSERT_FAIL
    fi
}

assert_is_not_file ()
{
    if [ -f "$1" ]
    then
        exit $EXIT_ASSERT_FAIL
    fi
}

assert_dir_is_empty ()
{
    if [ $(find "$1" | wc -l) -gt 1 ]
    then
        exit $EXIT_ASSERT_FAIL
    fi
}

assert_dir_is_not_empty ()
{
    if [ $(find "$1" | wc -l) -le 1 ]
    then
        exit $EXIT_ASSERT_FAIL
    fi
}

assert_file_is_empty ()
{
    if [ $(cat "$1" | wc -l) -gt 0 ]
    then
        cat "$1"
        exit $EXIT_ASSERT_FAIL
    fi
}

assert_file_is_not_empty ()
{
    if [ $(cat "$1" | wc -l) -lt 1 ]
    then
        exit $EXIT_ASSERT_FAIL
    fi
}

assert_files_match ()
{
    diff "$1" "$2"
    if (( $? ))
    then
        exit $EXIT_ASSERT_FAIL
    fi
}

assert_dirs_match ()
{
    diff -d "$1" "$2"
    if (( $? ))
    then
        exit $EXIT_ASSERT_FAIL
    fi
}

assert_string_is_empty ()
{
    if [ -n "$1" ]
    then
        exit $EXIT_ASSERT_FAIL
    fi
}

assert_string_is_not_empty ()
{
    if [ -z "$1" ]
    then
        exit $EXIT_ASSERT_FAIL
    fi
}

assert_strings_match ()
{
    if [[ "$1" != "$2" ]]
    then
        exit $EXIT_ASSERT_FAIL
    fi
}
