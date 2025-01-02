#!/usr/bin/make -f

PYTHON=python3
SPHINX_APIDOC=sphinx-apidoc
TARGET=geomodels

.PHONY: default help dist check fullcheck coverage clean cleaner distclean \
        lint docs api man ext data wheels

default: help

help:
	@echo "Usage: make <TARGET>"
	@echo "Available targets:"
	@echo "  help      - print this help message"
	@echo "  dist      - generate the distribution packages (source and wheel)"
	@echo "  check     - run a full test (using pytest)"
	@echo "  fullcheck - run a full test (using tox)"
	@echo "  coverage  - run tests and generate the coverage report"
	@echo "  clean     - clean build artifacts"
	@echo "  cleaner   - clean cache files and working directories of al tools"
	@echo "  distclean - clean all the generated files"
	@echo "  lint      - perform check with code linter (flake8, black)"
	@echo "  docs      - generate the sphinx documentation"
	@echo "  api       - update the API source files in the documentation"
	@echo "  man       - build man pages for CLI programs"
	@echo "  ext       - build Python extensions inplace"
	@echo "  data      - download data needed for testing"
	@echo "  wheels    - build Python wheels"

dist:
	$(PYTHON) -m build
	$(PYTHON) -m twine check dist/*.tar.gz dist/*.whl

check: ext data
	$(PYTHON) -m geomodels info
	if [ -d data ]; then export GEOGRAPHICLIB_DATA="$(PWD)/data"; fi && \
	$(PYTHON) -m pytest --doctest-modules $(TARGET)

fullcheck: data
	if [ -d data ]; then export GEOGRAPHICLIB_DATA="$(PWD)/data"; fi && \
	$(PYTHON) -m tox run

coverage: ext data
	if [ -d data ]; then export GEOGRAPHICLIB_DATA="$(PWD)/data"; fi && \
	$(PYTHON) -m pytest --doctest-modules --cov=$(TARGET) --cov-report=html --cov-report=term

clean:
	$(RM) -r *.*-info build
	find . -name __pycache__ -type d -exec $(RM) -r {} +
	# $(RM) -r __pycache__ */__pycache__ */*/__pycache__ */*/*/__pycache__
	$(RM) $(TARGET)/*.cpp $(TARGET)/*.so $(TARGET)/*.o
	if [ -f docs/Makefile ] ; then $(MAKE) -C docs clean; fi
	$(RM) -r docs/_build
	$(RM) extern/geographiclib/include/GeographicLib/Config.h

cleaner: clean
	$(RM) -r .coverage htmlcov
	$(RM) -r .pytest_cache .tox
	$(RM) -r .mypy_cache .ruff_cache
	$(RM) -r .ipynb_checkpoints

distclean: cleaner
	$(RM) -r dist
	$(RM) -r data
	$(RM) -r wheelhouse

lint:
	$(PYTHON) -m flake8 --count --statistics $(TARGET)
	$(PYTHON) -m pydocstyle --count $(TARGET)
	$(PYTHON) -m isort --check $(TARGET)
	$(PYTHON) -m black --check $(TARGET)
	$(PYTHON) -m mypy --check-untyped-defs --ignore-missing-imports -p $(TARGET)
	ruff check $(TARGET)

api: ext
	$(RM) -r docs/api
	$(SPHINX_APIDOC) --module-first --separate --no-toc -o docs/api \
	  --doc-project "$(TARGET) API" --templatedir docs/_templates/apidoc \
	  $(TARGET) $(TARGET)/tests $(TARGET)/*.pyx

docs: ext data man
	mkdir -p docs/_static
	$(MAKE) -C docs html
	if [ -d data ]; then export GEOGRAPHICLIB_DATA="$(PWD)/data"; fi && \
	$(MAKE) -C docs doctest
	$(MAKE) -C docs linkcheck
	# $(MAKE) -C docs spelling

man: docs/man/geomodels-cli.1

docs/man/geomodels-cli.1: ext
	mkdir -p docs/man
	env PYTHONPATH=. argparse-manpage \
	    --module geomodels.cli --function get_parser \
	    --project-name "$(TARGET)" \
	    --url "https://github.com/avalentino/$(TARGET)" \
	    --author "Antonio Valentino" \
	    --author-email "antonio dot valentino at tiscali.it" > $@

ext: geomodels/_ext.cpp
	$(PYTHON) setup.py build_ext --inplace

geomodels/_ext.cpp: $(TARGET)/geoid.pxd $(TARGET)/geoid.pyx \
                    $(TARGET)/gravity.pxd $(TARGET)/gravity.pyx \
                    $(TARGET)/magnetic.pxd $(TARGET)/magnetic.pyx
	$(PYTHON) -m cython -3 --cplus $(TARGET)/_ext.pyx

data: ext
	$(PYTHON) -m geomodels install-data -d data recommended

wheels:
	# Requires docker
	cibuildwheel --platform auto
