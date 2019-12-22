#!/usr/bin/make -f

PYTHON=python3
SPHINX_APIDOC=sphinx-apidoc
DOWNLOAD=curl -O

GEOGRAPHICLIB_VERSION=1.50.1
GEOGRAPHICLIB_SRCDIR=GeographicLib-$(GEOGRAPHICLIB_VERSION)
GEOGRAPHICLIB_ARCHIVE=$(GEOGRAPHICLIB_SRCDIR).tar.gz
GEOGRAPHICLIB_BASE_URL=\
https://netcologne.dl.sourceforge.net/project/geographiclib/distrib
GEOGRAPHICLIB_ARCHIVE_URL=$(GEOGRAPHICLIB_BASE_URL)/$(GEOGRAPHICLIB_ARCHIVE)


.PHONY: ext build sdist wheel html check pytest apidoc clean distclean \
        ext-embed wheel-embed pytest-embed geographiclib-static \
        manylinux


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


pytest: ext
	$(PYTHON) -c "form geomodel.test import print_versions; print_versions()"
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
	$(RM) -r $(GEOGRAPHICLIB_SRCDIR)


distclean: clean
	$(RM) $(GEOGRAPHICLIB_ARCHIVE)
	$(RM) -r data


$(GEOGRAPHICLIB_ARCHIVE):
	$(DOWNLOAD) $(GEOGRAPHICLIB_ARCHIVE_URL)


$(GEOGRAPHICLIB_SRCDIR): $(GEOGRAPHICLIB_ARCHIVE)
	tar xvf $<


$(GEOGRAPHICLIB_SRCDIR)/src/libGeographic.a: $(GEOGRAPHICLIB_SRCDIR)
	$(MAKE) -C $(GEOGRAPHICLIB_SRCDIR) CXXFLAGS="-fPIC"


geographiclib-static: $(GEOGRAPHICLIB_SRCDIR)/src/libGeographic.a


wheel-embed: geographiclib-static
	env CPPFLAGS="-I$${PWD}/GeographicLib-1.50.1/include" \
	    LDFLAGS="-L$${PWD}/GeographicLib-1.50.1/src" \
	$(PYTHON) setup.py bdist_wheel


ext-embed: geographiclib-static
	env CPPFLAGS="-I$${PWD}/GeographicLib-1.50.1/include" \
	    LDFLAGS="-L$${PWD}/GeographicLib-1.50.1/src" \
	$(PYTHON) setup.py build_ext --inplace


data:
	$(PYTHON) -m geomodels -d data recommended


pytest-embed: ext-embed data
	$(PYTHON) -c "from geomodels.test import print_versions; print_versions()"
	env GEOGRAPHICLIB_DATA=$${PWD}/data $(PYTHON) -m pytest


manylinux: sdist
	# make sdist
	# docker pull quay.io/pypa/manylinux2010_x86_64
	docker run --rm -v $(shell pwd):/io quay.io/pypa/manylinux2010_x86_64 sh /io/build-manylinux-wheels.sh
