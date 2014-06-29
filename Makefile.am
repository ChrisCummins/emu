SUBDIRS = 				\
	emu				\
	Documentation			\
	templates			\
	$(NULL)

docdir = $(datadir)/doc/@PACKAGE@
doc_DATA = README

EXTRA_DIST = autogen.sh

.PHONY: check test todo help
check test:
	@./scripts/run-tests.sh

todo:
	@./scripts/todo.sh

help:
	@echo 'Build targets:'
	@echo '  all        - Build emu'
	@echo '  install    - Install package'
	@echo '  uninstall  - Uninstall package'
	@echo ''
	@echo 'Other targets:'
	@echo '  check      - Run test suite'
	@echo '  todo       - Show all TODO/FIXME flags in source files'
	@echo '  help       - Display this help'
	@echo ''
	@echo '  make V=0|1 [targets] 0 => quiet build (default), 1 => verbose build'
	@echo ''
	@echo 'For further info see the ./README file'
