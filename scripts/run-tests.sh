#!/bin/bash

EXIT_NO_TESTS=1
ERROR_LOG=../ERROR.log
tests_passed=0
tests_failed=0
tests_skipped=0

# Always run this.
finish ()
{
    # print test results summary
    if (( $tests_passed )) || (( $tests_failed )); then
        echo ""
    fi

    if (( $tests_failed )); then
        echo -n "$tests_passed passed, $tests_failed failed"
    else
        echo -n "All $tests_passed tests passed"
    fi

    if (( $tests_skipped )); then
        echo -n " ($tests_skipped skipped)"
    fi
    echo ""

    if (( $tests_failed )); then
        failed_tests="$(find . -name '*.log')"

        for log in $failed_tests; do
            log_name="${log%.log}"
            echo "" >> $ERROR_LOG
            echo "$colour_fail${log_name:2}$colour_reset ($(cat $log | tail -n-1))" >> $ERROR_LOG
            cat $log | head -n-1 >> $ERROR_LOG
            rm -rf $log
        done

        echo ''
        echo "A log file of failed tests can be found at '$(basename $ERROR_LOG)'"
    fi

    # One final sweap to make sure all log files are disposed of.
    find . -name '*.log' | xargs rm -f
}
trap finish EXIT

set -a
test_setup ()
{
    source libtest.sh
    rm -rvf "$EMU_TEST_DIR"
    mkdir -pv "$EMU_TEST_DIR"
    mkdir -pv "$EMU_TEST_DIR"/test-source
    pushd "$EMU_TEST_DIR"
}

test_teardown ()
{
    popd
    rm -rvf "$EMU_TEST_DIR"
}

cd tests

# Get rid of any existing error log.
rm -f $ERROR_LOG

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
    test_dir=".$1"
else
    # execute all tests
    test_dir="."
fi

test_files="$(find $1 -type f 2>/dev/null | sort)"

if [ -z "$test_files" ]
then
    echo "No tests found!" >&2
    exit $EXIT_NO_TESTS
fi

# delete old logs
for log in $(find . -name '*.log')
do
    rm -f "$log"
done

# execute tests
for test in $test_files
do
    if [ "$test" != "./.gitignore" ] && [ "$test" != "./libtest.sh" ]
    then
        if [ "$test_dir" == "." ]
        then
            test_name="${test:2}"
        else
            test_name="$test"
        fi

        echo -ne "\t$test_name "

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
