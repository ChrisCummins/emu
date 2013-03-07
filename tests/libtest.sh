#!/bin/bash

## EXIT CODES
EXIT_ASSERT_FAIL=5

## ASSERTIONS
set -ax

assert ()
{
    if [ $(test "$1") ]
    then
        echo "ERROR: assert '$1' failed!" >&2
        exit $EXIT_ASSERT_FAIL
    else
        echo "Assert '$1'"
    fi
}

assert_not ()
{
    if ! [ $(test "$1") ]
    then
        echo "ERROR: assert !'$1' failed!" >&2
        exit $EXIT_ASSERT_FAIL
    else
        echo "Assert !'$1'"
    fi
}

assert_zero ()
{
    if (( $1 ))
    then
        echo "ERROR: assertion '$1' == 0!" >&2
        exit $EXIT_ASSERT_FAIL
    else
        echo "Assert '$1' == 0"
    fi
}

assert_non_zero ()
{
    if ! (( $1 ))
    then
        echo "ERROR: assertion '$1' != 0 failed!" >&2
        exit $EXIT_ASSERT_FAIL
    else
        echo "Assert '$1' != 0"
    fi
}

assert_success ()
{
    set +e
    echo "Assert '$1' succeeds"
    $($1)
    RETURN=$?
    if (( $RETURN ))
    then
        echo "ERROR: assertion '$1' succeeds failed! ($RETURN)" >&2
        exit $EXIT_ASSERT_FAIL
    fi
    set -e
}

assert_fail ()
{
    set +e
    echo "Assert '$1' fails"
    $($1)
    RETURN=$?
    if ! (( $RETURN ))
    then
        echo "ERROR: assertion '$1' fails failed! ($RETURN)" >&2
        exit $EXIT_ASSERT_FAIL
    else
        echo "Assertion succeeded ($RETURN)"
    fi
    set -e
}

assert_is_dir ()
{
    echo "Assert '$1' is dir"
    if [ ! -d "$1" ]
    then
        echo "ERROR: assertion '$1' is dir failed!" >&2
        exit $EXIT_ASSERT_FAIL
    fi
}

assert_is_not_dir ()
{
    echo "Assert '$1' is not dir"
    if [ -d "$1" ]
    then
        echo "ERROR: assertion '$1' is not dir failed!" >&2
        ls -l "$1"
        exit $EXIT_ASSERT_FAIL
    fi
}

assert_is_file ()
{
    echo "Assert '$1' is file"
    if [ ! -f "$1" ]
    then
        echo "ERROR: assertion '$1' is file failed!" >&2
        exit $EXIT_ASSERT_FAIL
    fi
}

assert_is_not_file ()
{
    echo "Assert '$1' is not file"
    if [ -f "$1" ]
    then
        echo "ERROR: assertion '$1' is not file failed!" >&2
        ls -l "$1"
        exit $EXIT_ASSERT_FAIL
    fi
}

assert_dir_is_empty ()
{
    echo "Assert '$1' is empty"
    if [ $(find "$1" | wc -l) -gt 1 ]
    then
        echo "ERROR: assertion '$1' is empty failed! ($(find "$1" | wc -l))" >&2
        exit $EXIT_ASSERT_FAIL
    fi
}

assert_dir_is_not_empty ()
{
    echo "Assert '$1' is not empty"
    if [ $(find "$1" | wc -l) -le 1 ]
    then
        echo "ERROR: assertion '$1' is not empty failed! ($(find "$1" | wc -l))" >&2
        exit $EXIT_ASSERT_FAIL
    fi
}

assert_file_is_empty ()
{
    echo "Assert '$1' is empty"
    if [ $(cat "$1" | wc -l) -gt 0 ]
    then
        cat "$1"
        echo "ERROR: assertion '$1' is empty failed!" >&2
        exit $EXIT_ASSERT_FAIL
    fi
}

assert_file_is_not_empty ()
{
    echo "Assert '$1' is not empty"
    if [ $(cat "$1" | wc -l) -lt 1 ]
    then
        echo "ERROR: assertion '$1' is not empty failed!" >&2
        exit $EXIT_ASSERT_FAIL
    fi
}

assert_files_match ()
{
    echo "Assert '$1' and '$2' match"
    diff "$1" "$2"
    if (( $? ))
    then
        echo "ERROR: assertion '$1' matches '$2' failed!" >&2
        exit $EXIT_ASSERT_FAIL
    fi
}

assert_dirs_match ()
{
    echo "Assert '$1' and '$2' match"
    diff -d "$1" "$2"
    if (( $? ))
    then
        echo "ERROR: assertion '$1' matches '$2' failed!" >&2
        exit $EXIT_ASSERT_FAIL
    fi
}

assert_string_is_empty ()
{
    echo "Assert string is empty '$1'"
    if [ -n "$1" ]
    then
        echo "ERROR: assertion '$1' is empty failed!" >&2
        exit $EXIT_ASSERT_FAIL
    fi
}

assert_string_is_not_empty ()
{
    echo "Assert string is not empty '$1'"
    if [ -z "$1" ]
    then
        echo "ERROR: assertion '$1' is not empty failed!" >&2
        exit $EXIT_ASSERT_FAIL
    fi
}

assert_strings_match ()
{
    echo "Assert strings match: '$1', '$2'"
    if [[ "$1" != "$2" ]]
    then
        echo "ERROR: assert strings match failed!" >&2
        exit $EXIT_ASSERT_FAIL
    fi
}
