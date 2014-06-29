AC_PREREQ([2.68])

m4_define([emu_major_version], [0])
m4_define([emu_minor_version], [0])
m4_define([emu_micro_version], [5])
m4_define([emu_version],
          [emu_major_version.emu_minor_version.emu_micro_version])

AC_INIT([emu],
	[emu_version],
	[chrisc.101@gmail.com])

AC_SUBST([EMU_VERSION_MAJOR], [emu_major_version])
AC_SUBST([EMU_VERSION_MINOR], [emu_minor_version])
AC_SUBST([EMU_VERSION_MICRO], [emu_micro_version])
AC_SUBST([EMU_VERSION], [emu_version])

# Check for programs.
AC_PROG_AWK
AC_PROG_INSTALL
AC_PROG_LN_S
AC_PROG_MAKE_SET

# Makefile portability.
AC_SUBST([CP], [cp])

# Templates.
EMU_TEMPLATE_DIR='templates'
EMU_TEMPLATE_FILES=$(cd "$EMU_TEMPLATE_DIR" && find . -type f | grep -v .gitignore | grep -v Makefile | tr '\n' ' ')
AC_SUBST(EMU_TEMPLATE_FILES)

# Set a default prefix.
AS_IF([test "x$prefix" = "xNONE"],
      [prefix="/usr/local"])

# Useful locations.
LIBEMU="$prefix/libexec/emu/libemu"
AC_SUBST([LIBEMU])

SOURCE_TEMPLATES="$prefix/share/emu/templates/source-templates"
AC_SUBST([SOURCE_TEMPLATES])

STACK_TEMPLATES="$prefix/share/emu/templates/stack-templates"
AC_SUBST([STACK_TEMPLATES])

AC_SUBST([MANSECTION], [1])

DATE="$(date +'%B %d, %Y')"
AC_SUBST([DATE])

AM_INIT_AUTOMAKE([1.11 foreign -Wall -Werror -Wno-portability])

AC_OUTPUT([
Makefile
emu/Makefile
emu/emu-clean.sh
emu/libemu.sh
emu/emu-peek.sh
emu/emu-verify.sh
emu/emu.sh
emu/emu-init.sh
emu/emu-log.sh
emu/emu-status.sh
emu/emu-stack.sh
emu/emu-push.sh
emu/emu-pop.sh
Documentation/Makefile
Documentation/man/Makefile
Documentation/man/emu-status.man
Documentation/man/emu-log.man
Documentation/man/emu-pop.man
Documentation/man/emu.man
Documentation/man/emu-init.man
Documentation/man/emu-push.man
Documentation/man/emu-stack.man
Documentation/man/emu-clean.man
Documentation/man/emu-verify.man
Documentation/man/emu-peek.man
templates/Makefile
tests/peek/peek
tests/clean/in-progress
tests/clean/lock
tests/clean/orphans
tests/clean/deadlink
tests/clean/debug
tests/stack/show
tests/stack/add
tests/stack/rm
tests/stack/stack
tests/stack/quiet
tests/libtest.sh
tests/libemu/traps
tests/libemu/echo
tests/libemu/dir
tests/libemu/lock
tests/libemu/fail
tests/libemu/hooks
tests/libemu/variables
tests/libemu/panic
tests/libemu/stack
tests/libemu/permissions
tests/pop/pop
tests/push/message
tests/push/no-stack
tests/push/verify
tests/push/max
tests/push/dry-run
tests/push/force
tests/push/push
tests/push/verbose
tests/push/excludes
tests/push/mutex
tests/log/no-stack
tests/log/stacks
tests/log/log
tests/log/push
tests/log/summary
tests/log/limit
tests/init/init
tests/init/template
tests/init/files
tests/init/update
tests/init/dirs
tests/init/reinitialize
tests/init/quiet
tests/init/permissions
tests/init/clean
tests/man
tests/version
tests/verify/hash
tests/verify/invalid-hash
tests/verify/stack-hash
])
