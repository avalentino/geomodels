#!/usr/bin/make -f

PYTHON=python3

.PHONY: ext build sdist wheel clean


dafault: ext


ext:
	$(PYTHON) setup.py build_ext --inplace


build:
	$(PYTHON) setup.py build


sdist:
	$(PYTHON) setup.py sdist


wheel:
	$(PYTHON) setup.py bdist_wheel


clean:
	$(PYTHON) setup.py clean --all
	$(RM) -rf MANIFEST dist build geomodels.egg-info
	$(RM) -rf geomodels/__pycache__/ geomodels/*.cpp geomodels/*.so
