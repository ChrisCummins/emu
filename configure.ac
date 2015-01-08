AC_PREREQ([2.68])

dnl ================================================================
dnl     Autoconf script for emu.
dnl
dnl To rebuild the configure script from this, execute command
dnl     autoconf
dnl in the directory containing this script.
dnl
dnl Copyright 2014 Chris Cummins.
dnl
dnl Permission is hereby granted, free of charge, to any person obtaining
dnl a copy of this software and associated documentation files (the
dnl "Software"), to deal in the Software without restriction, including
dnl without limitation the rights to use, copy, modify, merge, publish,
dnl distribute, sublicense, and/or sell copies of the Software, and to
dnl permit persons to whom the Software is furnished to do so, subject to
dnl the following conditions:
dnl
dnl The above copyright notice and this permission notice shall be
dnl included in all copies or substantial portions of the Software.
dnl
dnl THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
dnl EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
dnl MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
dnl NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
dnl LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
dnl OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
dnl WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
dnl
dnl Table of contents:
dnl
dnl   1.     Project versions
dnl
dnl   2.     Project details
dnl
dnl   3.     Substitutions
dnl   3.1.     Set the PREFIX
dnl   3.2.     Export the package versioning
dnl   3.3.     Export project variables
dnl
dnl   4.     Build requirements
dnl   4.1.     Do we have the required python binaries?
dnl
dnl   5.     Project configuration
dnl   5.1      Are we generating the man pages?
dnl   5.2      Are we generating the test scripts?
dnl
dnl   6.     Generate files
dnl   6.1.     Generate a config summary document
dnl   6.2.     Dah dah!
dnl
dnl ================================================================


dnl ================================================================
dnl 1. Project versions (i.e. the package version)
dnl ================================================================
m4_define([emu_major_version],[0])
m4_define([emu_minor_version],[1])
m4_define([emu_micro_version],[51])
m4_define([emu_version],[emu_major_version.emu_minor_version.emu_micro_version])


dnl ================================================================
dnl 2. Project details (i.e. the "meta" stuff)
dnl ================================================================
m4_define([author],[chrisc.101@gmail.com])

AC_INIT([emu],[emu_version],[chrisc.101@gmail.com])
AC_CONFIG_SRCDIR([emu/libemu.py])
AC_CONFIG_AUX_DIR([build])

dnl Support for --program-prefix, --program-suffix and
dnl --program-transform-name options
AC_ARG_PROGRAM

dnl Fairly arbitrary, older versions might work too.
AM_INIT_AUTOMAKE([1.11 -Wall foreign no-define -Wno-portability])
AM_SILENT_RULES([yes])


dnl ================================================================
dnl 3. Substitutions (i.e. what we need to substitute in other files)
dnl ================================================================


dnl     ============================================================
dnl     3.1. Set the PREFIX
dnl     ============================================================
AS_IF([test "x$prefix" = "xNONE"],
      [prefix="/usr/local"])

PREFIX="$prefix"
AC_SUBST([PREFIX])


dnl     ============================================================
dnl     3.2. Export the package versioning
dnl     ============================================================
AC_SUBST([EMU_VERSION_MAJOR],[emu_major_version])
AC_SUBST([EMU_VERSION_MINOR],[emu_minor_version])
AC_SUBST([EMU_VERSION_MICRO],[emu_micro_version])
AC_SUBST([EMU_VERSION],[emu_version])


dnl     ============================================================
dnl     3.3. Export project variables
dnl     ============================================================
EMU_TEMPLATE_DIR='templates'
EMU_TEMPLATE_FILES=$(cd "$EMU_TEMPLATE_DIR" && \
                     find . -type f -not -name '.gitignore' \
                                    -not -name 'Makefile*' | tr '\n' ' ')
AC_SUBST(EMU_TEMPLATE_FILES)

SOURCE_TEMPLATES="$prefix/share/emu/templates/source-templates"
AC_SUBST([SOURCE_TEMPLATES])

SINK_TEMPLATES="$prefix/share/emu/templates/sink-templates"
AC_SUBST([SINK_TEMPLATES])

AC_SUBST([MANSECTION], [1])

DATE="$(date +'%B %d, %Y')"
AC_SUBST([DATE])

AC_SUBST([CP], [cp])


dnl ================================================================
dnl 4. Build requirements
dnl ================================================================
AC_PROG_AWK
AC_PROG_INSTALL
AC_PROG_MKDIR_P
AC_PROG_SED
AC_PROG_LN_S
AC_PROG_MAKE_SET


dnl     ============================================================
dnl     4.1. Do we the required python binaries?
dnl     ============================================================
AC_CHECK_PROG([PYTHON_2_7],[python2.7],[python2.7])
AS_IF([test "x$PYTHON_2_7" != x],
      [HAVE_PYTHON_2_7=yes],
      [HAVE_PYTHON_2_7=no
       AC_MSG_ERROR([Required python binary not found.])])
AC_SUBST([HAVE_PYTHON_2_7],[$HAVE_PYTHON_2_7])
AM_CONDITIONAL([HAVE_PYTHON_2_7],[test "x$HAVE_PYTHON_2_7" = xyes])


dnl ================================================================
dnl 5. Project configuration
dnl ================================================================


dnl     ============================================================
dnl     5.1. Are we generating the man pages?
dnl     ============================================================
AC_ARG_ENABLE([man-pages],
              [AS_HELP_STRING([--enable-man-pages],
                              [Generate man pages (default: yes)])],,
              [enable_man_pages=yes])
AM_CONDITIONAL(ENABLE_MAN_PAGES,[test "x$enable_man_pages" = xyes])


dnl     ============================================================
dnl     5.2. Are we generating the test scripts?
dnl     ============================================================
AC_ARG_ENABLE([tests],
              [AS_HELP_STRING([--enable-tests],
                              [Generate tests (default: yes)])],,
              [enable_tests=yes])
AM_CONDITIONAL(ENABLE_TESTS,[test "x$enable_tests" = xyes])


dnl ================================================================
dnl 6. Generate files
dnl ================================================================
AS_IF([test "x$enable_man_pages" = xyes],
      [AC_CONFIG_FILES([
              man/emu-checkout.man
              man/emu-log.man
              man/emu.man
              man/emu-init.man
              man/emu-prune.man
              man/emu-push.man
              man/emu-squash.man
              man/emu-sink.man
              man/emu-clean.man
              man/emu-verify.man])],)


AS_IF([test "x$enable_tests" = xyes],
      [AC_CONFIG_FILES([
              test/clean/in-progress
              test/clean/lock
              test/clean/orphans
              test/clean/deadlink
              test/sink/add
              test/sink/rm
              test/sink/sink
              test/libtest.sh
              test/push/message
              test/push/no-sink
              test/push/max
              test/push/dry-run
              test/push/push
              test/push/verbose
              test/push/excludes
              test/log/no-sink
              test/log/sinks
              test/log/log
              test/log/push
              test/log/summary
              test/log/limit
              test/init/init
              test/init/template
              test/init/files
              test/init/update
              test/init/dirs
              test/init/reinitialize
              test/init/quiet
              test/init/permissions
              test/man
              test/version
              test/verify/hash
              test/verify/invalid-hash
              test/verify/sink-hash])],)


AC_CONFIG_FILES([
        Makefile
        emu/Makefile
        man/Makefile
        templates/Makefile])


AC_OUTPUT


dnl     ============================================================
dnl     5.1. Generate a config summary document
dnl     ============================================================
echo "creating config.summary"

s=config.summary

echo "This file contains a summary of the configuration options generated" > $s
echo "by the configure script, generated at $(date)." >> $s

echo "" >> $s
echo "emu - $EMU_VERSION" >> $s
echo "--------------" >> $s


# Configuration:
echo "" >> $s
echo "Generate man pages:             $enable_man_pages" >> $s
echo "Generate tests:                 $enable_tests" >> $s


dnl     ============================================================
dnl     5.2 Dah dah!
dnl     ============================================================
cat $s | tail -n+3

echo ""
echo "You can now run \`make'."
