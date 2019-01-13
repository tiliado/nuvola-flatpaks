# Copyright 2019 Jiří Janoušek <janousek.jiri@gmail.com>
# License: BSD-2-Clause, see file LICENSE at the project root.

.PHONY: docs distclean info check flake8 pylint test mypy all tox setup

MODULE = nufb

all: setup check docs

info:
	cat Makefile

tox:
	tox

check: flake8 mypy pylint test

flake8:
	flake8 $(MODULE)

mypy:
	MYPYPATH=stubs mypy $(MODULE)

pylint:
	pylint --rcfile .pylintrc $(MODULE)

test:
	pytest

venv:
	python3 -m venv venv

setup: venv/.stamp

venv/.stamp: venv requirements.txt requirements-devel.txt
	venv/bin/python3 -m pip install --upgrade pip
	venv/bin/python3 -m pip install --upgrade -r requirements.txt
	venv/bin/python3 -m pip install --upgrade -r requirements-devel.txt
	touch venv/.stamp

docs: venv
	$(MAKE) -C doc html

distclean:
	rm -rf venv
