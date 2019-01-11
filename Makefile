.PHONY: docs distclean info check flake8 pylint test mypy all

MODULE = nufb

info:
	cat Makefile

all: check docs

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
	venv/bin/python3 -m pip install --upgrade pip
	venv/bin/python3 -m pip install --upgrade -r requirements.txt
	venv/bin/python3 -m pip install --upgrade -r requirements-devel.txt
	touch venv

docs: venv
	$(MAKE) -C doc html

distclean:
	rm -rf venv
