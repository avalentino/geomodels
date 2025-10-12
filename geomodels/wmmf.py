"""World Magnetic Model Format tools.

Classes and function for reading and writing files in World Magnetic
Model Format and in IGRF text format.

See: https://geographiclib.sourceforge.io/C++/doc/magnetic.html#magneticformat
and https://www.ngdc.noaa.gov/IAGA/vmod/igrf.html.
"""

from __future__ import annotations

import struct
import typing
import fnmatch
import pathlib
import datetime
import warnings
from collections import OrderedDict, namedtuple
from dataclasses import dataclass
from urllib.parse import urlsplit
from urllib.request import urlopen

import numpy as np

if typing.TYPE_CHECKING:
    from ._typing import PathType

__all__ = ["MetaData", "SphCoeffSet", "WmmData", "import_igrf_txt"]


@dataclass
class MetaData:
    """World Magnetic Model Format metadata."""

    Name: str = "N/A"
    Description: str = "International Geomagnetic Reference Field"
    URL: str = "http://ngdc.noaa.gov/IAGA/vmod/igrf.html"
    Publisher: str = "International Association of Geomagnetism and Aeronomy"
    ReleaseDate: str = "N/A"
    DataCutOff: str = "N/A"
    ConversionDate: str = "N/A"
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
    ID: str = "N/A"
    Type = "linear"
    ByteOrder = "little"
    N: int = 0  # noqa: VNE001
    M: int = 0  # noqa: VNE001
    FORMAT_VERSION: int = 1

    _DATEFMT = "%Y-%m-%d"

    def load(self, filename: PathType) -> None:
        """Load a metadata file in WMM format and return a MetaData object."""
        type_map = typing.get_type_hints(self)
        with open(filename) as fd:
            line = next(fd)
            format_ = line.rstrip()
            if format_ not in ("WMMF-1", "WMMF-2"):
                raise RuntimeError(f"invalid format: {format_!r}")
            self.FORMAT_VERSION = int(format_[-1])

            for line in fd:
                line = line.split("#", 1)[0]
                line = line.strip()
                if not line:
                    continue

                name, value = line.split(None, 1)
                if not hasattr(self, name):
                    warnings.warn(f"unexpected field: {name!r}", stacklevel=2)
                    continue
                if callable(getattr(self, name)):
                    warnings.warn(
                        f"field name conflicts with method name: {name!r}",
                        stacklevel=2,
                    )
                    continue
                field_type = type_map.get(name, str)
                setattr(self, name, field_type(value))

    def get_years(self) -> list[int]:
        """Return the list of years associated to the models."""
        years = range(
            self.Epoch,
            self.Epoch + self.DeltaEpoch * self.NumModels,
            self.DeltaEpoch,
        )
        return list(years)

    def _generation_str(self) -> str:
        if self.Name and self.Name != "N/A":
            generation = str(int(self.Name[-2:]) - 1)
            if generation == "1":
                return f"{generation}st Generation"
            if generation == "2":
                return f"{generation}nd Generation"
            if generation == "3":
                return f"{generation}rd Generation"

            assert "0" <= generation[-1] <= "9"
            return f"{generation}th Generation"
        return ""

    def get_id(self) -> str:
        """Return the model ID (eventually inferred by the model name)."""
        if not self.ID or self.ID == "N/A":
            if not self.Name.startswith("igrf") or len(self.Name) != 6:
                return "N/A"
            return self.Name.upper() + "-A"
        return self.ID

    def __str__(self) -> str:
        """Return the string representation of the MetaDAta object."""
        upper_name = self.Name.upper()

        description = self.Description
        if description == "International Geomagnetic Reference Field":
            gen = self._generation_str()
            description = f"{description} {gen}"

        id_ = self.get_id()

        return f"""\
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
"""  # noqa: E800,N400

    def save(self, filename: PathType) -> None:
        """Save metadata in WMM format."""
        with open(filename, "w") as fd:
            fd.write(str(self))


SphCoeffSet = namedtuple("SphCoeffSet", ["C", "S"])
SphCoeffsType = OrderedDict[str, SphCoeffSet]


class WmmData:
    """Magnetic field data."""

    @classmethod
    def from_metadata_and_coeffs(
        cls, metadata: MetaData, coeffs: SphCoeffsType
    ) -> WmmData:
        """Instantiate a WmmData object from metadata and coefficients."""
        wmmdata = cls()
        wmmdata.metadata = metadata
        wmmdata.coeffs = coeffs
        wmmdata._check()  # noqa: SF01
        return wmmdata

    def __init__(self, filename: PathType | None = None) -> None:
        """Initialize a WmmData instance."""
        self.metadata = MetaData()
        self.coeffs: SphCoeffsType = OrderedDict()

        if filename:
            filename = pathlib.Path(filename)
            self.load(filename)

    def _check(self) -> None:
        years = list(self.coeffs.keys())
        rate = years.pop()
        if rate != "rate":
            raise RuntimeError("rate coefficients not found")
        if years != [str(year) for year in self.metadata.get_years()]:
            raise RuntimeError("coefficient years does not match metadata")

    @staticmethod
    def _load_sph_coeff_set(fd: typing.IO) -> SphCoeffSet:
        data = fd.read(2 * 4)
        lines, cols = struct.unpack("<ii", data)

        nc = (cols + 1) * (2 * lines - cols + 2) // 2
        data = np.fromfile(fd, dtype=np.float64, count=nc)
        cosine_coef = np.zeros((lines + 1, cols + 1))
        cosine_coef.T[np.triu_indices(cols + 1, 0, lines + 1)] = data

        nc = cols * (2 * lines - cols + 1) // 2
        data = np.fromfile(fd, dtype=np.float64, count=nc)
        sine_coef = np.zeros((lines + 1, cols + 1))
        sine_coef.T[1:, 1:][np.triu_indices(cols, 0, lines)] = data

        return SphCoeffSet(cosine_coef, sine_coef)

    def _load_sph_coeffs(self, filename: PathType) -> SphCoeffsType:
        """Load spherical harmonics coeffs from a binary file in WMM format."""
        filename = pathlib.Path(filename)
        years = self.metadata.get_years()

        with open(filename, "rb") as fd:
            id_ = fd.read(8).decode("utf-8")
            if id_ != self.metadata.ID:
                raise RuntimeError(
                    f"data ID ({id_}) does not match "
                    f"metadata ID ({self.metadata.ID})"
                )
            data = OrderedDict()
            for year in years:
                data[str(year)] = self._load_sph_coeff_set(fd)
            data["rate"] = self._load_sph_coeff_set(fd)

        return data

    def load(self, filename: PathType) -> None:
        """Load metadata and spherical harmonics coefficients."""
        filename = pathlib.Path(filename)
        # self.metadata = MetaData()  # @TODO: check
        self.metadata.load(filename)
        bin_filename = filename.with_suffix(filename.suffix + ".cof")
        self.coeffs = self._load_sph_coeffs(bin_filename)
        self._check()

    @staticmethod
    def _save_sph_coeff_set(fd: typing.IO, coeffs: SphCoeffSet) -> None:
        if coeffs.C.ndim != 2:
            raise TypeError("coefficients are not 2d arrays")
        if coeffs.C.shape != coeffs.S.shape:
            raise ValueError(
                "C and S coefficient do not have the same shape "
                f"(C: {coeffs.C.shape}, S: {coeffs.S.shape})"
            )

        lines, cols = coeffs.C.shape
        lines -= 1
        cols -= 1
        if cols > lines:
            raise TypeError(
                "invalid shape of coefficient arrays: "
                f"n={lines}, m={cols}, expected m <= n"
            )

        # compute the effective size (n, m)
        size = np.abs(coeffs.C) + np.abs(coeffs.S)
        lines = np.where(np.sum(size, 0) > 0)[0][-1]
        cols = np.where(np.sum(size, 1) > 0)[0][-1]
        if cols > lines:
            cols = lines

        bytes_ = struct.pack("<ii", lines, cols)
        fd.write(bytes_)

        data = coeffs.C.T[np.triu_indices(cols + 1, 0, lines + 1)]
        data = np.ascontiguousarray(data, dtype="<f8")
        fd.write(data.tobytes())

        data = coeffs.S.T[1:, 1:][np.triu_indices(cols, 0, lines)]
        data = np.ascontiguousarray(data, dtype="<f8")
        fd.write(data.tobytes())

    def _save_sph_coeffs(self, filename: PathType) -> None:
        """Store spherical harmonics coefficients in binary WMM format."""
        id_ = self.metadata.get_id()
        if len(id_) != 8:
            raise ValueError(f"invalid id_ ({id_:r}): expected len(id_) == 8")

        with open(filename, "wb") as fd:
            fd.write(id_.encode("utf-8"))
            for coeffs in self.coeffs.values():
                self._save_sph_coeff_set(fd, coeffs)

    def save(self, outpath: PathType, force: bool = False) -> None:
        """Save data in WMM format (metadata and binary)."""
        outpath = pathlib.Path(outpath)
        if outpath.is_dir():
            filename = outpath / (self.metadata.Name + ".wmm")
        else:
            filename = outpath
        bin_filename = filename.with_suffix(filename.suffix + ".cof")

        if not force:
            if filename.exists():
                raise RuntimeError(f'"{filename}" already exists')
            if bin_filename.exists():
                raise RuntimeError(f'"{bin_filename}" already exists')

        self.metadata.save(filename)
        self._save_sph_coeffs(bin_filename)


def _metadata_from_txt_header(header: str) -> MetaData:
    """Build a MetaData object from the header of a coeff file.

    The coeff file is expected to be in text IGRF format.
    """
    parts = header.split()
    if parts[:3] != ["g/h", "n", "m"] or "-" not in parts[-1]:
        raise ValueError(f"invalid header line: {header!r}")

    years = [float(item) for item in parts[3:-1]]

    # check uniform time sampling
    dyears = [b - a for a, b in zip(years[1:], years[:-1], strict=True)]
    if max(dyears) != min(dyears):
        raise RuntimeError("non uniform time sampling detected")

    today = datetime.datetime.now(tz=datetime.timezone.utc).date()
    metadata = MetaData()
    metadata.ConversionDate = today.strftime(MetaData._DATEFMT)  # noqa: SF01
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
    filename = pathlib.Path(path)
    urlobj = urlsplit(filename.as_uri())

    pattern = "igrf[0-9][0-9]coeffs.txt"
    if not fnmatch.fnmatch(filename.name, pattern):
        raise ValueError(
            f'invalid file name ("{filename}"), expected pattern: {pattern!r}'
        )

    if urlobj.scheme in ("", "file"):
        fd = open(filename)  # noqa: SIM115
    else:
        fd = urlopen(str(path))  # noqa: S310

    with fd:
        for line in fd:
            if line.startswith("#"):
                continue
            if line.startswith("g/h"):
                assert filename.stem.endswith("coeffs")
                metadata = _metadata_from_txt_header(line)
                metadata.Name = filename.stem[:-6]
                break
        else:
            raise RuntimeError(f"header line not found in {filename}")

        years = metadata.get_years()
        dtype = np.dtype(
            [
                ("type", "S1"),
                ("n", "int"),
                ("m", "int"),
            ]
            + [(f"{year}", "float64") for year in years]
            + [("rate", "float64")]
        )
        coeffs = np.loadtxt(fd, dtype=dtype)

    lines = np.max(coeffs["n"])
    cols = np.max(coeffs["m"])

    g_idx = coeffs["type"] == b"g"
    g_coeff = coeffs[g_idx]
    h_idx = coeffs["type"] == b"h"
    h_coeff = coeffs[h_idx]

    data = OrderedDict()
    for year in years:
        cosine_coef = np.zeros((lines + 1, cols + 1))
        cosine_coef[g_coeff["n"], g_coeff["m"]] = g_coeff[str(year)]

        sine_coef = np.zeros((lines + 1, cols + 1))
        sine_coef[h_coeff["n"], h_coeff["m"]] = h_coeff[str(year)]

        data[str(year)] = SphCoeffSet(cosine_coef, sine_coef)

    cosine_coef = np.zeros((lines + 1, cols + 1))
    cosine_coef[g_coeff["n"], g_coeff["m"]] = g_coeff["rate"]

    sine_coef = np.zeros((lines + 1, cols + 1))
    sine_coef[h_coeff["n"], h_coeff["m"]] = h_coeff["rate"]

    data["rate"] = SphCoeffSet(cosine_coef, sine_coef)

    return WmmData.from_metadata_and_coeffs(metadata, data)
