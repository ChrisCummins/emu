VERSION = 0.0.1

default:
	@echo "  useage: install|uninstall[_usr|_exec]"

install_exec:
	@cp emu/emu /usr/local/bin/emu
	@echo "  CP  /usr/local/bin/emu"
	@cp emu/emu-init /usr/local/bin/emu-init
	@echo "  CP  /usr/local/bin/emu-init"
	@cp emu/emu-log /usr/local/bin/emu-log
	@echo "  CP  /usr/local/bin/emu-log"
	@cp emu/emu-sink /usr/local/bin/emu-reset
	@echo "  CP  /usr/local/bin/emu-reset"
	@cp emu/emu-sink /usr/local/bin/emu-restore
	@echo "  CP  /usr/local/bin/emu-restore"
	@cp emu/emu-sink /usr/local/bin/emu-sink
	@echo "  CP  /usr/local/bin/emu-sink"
	@cp emu/emu-snapshot /usr/local/bin/emu-snapshot
	@echo "  CP  /usr/local/bin/emu-snapshot"
	@cp emu/emu-verify /usr/local/bin/emu-verify
	@echo "  CP  /usr/local/bin/emu-verify"

install_lib:
	@cp lib/libemu /usr/local/lib
	@echo "  CP  /usr/local/lib/libemu"

install_usr:
	@cp -r share/emu /usr/share
	@echo "  CP  /usr/share/emu"

install: install_usr install_lib install_exec

uninstall_exec:
	@rm -f /usr/local/bin/emu
	@echo "  RM  /usr/local/bin/emu"
	@rm -f /usr/local/bin/emu-init
	@echo "  RM  /usr/local/bin/emu-init"
	@rm -f /usr/local/bin/emu-log
	@echo "  RM  /usr/local/bin/emu-log"
	@rm -f /usr/local/bin/emu-reset
	@echo "  RM  /usr/local/bin/emu-reset"
	@rm -f /usr/local/bin/emu-restore
	@echo "  RM  /usr/local/bin/emu-restore"
	@rm -f /usr/local/bin/emu-sink
	@echo "  RM  /usr/local/bin/emu-sink"
	@rm -f /usr/local/bin/emu-snapshot
	@echo "  RM  /usr/local/bin/emu-snapshot"
	@rm -f /usr/local/bin/emu-verify
	@echo "  RM  /usr/local/bin/emu-verify"

uninstall_lib:
	@rm -f /usr/local/lib/libemu
	@echo "  RM  /usr/local/lib/libemu"

uninstall_usr:
	@rm -rf /usr/share/emu
	@echo "  RM  /usr/share/emu"

uninstall: uninstall_usr uninstall_lib uninstall_exec

release:
	@cd .. && tar czf emu-$(VERSION).tar.gz emu
	@mv ../emu-$(VERSION).tar.gz ./
	@echo "  TAR emu-0.0.1.tar.gz"
