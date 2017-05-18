#!/usr/bin/env bash
#
# Copyright (C) 2012-2017 Chris Cummins.
#
# This file is part of emu.
#
# Emu is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# Emu is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public
# License for more details.
#
# You should have received a copy of the GNU General Public License
# along with emu.  If not, see <http://www.gnu.org/licenses/>.

EXIT_NO_TESTS=1
ERROR_LOG=../test.log
tests_passed=0
tests_failed=0
tests_skipped=0

# Always run this.
finish ()
{
    # print test results summary
    if (( $tests_passed )) || (( $tests_failed )); then
        echo ""

        if (( $tests_failed )); then
            echo -n "$tests_passed passed, $tests_failed failed"
        else
            echo -n "All $tests_passed tests passed"
        fi
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

cd test &>/dev/null || {
    echo "Script must be executed from project base directory!" >&2;
    exit 1;
}

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
    test_dir="$1"
else
    # execute all tests
    test_dir="."
fi

test_files="$(find $test_dir -type f \
                 -not -name '.gitignore' \
                 -not -name 'libtest*' \
                 -not -name '*.in' \
                 2>/dev/null | sort)"

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
    if [ "$test_dir" == "." ]
    then
        test_name="${test:2}"
    else
        test_name="$test"
    fi

    echo -ne "\t$test_name "

    pushd . &>/dev/null
    chmod +x $test
    $test &> $test.log

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

    chmod -x $test
    popd &>/dev/null
done
