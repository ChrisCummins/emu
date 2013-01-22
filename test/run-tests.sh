#!/bin/bash

## GLOBAL VARIABLES

EXIT_NO_TESTS=1

## TEST FUNCTIONS

test_setup ()
{
    echo "INFO: Running setup..."
    source libtest.sh
    rm -rvf /tmp/emu
    mkdir -pv /tmp/emu
    mkdir -pv /tmp/emu/test-source
    echo "INFO: Running test..."
}
export -f test_setup

test_teardown ()
{
    echo "INFO: Running teardown..."
    rm -rvf /tmp/emu
    echo "INFO: Test ended"
}
export -f test_teardown

cd test

## LOCAL VARIABLES

tests_passed=0
tests_failed=0
tests_skipped=0

# use coloured text if available
if [ $(which tput 2>/dev/null) ]
then
    colour_pass="$(tput setaf 2)"
    colour_fail="$(tput setaf 1)"
    colour_skip="$(tput setaf 3)"
    colour_reset="$(tput sgr0)"
fi

if [ -n "$1" ]
then
    # pick from subcategory
    test_dir="$1"
else
    # execute all tests
    test_dir="."
fi

test_files="$(find $1 -type f 2>/dev/null)"

if [ -z "$test_files" ]
then
    echo "No tests found!" >&2
    exit $EXIT_NO_TESTS
fi

# delete old logs
for log in $(find . -name "*.log")
do
    rm -fv "$log"
done

# execute tests
for test in $test_files
do
    if [ "$test" != "./run-tests.sh" ] && [ "$test" != "./libtest.sh" ]
    then
        if [ "$test_dir" == "." ]
        then
            test_name="${test:2}"
        else
            test_name="$test"
        fi

        echo -n "$test_name "

        if [ -x "$test" ]
        then
            pushd . &>/dev/null
            ./$test &> $test.log

            exit_code=$?
            if (( $exit_code ))
            then
                echo "${colour_fail}FAIL${colour_reset}"
                echo "$test failed!" >>$test.log
                test_teardown &>/dev/null
                echo $exit_code >>$test.log
                tests_failed=$((tests_failed+1))
            else
                echo "${colour_pass}PASS${colour_reset}"
                rm -f $test.log
                tests_passed=$((tests_passed+1))
            fi

            popd &>/dev/null
        else
            echo "${colour_skip}SKIPPED${colour_reset}"
            tests_skipped=$((tests_skipped+1))
        fi
    fi
done

# print test results summary
if (( $tests_passed )) || (( $tests_failed ))
then
    echo ""
fi

if (( $tests_failed ))
then
    echo -n "$tests_passed passed, $tests_failed failed"
else
    echo -n "All $tests_passed tests passed"
fi

if (( $tests_skipped ))
then
    echo -n " ($tests_skipped skipped)"
fi
echo ""

# print failed test logs
for log in $(find . -name "*.log")
do
    log_name="${log%.log}"
    echo ""
    echo "$colour_fail${log_name:2}$colour_reset ($(cat $log | tail -n-1))"
    cat $log | head -n-1
    rm -rf $log
done
