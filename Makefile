.PHONY: check test install help

PYTHON ?= python

check test: install
	$(PYTHON) setup.py test
	./scripts/run-tests.sh

install:
	$(PYTHON) setup.py install

help:
	@echo "usage: make {install,test}"
