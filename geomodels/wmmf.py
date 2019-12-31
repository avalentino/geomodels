# -*- coding: utf-8 -*-

"""World Magnetic Model Format tools.

Classes and function for reading and writing files in World Magnetic
Model Format and in IGRF text format.

See: https://geographiclib.sourceforge.io/html/magnetic.html#magneticformat
and https://www.ngdc.noaa.gov/IAGA/vmod/igrf.html.
"""

import os
import typing
import struct
import fnmatch
import pathlib
import datetime
import warnings

from typing import Optional, List
from collections import OrderedDict, namedtuple
from dataclasses import dataclass
from urllib.parse import urlsplit
from urllib.request import urlopen

import numpy as np

from ._typing import PathType


__all__ = ['MetaData', 'SphCoeffSet', 'WmmData', 'import_igrf_txt']


@dataclass
class MetaData:
    """World Magnetic Model Format metadata."""

    Name: str = 'N/A'
    Description: str = 'International Geomagnetic Reference Field'
    URL: str = 'http://ngdc.noaa.gov/IAGA/vmod/igrf.html'
    Publisher: str = 'International Association of Geomagnetism and Aeronomy'
    ReleaseDate: str = 'N/A'
    DataCutOff: str = 'N/A'
    ConversionDate: str = 'N/A'
    DataVersion: int = 1
    Radius: int = 6371200
    NumModels: int = 0
    Epoch: int = 1900
    DeltaEpoch: int = 5
    MinTime: int = 0
    MaxTime: int = 0
    MinHeight: int = -1000
    MaxHeight: int = 600000
    NumConstants: int = 0
    Normalization: int = 1
    ID: str = 'N/A'
    Type = 'linear'
    ByteOrder = 'little'
    N: int = 0
    M: int = 0
    FORMAT_VERSION: int = 1

    _DATEFMT = '%Y-%m-%d'

    def load(self, filename: PathType) -> None:
        """Load a metadata file in WMM format and return a MetaData object."""
        type_map = typing.get_type_hints(self)
        with open(filename) as fd:
            line = next(fd)
            format_ = line.rstrip()
            if format_ not in ('WMMF-1', 'WMMF-2'):
                raise RuntimeError(f'invalid format: {format_!r}')
            else:
                self.FORMAT_VERSION = int(format_[-1])

            for line in fd:
                line = line.split('#', 1)[0]
                line = line.strip()
                if not line:
                    continue

                name, value = line.split(None, 1)
                if not hasattr(self, name):
                    warnings.warn(f'unexpected field: {name!r}')
                    continue
                if callable(getattr(self, name)):
                    warnings.warn(
                        f'field name conflicts with method name: {name!r}')
                    continue
                field_type = type_map.get(name, str)
                setattr(self, name, field_type(value))

    def get_years(self) -> List[int]:
        """Return the list of years associated to teh models."""
        years = range(
            self.Epoch,
            self.Epoch + self.DeltaEpoch * self.NumModels,
            self.DeltaEpoch)
        return list(years)

    def _generation_str(self) -> str:
        if self.Name and self.Name != 'N/A':
            generation = str(int(self.Name[-2:]) - 1)
            if generation == '1':
                generation = f'{generation}st Generation'
            elif generation == '2':
                generation = f'{generation}nd Generation'
            elif generation == '3':
                generation = f'{generation}rd Generation'
            else:
                assert '0' <= generation[-1] <= '9'
                generation = f'{generation}th Generation'
        else:
            generation = ''
        return generation

    def get_id(self) -> str:
        """Return the model ID (eventually inferred by the model name)."""
        if not self.ID or self.ID == 'N/A':
            if not self.Name.startswith('igrf') or len(self.Name) != 6:
                id_ = 'N/A'
            else:
                id_ = self.Name.upper() + '-A'
        else:
            id_ = self.ID
        return id_

    def __str__(self) -> str:
        upper_name = self.Name.upper()

        description = self.Description
        if description == 'International Geomagnetic Reference Field':
            gen = self._generation_str()
            description = f'{description} {gen}'

        id_ = self.get_id()

        return f'''\
WMMF-{self.FORMAT_VERSION}
# A World Magnetic Model (Format {self.FORMAT_VERSION}) file.  \
For documentation on the
# format of this file see
# http://geographiclib.sf.net/html/magnetic.html#magneticformat
Name            {self.Name}
Description     {description}
URL             {self.URL}
Publisher       {self.Publisher}
ReleaseDate     {self.ReleaseDate}
DataCutOff      {self.DataCutOff}
ConversionDate  {self.ConversionDate}
DataVersion     {self.DataVersion}
Radius          {self.Radius}
NumModels       {self.NumModels}
Epoch           {self.Epoch}
DeltaEpoch      {self.DeltaEpoch}
MinTime         {self.MinTime}
MaxTime         {self.MaxTime}
MinHeight       {self.MinHeight}
MaxHeight       {self.MaxHeight}

# The coefficients are stored in a file obtained by appending ".cof" to
# the name of this file.  The coefficients were obtained from {upper_name}.COF
# in the geomag70 distribution.
ID              {id_}
'''

    def save(self, filename: PathType) -> None:
        with open(filename, 'w') as fd:
            fd.write(str(self))


SphCoeffSet = namedtuple('SphCoeffSet', ['C', 'S'])

# @COMPATIBILITY: typing.OrderedDict is new in Python v3.7.2
if hasattr(typing, 'OrderedDict'):
    SphCoeffsType = typing.OrderedDict[str, SphCoeffSet]
else:
    SphCoeffsType = typing.Dict[str, SphCoeffSet]


class WmmData:
    """Magnetic field data."""

    # @COMPATIBILITY: output type is a string (forward declaration)
    #                 Python 3.7 implements PEP 563:
    #                 "Postponed evaluation of annotations"
    #
    #                 from __future__ import annotations
    @classmethod
    def from_metadata_and_coeffs(
            cls, medadata: MetaData, coeffs: SphCoeffsType) -> 'WmmData':
        wmmdata = cls()
        wmmdata.metadata = medadata
        wmmdata.coeffs = coeffs
        wmmdata._check()
        return wmmdata

    def __init__(self, filename: Optional[PathType] = None) -> None:
        self.metadata = MetaData()
        self.coeffs = OrderedDict()

        if filename:
            filename = pathlib.Path(filename)
            self.load(filename)

    def _check(self) -> None:
        years = list(self.coeffs.keys())
        rate = years.pop()
        if rate != 'rate':
            raise RuntimeError('rate coefficients not found')
        if years != [str(year) for year in self.metadata.get_years()]:
            raise RuntimeError('coefficient years does not match metadata')

    @staticmethod
    def _load_sph_coeff_set(fd: typing.IO) -> SphCoeffSet:
        data = fd.read(2 * 4)
        n, m = struct.unpack('<ii', data)

        nc = (m + 1) * (2 * n - m + 2) // 2
        data = np.fromfile(fd, dtype=np.float64, count=nc)
        C = np.zeros((n + 1, m + 1))
        C.T[np.triu_indices(m + 1, 0, n + 1)] = data

        nc = m * (2 * n - m + 1) // 2
        data = np.fromfile(fd, dtype=np.float64, count=nc)
        S = np.zeros((n + 1, m + 1))
        S.T[1:, 1:][np.triu_indices(m, 0, n)] = data

        return SphCoeffSet(C, S)

    def _load_sph_coeffs(self, filename: PathType) -> SphCoeffsType:
        """Load spherical harmonics coeffs from a binary file in WMM format."""
        filename = pathlib.Path(filename)
        years = self.metadata.get_years()

        with open(filename, 'rb') as fd:
            id_ = fd.read(8).decode('utf-8')
            if id_ != self.metadata.ID:
                raise RuntimeError(
                    f'data ID ({id_}) does not match '
                    f'metadata ID ({self.metadata.ID})')
            data = OrderedDict()
            for year in years:
                data[str(year)] = self._load_sph_coeff_set(fd)
            data['rate'] = self._load_sph_coeff_set(fd)

        return data

    def load(self, filename: PathType) -> None:
        """Load metadata and spherical harmonics coefficients."""
        filename = pathlib.Path(filename)
        # self.metadata = MetaData()  # @TODO: check
        self.metadata.load(filename)
        bin_filename = filename.with_suffix(filename.suffix + '.cof')
        self.coeffs = self._load_sph_coeffs(bin_filename)
        self._check()

    @staticmethod
    def _save_sph_coeff_set(fd: typing.IO, coeffs: SphCoeffSet) -> None:
        if coeffs.C.ndim != 2:
            raise TypeError('coefficients are not 2d arrays')
        if coeffs.C.shape != coeffs.S.shape:
            raise ValueError(
                'C and S coefficient do not have the same shape '
                '(C: {}, S: {})'.format(coeffs.C.shape, coeffs.S.shape))

        n, m = coeffs.C.shape
        n -= 1
        m -= 1
        if m > n:
            raise TypeError(
                f'invalid shape of coefficient arrays: '
                f'n={n}, m={m}, expected m <= n')

        # compute the effective size (n, m)
        M = np.abs(coeffs.C) + np.abs(coeffs.S)
        n = np.where(np.sum(M, 0) > 0)[0][-1]
        m = np.where(np.sum(M, 1) > 0)[0][-1]
        if m > n:
            m = n

        data = struct.pack('<ii', n, m)
        fd.write(data)

        data = coeffs.C.T[np.triu_indices(m + 1, 0, n + 1)]
        data = np.ascontiguousarray(data, dtype='<f8')
        fd.write(data.tobytes())

        data = coeffs.S.T[1:, 1:][np.triu_indices(m, 0, n)]
        data = np.ascontiguousarray(data, dtype='<f8')
        fd.write(data.tobytes())

    def _save_sph_coeffs(self, filename: PathType) -> None:
        """Store spherical harmonics coefficients in binary WMM format."""
        id_ = self.metadata.get_id()
        if len(id_) != 8:
            raise ValueError(f'invalid id_ ({id_:r}): expected len(id_) == 8')

        with open(filename, 'wb') as fd:
            fd.write(id_.encode('utf-8'))
            for coeffs in self.coeffs.values():
                self._save_sph_coeff_set(fd, coeffs)

    def save(self, outpath: PathType, force: bool = False) -> None:
        """Save data in WMM format (metadata and binary)."""
        outpath = pathlib.Path(outpath)
        if outpath.is_dir():
            filename = outpath / (self.metadata.Name + '.wmm')
        else:
            filename = outpath
        bin_filename = filename.with_suffix(filename.suffix + '.cof')

        if not force:
            if filename.exists():
                raise RuntimeError(f'"{filename}" already exists')
            if bin_filename.exists():
                raise RuntimeError(f'"{bin_filename}" already exists')

        self.metadata.save(filename)
        self._save_sph_coeffs(bin_filename)


def _metadata_from_txt_header(header: str) -> MetaData:
    """Build a MataData object from the header of a coeffs file
    in text IGRF format."""
    parts = header.split()
    if parts[:3] != ['g/h', 'n', 'm'] or '-' not in parts[-1]:
        raise ValueError(f'invalid header line: {header!r}')

    years = [float(item) for item in parts[3:-1]]

    # check uniform time sampling
    dyears = [b - a for a, b in zip(years[1:], years[:-1])]
    if max(dyears) != min(dyears):
        raise RuntimeError('non uniform time sampling detected')

    metadata = MetaData()
    metadata.ConversionDate = datetime.date.today().strftime(MetaData._DATEFMT)
    metadata.NumModels = len(years)
    metadata.Epoch = int(years[0])
    metadata.DeltaEpoch = int(years[1] - years[0])
    metadata.MinTime = int(years[0])
    metadata.MaxTime = int(years[-1]) + metadata.DeltaEpoch

    return metadata


def import_igrf_txt(path: PathType) -> WmmData:
    """Decode a spherical harmonics coefficient file in IGRF text format.

    :param path:
        the path to a local filename or a remote URL.
    """
    urlobj = urlsplit(os.fspath(path))
    filename = pathlib.Path(urlobj.path)

    pattern = 'igrf[0-9][0-9]coeffs.txt'
    if not fnmatch.fnmatch(filename.name, pattern):
        raise ValueError(
            f'invalid file name ("{filename}"), expected pattern: {pattern!r}')

    if urlobj.scheme in ('', 'file'):
        fd = open(filename)
    else:
        fd = urlopen(path)

    with fd:
        for line in fd:
            if line.startswith('#'):
                continue
            elif line.startswith('g/h'):
                assert filename.stem.endswith('coeffs')
                metadata = _metadata_from_txt_header(line)
                metadata.Name = filename.stem[:-6]
                break
        else:
            raise RuntimeError(f'header line not found in {filename}')

        years = metadata.get_years()
        dtype = [
            ('type', 'S1'),
            ('n', 'int'),
            ('m', 'int'),
        ] + [(f'{year}', 'float64') for year in years] + [
            ('rate', 'float64')
        ]
        dtype = np.dtype(dtype)

        coeffs = np.loadtxt(fd, dtype=dtype)

    n = np.max(coeffs['n'])
    m = np.max(coeffs['m'])

    g_idx = coeffs['type'] == b'g'
    g = coeffs[g_idx]
    h_idx = coeffs['type'] == b'h'
    h = coeffs[h_idx]

    data = OrderedDict()
    for year in years:
        C = np.zeros((n + 1, m + 1))
        C[g['n'], g['m']] = g[str(year)]

        S = np.zeros((n + 1, m + 1))
        S[h['n'], h['m']] = h[str(year)]

        data[str(year)] = SphCoeffSet(C, S)

    C = np.zeros((n + 1, m + 1))
    C[g['n'], g['m']] = g['rate']

    S = np.zeros((n + 1, m + 1))
    S[h['n'], h['m']] = h['rate']

    data['rate'] = SphCoeffSet(C, S)

    return WmmData.from_metadata_and_coeffs(metadata, data)
