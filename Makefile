#!/usr/bin/make -f

PYTHON=python3

.PHONY: sdist clean


sdist:
	$(PYTHON) setup.py sdist


clean:
	$(PYTHON) setup.py clean --all
	$(RM) -rf MANIFEST dist build
	$(RM) -rf geomodels/__pycache__/ geomodels/*.cpp geomodels/*.so
