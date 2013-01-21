#!/bin/bash

## EXIT CODES
EXIT_ASSERT_FAIL=5

## ASSERTIONS

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
export -f assert

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
export -f assert_not

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
export -f assert_zero

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
export -f assert_non_zero

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
export -f assert_success

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
export -f assert_fail

assert_is_dir ()
{
    echo "Assert '$1' is dir"
    if [ ! -d "$1" ]
    then
        echo "ERROR: assertion '$1' is dir failed!" >&2
        exit $EXIT_ASSERT_FAIL
    fi
}
export -f assert_is_dir

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
export -f assert_is_not_dir

assert_is_file ()
{
    echo "Assert '$1' is file"
    if [ ! -f "$1" ]
    then
        echo "ERROR: assertion '$1' is file failed!" >&2
        exit $EXIT_ASSERT_FAIL
    fi
}
export -f assert_is_file

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
export -f assert_is_not_file

assert_dir_is_empty ()
{
    echo "Assert '$1' is empty"
    if [ $(find "$1" | wc -l) -gt 1 ]
    then
        echo "ERROR: assertion '$1' is empty failed! ($(find "$1" | wc -l))" >&2
        exit $EXIT_ASSERT_FAIL
    fi
}
export -f assert_dir_is_empty

assert_dir_is_not_empty ()
{
    echo "Assert '$1' is not empty"
    if [ $(find "$1" | wc -l) -le 1 ]
    then
        echo "ERROR: assertion '$1' is not empty failed! ($(find "$1" | wc -l))" >&2
        exit $EXIT_ASSERT_FAIL
    fi
}
export -f assert_dir_is_not_empty

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
export -f assert_file_is_empty

assert_file_is_not_empty ()
{
    echo "Assert '$1' is not empty"
    if [ $(cat "$1" | wc -l) -lt 1 ]
    then
        echo "ERROR: assertion '$1' is not empty failed!" >&2
        exit $EXIT_ASSERT_FAIL
    fi
}
export -f assert_file_is_not_empty

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
export -f assert_files_match

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
export -f assert_dirs_match

assert_string_is_empty ()
{
    echo "Assert string is empty '$1'"
    if [ -n "$1" ]
    then
        echo "ERROR: assertion '$1' is empty failed!" >&2
        exit $EXIT_ASSERT_FAIL
    fi
}
export -f assert_string_is_empty

assert_string_is_not_empty ()
{
    echo "Assert string is not empty '$1'"
    if [ -z "$1" ]
    then
        echo "ERROR: assertion '$1' is not empty failed!" >&2
        exit $EXIT_ASSERT_FAIL
    fi
}
export -f assert_string_is_not_empty

assert_strings_match ()
{
    echo "Assert strings match: '$1', '$2'"
    if [[ "$1" != "$2" ]]
    then
        echo "ERROR: assert strings match failed!" >&2
        exit $EXIT_ASSERT_FAIL
    fi
}
export -f assert_strings_match
