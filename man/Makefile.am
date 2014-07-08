if ENABLE_MAN_PAGES
man_MANS =	 			\
	emu.1				\
	emu-checkout.1			\
	emu-clean.1			\
	emu-init.1			\
	emu-log.1			\
	emu-prune.1			\
	emu-push.1			\
	emu-squash.1			\
	emu-stack.1			\
	emu-status.1			\
	emu-verify.1			\
	$(NULL)

CLEANFILES = $(man_MANS)
endif

%.1: %.man
	cp $< $@
