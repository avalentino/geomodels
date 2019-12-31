#!/usr/bin/make -f

PYTHON=python3
SPHINX_APIDOC=sphinx-apidoc
DOWNLOAD=curl -C - -O
GEOGRAPHICLIB_VERSION=1.50.1
GEOGRAPHICLIB_BASEDIR=GeographicLib-$(GEOGRAPHICLIB_VERSION)
GEOGRAPHICLIB_ARCHIVE=$(GEOGRAPHICLIB_BASEDIR).tar.gz
GEOGRAPHICLIB_BASE_URL=\
https://netcologne.dl.sourceforge.net/project/geographiclib/distrib
GEOGRAPHICLIB_ARCHIVE_URL=$(GEOGRAPHICLIB_BASE_URL)/$(GEOGRAPHICLIB_ARCHIVE)

EXTERNAL=external
GEOGRAPHICLIB_SRC=$(EXTERNAL)/$(GEOGRAPHICLIB_BASEDIR)

PKG=geomodels
PKG_VER=$(shell grep __version__ geomodels/__init__.py | cut -d "'" -f 2)
PKG_SRC_ARC=dist/$(PKG)-$(PKG_VER).tar.gz


.PHONY: ext build sdist wheel html man check pytest apidoc clean distclean \
        embed data fullsdidt manylinux


dafault: ext


ext: geomodels/_ext.cpp
	$(PYTHON) setup.py build_ext --inplace


geomodels/_ext.cpp: geomodels/geoid.pxd geomodels/geoid.pyx \
                    geomodels/gravity.pxd geomodels/gravity.pyx \
                    geomodels/magnetic.pxd geomodels/magnetic.pyx
	$(PYTHON) -m cython -3 --cplus geomodels/_ext.pyx


build:
	$(PYTHON) setup.py build


$(PKG_SRC_ARC):
	$(PYTHON) setup.py sdist


sdist: $(PKG_SRC_ARC)
	cd dist && sha256sum -b *.tar.gz > $$(ls *.tar.gz).sha256


wheel:
	$(PYTHON) setup.py bdist_wheel


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


check:
	$(PYTHON) setup.py test


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
	$(RM) $(GEOGRAPHICLIB_ARCHIVE)


distclean: clean
	$(RM) -r docs/html
	$(RM) -r $(EXTERNAL)
	$(RM) -r data
	$(RM) -r wheelhouse


$(GEOGRAPHICLIB_ARCHIVE):
	$(DOWNLOAD) $(GEOGRAPHICLIB_ARCHIVE_URL)


$(GEOGRAPHICLIB_SRC):
	$(MAKE) $(GEOGRAPHICLIB_ARCHIVE)
	mkdir -p $(EXTERNAL)
	tar -C $(EXTERNAL) -xvf $(GEOGRAPHICLIB_ARCHIVE)


data: ext
	$(PYTHON) -m geomodels install-data -d data recommended


embed: $(GEOGRAPHICLIB_SRC)


fullsdist: embed data html sdist


manylinux: fullsdist
	docker pull quay.io/pypa/manylinux2010_x86_64
	docker run --rm -v $(shell pwd):/io quay.io/pypa/manylinux2010_x86_64 sh /io/build-manylinux-wheels.sh
