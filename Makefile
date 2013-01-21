QUIET_ = @
QUIET = $(QUIET_$(V))

.PHONY: help

help:
	$(QUIET) echo "  usage: <install|uninstall>[-<share|lib|exec|doc>]"

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
