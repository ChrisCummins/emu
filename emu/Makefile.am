bin_SCRIPTS = 				\
	emu				\
	emu-checkout			\
	emu-clean			\
	emu-init			\
	emu-log				\
	emu-push			\
	emu-stack			\
	emu-status			\
	emu-verify			\
	$(NULL)

pkglibexec_SCRIPTS = libemu libemu.py

CLEANFILES = $(pkglibexec_SCRIPTS) $(bin_SCRIPTS)

%: %.sh
	$(INSTALL) --mode=755 $< $@ &

libemu: libemu.sh
	$(INSTALL) --mode=755 $< $@ &

%: %.py
	$(INSTALL) --mode=755 $< $@ &
