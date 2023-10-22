#!/usr/bin/make -f

PYTHON=python3
SPHINX_APIDOC=sphinx-apidoc

PKG=geomodels
PKG_VER=$(shell grep __version__ geomodels/__init__.py | cut -d "'" -f 2)
PKG_SRC_ARC=dist/$(PKG)-$(PKG_VER).tar.gz


.PHONY: ext build sdist wheel html man check pytest apidoc clean distclean \
        data fullsdist manylinux


default: ext


ext: geomodels/_ext.cpp
	$(PYTHON) setup.py build_ext --inplace


geomodels/_ext.cpp: geomodels/geoid.pxd geomodels/geoid.pyx \
                    geomodels/gravity.pxd geomodels/gravity.pyx \
                    geomodels/magnetic.pxd geomodels/magnetic.pyx
	$(PYTHON) -m cython -3 --cplus geomodels/_ext.pyx


$(PKG_SRC_ARC):
	$(PYTHON) -m build --sdist


sdist: $(PKG_SRC_ARC)
	cd dist && sha256sum -b *.tar.gz > $$(ls *.tar.gz).sha256


wheel:
	$(PYTHON) -m build --wheel


html: docs/html


docs/html: ext
	$(MAKE) -C docs html
	$(RM) -r docs/html
	if [ -d data ]; then export GEOGRAPHICLIB_DATA=$(PWD)/data; fi && \
	$(MAKE) -C docs doctest
	cp -R docs/_build/html docs/html


man: docs/man/geomodels-cli.1


docs/man/geomodels-cli.1: ext
	mkdir -p docs/man
	env PYTHONPATH=. argparse-manpage \
	    --module geomodels.cli --function get_parser \
	    --project-name "geomodels" \
	    --url "https://github.com/avalentino/geomodels" \
	    --author "Antonio Valentino" \
	    --author-email "antonio dot valentino at tiscali.it" > $@


check: pytest


pytest: ext
	$(PYTHON) -m geomodels info
	if [ -d data ]; then export GEOGRAPHICLIB_DATA=$(PWD)/data; fi && \
	$(PYTHON) -m pytest geomodels


apidoc: ext
	$(RM) -r docs/api
	$(SPHINX_APIDOC) -M -T -e -o docs/api . setup.py geomodels/tests geomodels/*.pyx


clean:
	$(MAKE) -C docs clean
	$(PYTHON) setup.py clean --all
	$(RM) -r MANIFEST dist build geomodels.egg-info .pytest_cache
	$(RM) -r geomodels/__pycache__ geomodels/tests/__pycache__ docs/_build
	$(RM) geomodels/*.cpp geomodels/*.so
	$(RM) extern/geographiclib/include/GeographicLib/Config.h


distclean: clean
	$(RM) -r docs/html
	$(RM) -r data
	$(RM) -r wheelhouse


data: ext
	$(PYTHON) -m geomodels install-data -d data recommended


fullsdist: data html sdist


manylinux: fullsdist
	docker pull quay.io/pypa/manylinux2010_x86_64
	docker run --rm -v $(shell pwd):/io quay.io/pypa/manylinux2010_x86_64 sh /io/build-manylinux-wheels.sh
