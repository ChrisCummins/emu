templatesdir = $(datarootdir)/emu/templates

templates = 				\
	source-templates		\
	stack-templates			\
	$(NULL)

.PHONY: install-data-local
install-data-local:
	mkdir -p $(templatesdir)
	cp -R $(templates) $(templatesdir)
