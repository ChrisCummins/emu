QUIET_ = @
QUIET = $(QUIET_$(V))

VERSION = 0.0.1

.PHONY: default

default:
	$(QUIET) echo "  useage: <install|uninstall>[_share|_lib|_exec|_doc]"

install_exec:
	$(QUIET) find emu -type f -exec cp -v {} /usr/local/bin \;

install_lib:
	$(QUIET) find lib -type f -exec cp -v {} /usr/local/lib \;

install_share:
	$(QUIET) cp -rv share/emu /usr/local/share

install_doc:
	$(QUIET) find share/man/ -type f -exec cp -v {} /usr/local/share/man/man1 \;

install: install_share install_lib install_exec install_doc

uninstall_exec:
	$(QUIET) rm -fv /usr/local/bin/emu
	$(QUIET) rm -fv /usr/local/bin/emu-init
	$(QUIET) rm -fv /usr/local/bin/emu-log
	$(QUIET) rm -fv /usr/local/bin/emu-reset
	$(QUIET) rm -fv /usr/local/bin/emu-restore
	$(QUIET) rm -fv /usr/local/bin/emu-sink
	$(QUIET) rm -fv /usr/local/bin/emu-snapshot
	$(QUIET) rm -fv /usr/local/bin/emu-verify

uninstall_lib:
	$(QUIET) rm -fv /usr/local/lib/libemu

uninstall_share:
	$(QUIET) rm -rfv /usr/local/share/emu

uninstall_doc:
	$(QUIET) rm -fv /usr/local/share/man/man1/emu*.1

uninstall: uninstall_share uninstall_lib uninstall_exec uninstall_doc

.PHONY: test check clean release

test check:
	$(QUIET) bash test/run-tests.sh

clean:
	$(QUIET) rm -rfv /tmp/emu

release:
	$(QUIET) releases/release.sh
