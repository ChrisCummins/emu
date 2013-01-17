QUIET_ = @
QUIET = $(QUIET_$(V))

CP := cp -v
RM := rm -fv

.PHONY: help

help:
	$(QUIET) echo "  usage: <install|uninstall>[-<share|lib|exec|doc>]"

# installer
install-exec:
	$(QUIET) find emu -type f -exec $(CP) {} /usr/local/bin \;

install-lib:
	$(QUIET) find lib -type f -exec $(CP) {} /usr/local/lib \;

install-share:
	$(QUIET) $(CP) -r share/emu /usr/local/share

install-doc:
	$(QUIET) find share/man/ -type f -exec $(CP) {} /usr/local/share/man/man1 \;

install: install-share install-lib install-exec install-doc

# uninstaller
uninstall-exec:
	$(QUIET) $(RM) /usr/local/bin/emu
	$(QUIET) $(RM) /usr/local/bin/emu-init
	$(QUIET) $(RM) /usr/local/bin/emu-log
	$(QUIET) $(RM) /usr/local/bin/emu-reset
	$(QUIET) $(RM) /usr/local/bin/emu-restore
	$(QUIET) $(RM) /usr/local/bin/emu-sink
	$(QUIET) $(RM) /usr/local/bin/emu-snapshot
	$(QUIET) $(RM) /usr/local/bin/emu-verify

uninstall-lib:
	$(QUIET) $(RM) /usr/local/lib/libemu

uninstall-share:
	$(QUIET) $(RM) -r /usr/local/share/emu

uninstall-doc:
	$(QUIET) $(RM) /usr/local/share/man/man1/emu*.1

uninstall: uninstall-share uninstall-lib uninstall-exec uninstall-doc

# misc
.PHONY: test check clean release

test check:
	$(QUIET) bash test/run-tests.sh

clean:
	$(QUIET) rm -rfv /tmp/emu

release:
	$(QUIET) releases/release.sh
