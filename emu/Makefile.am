bin_SCRIPTS = 				\
	emu				\
	emu-clean			\
	emu-init			\
	emu-log				\
	emu-peek			\
	emu-pop				\
	emu-push			\
	emu-stack			\
	emu-status			\
	emu-verify			\
	$(NULL)

pkglibexec_SCRIPTS = libemu

CLEANFILES = $(pkglibexec_SCRIPTS) $(bin_SCRIPTS)

%: %.sh
	$(INSTALL) --mode=755 $< $@ &
