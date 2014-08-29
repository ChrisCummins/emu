bin_SCRIPTS = 				\
	emu				\
	emu-checkout			\
	emu-clean			\
	emu-init			\
	emu-log				\
	emu-prune			\
	emu-push			\
	emu-sink			\
	emu-squash			\
	emu-verify			\
	$(NULL)

pkglibexec_SCRIPTS = libemu.py

CLEANFILES = $(pkglibexec_SCRIPTS) $(bin_SCRIPTS)

%: %.py
	$(INSTALL) --mode=755 $< $@ &
