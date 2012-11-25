VERSION = 0.0.1

default:
	@echo "  useage: install|uninstall[_usr|_exec]"

install_exec:
	@cp -v emu/emu /usr/local/bin/emu
	@cp -v emu/emu-init /usr/local/bin/emu-init
	@cp -v emu/emu-log /usr/local/bin/emu-log
	@cp -v emu/emu-sink /usr/local/bin/emu-reset
	@cp -v emu/emu-sink /usr/local/bin/emu-restore
	@cp -v emu/emu-sink /usr/local/bin/emu-sink
	@cp -v emu/emu-snapshot /usr/local/bin/emu-snapshot
	@cp -v emu/emu-verify /usr/local/bin/emu-verify

install_lib:
	@cp -v lib/libemu /usr/local/lib

install_usr:
	@cp -rv share/emu /usr/share

install: install_usr install_lib install_exec

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

uninstall_usr:
	@rm -rfv /usr/share/emu

uninstall: uninstall_usr uninstall_lib uninstall_exec

check:
	@bash test/run-tests.sh

test: check

clean:
	@rm -rfv /tmp/emu

release:
	@cd .. && tar czf emu-$(VERSION).tar.gz emu
	@mv -v ../emu-$(VERSION).tar.gz ./
