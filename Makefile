#!/usr/bin/make -f

PYTHON=python3

.PHONY: ext build sdist wheel check pytest clean


dafault: ext


ext:
	$(PYTHON) setup.py build_ext --inplace


build:
	$(PYTHON) setup.py build


sdist:
	$(PYTHON) setup.py sdist


wheel:
	$(PYTHON) setup.py bdist_wheel


check:
	$(PYTHON) setup.py test


pytest:
	$(PYTHON) -m pytest


clean:
	$(PYTHON) setup.py clean --all
	$(RM) -r MANIFEST dist build geomodels.egg-info .pytest_cache
	$(RM) -r geomodels/__pycache__ geomodels/test/__pycache__
	$(RM) geomodels/*.cpp geomodels/*.so
