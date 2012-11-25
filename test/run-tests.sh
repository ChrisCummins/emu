#!/bin/bash

# Test helper functions.
test_setup ()
{
    echo "INFO: Running setup..."
    mkdir -pv /tmp/emu/test-source
    mkdir -pv /tmp/emu/test-sink
    echo "INFO: Running test..."
}

test_teardown ()
{
    echo "INFO: Running teardown..."
    rm -rvf /tmp/emu/test-source
    rm -rvf /tmp/emu/test-sink
    echo "INFO: Test ended"
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
    echo "Assert '$1' succeeds"
    if (( $($1) ))
    then
        echo "ERROR: assertion '$1' succeeds failed!" >&2
        exit 5
    fi
}

assert_fail ()
{
    echo "Assert '$1' fails"
    if ! (( $($1) ))
    then
        echo "ERROR: assertion '$1' failed!" >&2
        exit 5
    fi
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
    if [ $(cat "$1" | wc -l) -le 1 ]
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

export -f test_setup
export -f test_teardown
export -f assert_zero
export -f assert_non_zero
export -f assert_success
export -f assert_fail
export -f assert_is_dir
export -f assert_is_not_dir
export -f assert_is_file
export -f assert_is_not_file
export -f assert_dir_is_empty
export -f assert_dir_is_not_empty
export -f assert_file_is_empty
export -f assert_file_is_not_empty
export -f assert_files_match
export -f assert_dirs_match

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
for TEST in $(ls)
do
    if [ $TEST != "run-tests.sh" ] && [ $TEST != "." ]
    then
        pushd . &>/dev/null
        echo -n "$TEST"
        ./$TEST &> $TEST.log

        EXIT_CODE=$?
        if (( $EXIT_CODE ))
        then
            echo "$TEXT_FAIL FAIL$TEXT_RESET"
            echo "$TEST failed!" >>$TEST.log
            test_teardown &>/dev/null
            echo $EXIT_CODE >>$TEST.log
            FAILED=$((FAILED+1))
        else
            echo "$TEXT_PASS PASS$TEXT_RESET"
            rm -f $TEST.log
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
for LOG in $(find . -name "*.log" -printf "%f\n")
do
    echo ""
    echo "$TEXT_FAIL${LOG%.log}$TEXT_RESET ($(cat $LOG | tail -n-1))"
    cat $LOG | head -n-1
    rm -rf $LOG
done