#!/bin/bash

# Test helper functions.
test_setup ()
{
    echo "INFO: Running setup..."
    mkdir -pv /tmp/emu
    mkdir -pv /tmp/emu/test-source
    echo "INFO: Running test..."
}

test_teardown ()
{
    echo "INFO: Running teardown..."
    rm -rvf /tmp/emu
    echo "INFO: Test ended"
}

assert ()
{
    if [ $(test "$1") ]
    then
        echo "ERROR: assert '$1' failed!" >&2
        exit 5
    else
        echo "Assert '$1'"
    fi
}

assert_not ()
{
    if ! [ $(test "$1") ]
    then
        echo "ERROR: assert !'$1' failed!" >&2
        exit 5
    else
        echo "Assert !'$1'"
    fi
}

assert_zero ()
{
    if (( $1 ))
    then
        echo "ERROR: assertion '$1' == 0!" >&2
        exit 5
    else
        echo "Assert '$1' == 0"
    fi
}

assert_non_zero ()
{
    if ! (( $1 ))
    then
        echo "ERROR: assertion '$1' != 0 failed!" >&2
        exit 5
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
        exit 5
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
        exit 5
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
        exit 5
    fi
}

assert_is_not_dir ()
{
    echo "Assert '$1' is not dir"
    if [ -d "$1" ]
    then
        echo "ERROR: assertion '$1' is not dir failed!" >&2
        ls -l "$1"
        exit 5
    fi
}

assert_is_file ()
{
    echo "Assert '$1' is file"
    if [ ! -f "$1" ]
    then
        echo "ERROR: assertion '$1' is file failed!" >&2
        exit 5
    fi
}

assert_is_not_file ()
{
    echo "Assert '$1' is not file"
    if [ -f "$1" ]
    then
        echo "ERROR: assertion '$1' is not file failed!" >&2
        ls -l "$1"
        exit 5
    fi
}

assert_dir_is_empty ()
{
    echo "Assert '$1' is empty"
    if [ $(find "$1" | wc -l) -gt 1 ]
    then
        echo "ERROR: assertion '$1' is empty failed! ($(find "$1" | wc -l))" >&2
        exit 5
    fi
}

assert_dir_is_not_empty ()
{
    echo "Assert '$1' is not empty"
    if [ $(find "$1" | wc -l) -le 1 ]
    then
        echo "ERROR: assertion '$1' is not empty failed! ($(find "$1" | wc -l))" >&2
        exit 5
    fi
}

assert_file_is_empty ()
{
    echo "Assert '$1' is empty"
    if [ $(cat "$1" | wc -l) -gt 0 ]
    then
        cat "$1"
        echo "ERROR: assertion '$1' is empty failed!" >&2
        exit 5
    fi
}

assert_file_is_not_empty ()
{
    echo "Assert '$1' is not empty"
    if [ $(cat "$1" | wc -l) -lt 1 ]
    then
        echo "ERROR: assertion '$1' is not empty failed!" >&2
        exit 5
    fi
}

assert_files_match ()
{
    echo "Assert '$1' and '$2' match"
    diff "$1" "$2"
    if (( $? ))
    then
        echo "ERROR: assertion '$1' matches '$2' failed!" >&2
        exit 5
    fi
}

assert_dirs_match ()
{
    echo "Assert '$1' and '$2' match"
    diff -d "$1" "$2"
    if (( $? ))
    then
        echo "ERROR: assertion '$1' matches '$2' failed!" >&2
        exit 5
    fi
}

assert_string_is_empty ()
{
    echo "Assert string is empty '$1'"
    if [ -n "$1" ]
    then
        echo "ERROR: assertion '$1' is empty failed!" >&2
        exit 5
    fi
}

assert_string_is_not_empty ()
{
    echo "Assert string is not empty '$1'"
    if [ -z "$1" ]
    then
        echo "ERROR: assertion '$1' is not empty failed!" >&2
        exit 5
    fi
}

assert_strings_match ()
{
    echo "Assert strings match: '$1', '$2'"
    if [[ "$1" != "$2" ]]
    then
        echo "ERROR: assert strings match failed!" >&2
        exit 5
    fi
}

export -f test_setup
export -f test_teardown
export -f assert
export -f assert_dir_is_empty
export -f assert_dir_is_not_empty
export -f assert_dirs_match
export -f assert_fail
export -f assert_file_is_empty
export -f assert_file_is_not_empty
export -f assert_files_match
export -f assert_is_dir
export -f assert_is_file
export -f assert_is_not_dir
export -f assert_is_not_file
export -f assert_non_zero
export -f assert_not
export -f assert_string_is_empty
export -f assert_string_is_not_empty
export -f assert_strings_match
export -f assert_success
export -f assert_zero

cd test

# Test results.
PASSED=0
FAILED=0

# Use coloured text if available.
unset TEXT_FAIL
unset TEXT_PASS
unset TEXT_RESET

if [ $(which tput 2>/dev/null) ]
then
    TEXT_FAIL="$(tput setaf 1)"
    TEXT_PASS="$(tput setaf 2)"
    TEXT_RESET="$(tput sgr0)"
fi

# Execute tests.
for TEST in $(find . -type f)
do
    if [ $TEST != "./run-tests.sh" ]
    then
        pushd . &>/dev/null
        echo -n "${TEST:2}"
        ./$TEST &> $TEST.log

        EXIT_CODE=$?
        if (( $EXIT_CODE ))
        then
            echo "${TEXT_FAIL}FAIL${TEXT_RESET}"
            echo "$test failed!" >>$test.log
            test_teardown &>/dev/null
            echo $exit_code >>$test.log
            FAILED=$((FAILED+1))
        else
            echo "${TEXT_PASS}PASS${TEXT_RESET}"
            rm -f $test.log
            PASSED=$((PASSED+1))
        fi

        popd &>/dev/null
    fi
done

# Print test results summary.
if (( $PASSED )) || (( $FAILED ))
then
    echo ""
fi

if (( $FAILED ))
then
    echo "Results: $PASSED passed $FAILED failed"
else
    echo "Results: All $PASSED tests passed"
fi

# Print failed test logs.
for LOG in $(find . -name "*.log")
do
    LOG_NAME="${LOG%.log}"
    echo ""
    echo "$TEXT_FAIL${LOG_NAME:2}$TEXT_RESET ($(cat $LOG | tail -n-1))"
    cat $LOG | head -n-1
    rm -rf $LOG
done
