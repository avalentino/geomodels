#!/usr/bin/make -f

PYTHON=python3
#SPHINX_APIDOC=sphinx-apidoc
SPHINX_APIDOC=$(shell dirname $(abspath $(lastword $(MAKEFILE_LIST))))/venv/bin/sphinx-apidoc


.PHONY: ext build sdist wheel html check pytest apidoc clean


dafault: ext


ext:
	$(PYTHON) setup.py build_ext --inplace


build:
	$(PYTHON) setup.py build


sdist:
	$(PYTHON) setup.py sdist


wheel:
	$(PYTHON) setup.py bdist_wheel


html: ext
	$(MAKE) -C docs html


check:
	$(PYTHON) setup.py test


pytest:
	$(PYTHON) -m pytest


apidoc: ext
	$(RM) -r docs/api
	$(SPHINX_APIDOC) -M -e -o docs/api . setup.py geomodels/test
	$(RM) docs/api/geomodels.common.rst \
		  docs/api/geomodels.gravity.rst \
		  docs/api/geomodels.geoid.rst \
		  docs/api/geomodels.magnetic.rst \
		  docs/api/modules.rst
	sed -i '/\(common\|geoid\|gravity\|magnetic\)$$/d' docs/api/geomodels.rst


clean:
	$(PYTHON) setup.py clean --all
	$(RM) -r MANIFEST dist build geomodels.egg-info .pytest_cache
	$(RM) -r geomodels/__pycache__ geomodels/test/__pycache__ docs/_build
	$(RM) geomodels/*.cpp geomodels/*.so
