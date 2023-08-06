#!/usr/bin/make
#
all: run
.PHONY: buildout run test cleanall

buildoutcmd=bin/buildout -t 5

bootstrap-buildout.py:
	wget https://bootstrap.pypa.io/bootstrap-buildout.py

bin/buildout: bootstrap-buildout.py buildout.cfg
	virtualenv-2.7 .
	./bin/python bootstrap-buildout.py
	touch $@

bin/instance: bin/buildout
	${buildoutcmd}
	touch $@

buildout: bin/buildout
	${buildoutcmd}

run: bin/instance
	bin/instance fg

bin/test: bin/buildout
	${buildoutcmd}
	touch $@

test: bin/test
	bin/test --all

cleanall:
	rm -fr bin develop-eggs include .installed.cfg lib .mr.developer.cfg parts downloads eggs
