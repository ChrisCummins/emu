SUBDIRS = 				\
	man				\
	templates			\
	$(NULL)

docdir = $(datadir)/doc/@PACKAGE@
doc_DATA = README

EXTRA_DIST = autogen.sh

.PHONY: check test todo help

if ENABLE_TESTS
check test:
	@./scripts/run-tests.sh
else
check test:
	@echo 'The current project configuration has tests disabled!' >&2
	@echo 'Run the configure script with --enable-tests' >&2
	@exit 1
endif

todo:
	@./scripts/todo.sh

help:
	@echo 'Build targets:'
	@echo '  install    - Install package'
	@echo '  uninstall  - Uninstall package'
	@echo ''
	@echo 'Other targets:'
if ENABLE_TESTS
	@echo '  test       - Run test suite'
endif
	@echo '  todo       - Show all TODO/FIXME flags in source files'
	@echo '  help       - Display this help'
	@echo ''
	@echo 'For further info see the ./README file'
