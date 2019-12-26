#!/bin/bash
# Based on: https://github.com/pypa/python-manylinux-demo 9700d97 17 Dec 2016
#
# It is assumed that the docker image has been run as follows::
#
#   $ make sdist
#   $ docker pull quay.io/pypa/manylinux1_x86_64
#   $ docker run --rm -v $(pwd):/io quay.io/pypa/manylinux1_x86_64 /io/build-manylinux-wheels.sh
#
# For interactive sessions please use::
#
#   $ make sdist
#   $ docker pull quay.io/pypa/manylinux1_x86_64
#   $ docker run -it -v $(pwd):/io quay.io/pypa/manylinux1_x86_64
#   $ cd /io
#   $ sh build-manylinux-wheels.sh

set -e -x

PKG=geomodels
GEOGRAPHICLIB_DATA=/io/data

# Compile wheels
for PYBIN in /opt/python/cp3[6-9]*/bin; do
    "${PYBIN}/pip" install -r /io/requirements-dev.txt
    "${PYBIN}/pip" wheel /io/dist/${PKG}*.tar.gz --wheel-dir wheelhouse/
done

# Bundle external shared libraries into the wheels
for whl in wheelhouse/${PKG}*.whl; do
    auditwheel repair "${whl}" --wheel-dir /io/wheelhouse/
done

# Install packages and test
for PYBIN in /opt/python/cp3[6-9]*/bin/; do
    "${PYBIN}/pip" install ${PKG} --no-index -f /io/wheelhouse
    "${PYBIN}/python" -m ${PKG} install-data -d ${GEOGRAPHICLIB_DATA} recommended
    env GEOGRAPHICLIB_DATA=${GEOGRAPHICLIB_DATA} \
    "${PYBIN}/python" -m pytest --pyargs ${PKG}
done
