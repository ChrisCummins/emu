QUIET_ = @
QUIET = $(QUIET_$(V))

CP := cp -v
RM := rm -fv

.PHONY: help

help:
	$(QUIET) echo "  usage: <install|uninstall>[_share|_lib|_exec|_doc]"

install_exec:
	$(QUIET) find emu -type f -exec $(CP) {} /usr/local/bin \;

install_lib:
	$(QUIET) find lib -type f -exec $(CP) {} /usr/local/lib \;

install_share:
	$(QUIET) $(CP) -r share/emu /usr/local/share

install_doc:
	$(QUIET) find share/man/ -type f -exec $(CP) {} /usr/local/share/man/man1 \;

install: install_share install_lib install_exec install_doc

uninstall_exec:
	$(QUIET) $(RM) /usr/local/bin/emu
	$(QUIET) $(RM) /usr/local/bin/emu-init
	$(QUIET) $(RM) /usr/local/bin/emu-log
	$(QUIET) $(RM) /usr/local/bin/emu-reset
	$(QUIET) $(RM) /usr/local/bin/emu-restore
	$(QUIET) $(RM) /usr/local/bin/emu-sink
	$(QUIET) $(RM) /usr/local/bin/emu-snapshot
	$(QUIET) $(RM) /usr/local/bin/emu-verify

uninstall_lib:
	$(QUIET) $(RM) /usr/local/lib/libemu

uninstall_share:
	$(QUIET) $(RM) -r /usr/local/share/emu

uninstall_doc:
	$(QUIET) $(RM) /usr/local/share/man/man1/emu*.1

uninstall: uninstall_share uninstall_lib uninstall_exec uninstall_doc

.PHONY: test check clean release

test check:
	$(QUIET) bash test/run-tests.sh

clean:
	$(QUIET) rm -rfv /tmp/emu

release:
	$(QUIET) releases/release.sh
