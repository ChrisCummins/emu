templatesdir = $(datarootdir)/emu/templates

templates = 				\
	source-templates		\
	stack-templates			\
	$(NULL)

EXTRA_DIST = $(shell find $(templates))

.PHONY: install-data-local
install-data-local:
	mkdir -p $(templatesdir)
	cp -R $(templates) $(templatesdir)
