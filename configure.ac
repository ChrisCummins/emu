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
emu/libemu.sh
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
test/peek/peek
test/clean/in-progress
test/clean/lock
test/clean/orphans
test/clean/deadlink
test/clean/debug
test/stack/show
test/stack/add
test/stack/rm
test/stack/stack
test/stack/quiet
test/libtest.sh
test/libemu/traps
test/libemu/echo
test/libemu/dir
test/libemu/lock
test/libemu/fail
test/libemu/hooks
test/libemu/variables
test/libemu/panic
test/libemu/stack
test/libemu/permissions
test/pop/pop
test/push/message
test/push/no-stack
test/push/verify
test/push/max
test/push/dry-run
test/push/force
test/push/push
test/push/verbose
test/push/excludes
test/push/mutex
test/log/no-stack
test/log/stacks
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
test/init/clean
test/man
test/version
test/verify/hash
test/verify/invalid-hash
test/verify/stack-hash
])
