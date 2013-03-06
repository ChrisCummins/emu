QUIET_ = @
QUIET = $(QUIET_$(V))

.PHONY: help

help:
	@echo 'Cleaning targets:'
	@echo '  clean           - Remove temporary files'
	@echo ''
	@echo 'Install targets:'
	@echo '  install         - Run all install targets marked with a \'*\''
	@echo '* install-share   - Install the share files'
	@echo '* install-lib     - Install library files'
	@echo '* install-exec    - Install the executable files'
	@echo '* install-doc     - Install the documentation'
	@echo ''
	@echo 'Uninstall targets:'
	@echo '  uninstall       - Run all uninstall targets marked with a \'*\''
	@echo '* uninstall-share - Install the share files'
	@echo '* uninstall-lib   - Install library files'
	@echo '* uninstall-exec  - Install the executable files'
	@echo '* uninstall-doc   - Install the documentation'
	@echo ''
	@echo 'Other targets:'
	@echo '  test            - Run the test suite (must be installed)'
	@echo '  help            - Display this help'
	@echo ''
	@echo '  make V=0|1 [targets] 0 => quiet build (default), 1 => verbose build'
	@echo ''
	@echo 'For further info see the ./README file'

# installer
install-exec:
	find emu -type f -exec cp -v {} /usr/local/bin \;

install-lib:
	find lib -type f -exec cp -v {} /usr/local/lib \;

install-share:
	cp -r share/emu /usr/local/share

install-doc:
	find share/man/ -type f -exec cp -v {} /usr/local/share/man/man1 \;

install: install-share install-lib install-exec install-doc

# uninstaller
uninstall-exec:
	rm -f /usr/local/bin/emu
	rm -f /usr/local/bin/emu-init
	rm -f /usr/local/bin/emu-log
	rm -f /usr/local/bin/emu-reset
	rm -f /usr/local/bin/emu-restore
	rm -f /usr/local/bin/emu-sink
	rm -f /usr/local/bin/emu-snapshot
	rm -f /usr/local/bin/emu-verify

uninstall-lib:
	rm -f /usr/local/lib/libemu

uninstall-share:
	rm -fr /usr/local/share/emu

uninstall-doc:
	rm -f /usr/local/share/man/man1/emu*.1

uninstall: uninstall-share uninstall-lib uninstall-exec uninstall-doc

# misc
.PHONY: test check clean release

test check:
	$(QUIET) bash test/run-tests.sh $(TEST)

clean:
	rm -rfv /tmp/emu
