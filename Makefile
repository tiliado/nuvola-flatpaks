# Copyright 2019 Jiří Janoušek <janousek.jiri@gmail.com>
# License: BSD-2-Clause, see file LICENSE at the project root.

.PHONY: help all tox lint docs test setup clean distclean

VENV_NAME ?= venv
VENV_ACTIVATE = . $(VENV_NAME)/bin/activate
PYTHON = ${VENV_NAME}/bin/python3
MODULE = nufb

help:
	@echo "Targets:"
	@echo "- all: setup + lint + test + docs"
	@echo "- tox: Run checks and tests with tox."
	@echo "- lint: Run flake8, mypy and pylint."
	@echo "- test: Runt pytest tests."
	@echo "- docs: Generate documentation."
	@echo "- setup: Set up python3 virtual environment."
	@echo "- clean: Clean built files and cache."
	@echo "- distclean: Clean built files, cache, venv and tox directories."


all: setup lint test docs

tox: setup
	${PYTHON} -m tox

lint: setup
	${PYTHON} -m flake8 $(MODULE)
	MYPYPATH=stubs ${PYTHON} -m mypy $(MODULE)
	${PYTHON} -m pylint --rcfile .pylintrc $(MODULE)

test: setup
	${PYTHON} -m pytest

docs: setup
	$(VENV_ACTIVATE) && $(MAKE) -C doc html
	$(VENV_ACTIVATE) && $(MAKE) -C doc latexpdf

setup: $(VENV_NAME)/activate

$(VENV_NAME)/activate: requirements.txt requirements-devel.txt
	test -d $(VENV_NAME) || python3 -m venv $(VENV_NAME)
	${PYTHON} -m pip install --upgrade pip
	${PYTHON} -m pip install --upgrade -r requirements.txt
	${PYTHON} -m pip install --upgrade -r requirements-devel.txt
	touch $(VENV_NAME)/activate

clean:
	rm -rf doc/_build
	find . -name __pycache__ -exec rm -rf {} \+
	rm -rf .pytest_cache .mypy_cache

distclean: clean
	rm -rf .tox $(VENV_NAME)
