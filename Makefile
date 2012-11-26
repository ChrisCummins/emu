VERSION = 0.0.1

default:
	@echo "  useage: <install|uninstall>[_share|_lib|_exec|_doc]"

install_exec:
	@find emu -type f -exec cp -v {} /usr/local/bin \;

install_lib:
	@find lib -type f -exec cp -v {} /usr/local/bin \;

install_share:
	@cp -rv share/emu /usr/local/share

install_doc:
	@find share/man/ -type f -exec cp -v {} /usr/local/share/man/man1 \;

install: install_share install_lib install_exec install_doc

uninstall_exec:
	@rm -fv /usr/local/bin/emu
	@rm -fv /usr/local/bin/emu-init
	@rm -fv /usr/local/bin/emu-log
	@rm -fv /usr/local/bin/emu-reset
	@rm -fv /usr/local/bin/emu-restore
	@rm -fv /usr/local/bin/emu-sink
	@rm -fv /usr/local/bin/emu-snapshot
	@rm -fv /usr/local/bin/emu-verify

uninstall_lib:
	@rm -fv /usr/local/lib/libemu

uninstall_share:
	@rm -rfv /usr/local/share/emu

uninstall_doc:
	@rm -fv /usr/local/share/man/man1/emu*.1

uninstall: uninstall_share uninstall_lib uninstall_exec uninstall_doc

check:
	@bash test/run-tests.sh

test: check

clean:
	@rm -rfv /tmp/emu

release:
	@releases/release.sh
