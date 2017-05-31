.PHONY: check test install help

check test: install
	python setup.py test
	./scripts/run-tests.sh

install:
	python setup.py install

help:
	@echo "usage: make {install,test}"
