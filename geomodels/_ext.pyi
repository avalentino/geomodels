import enum
from typing import NamedTuple

import numpy as np
from numpy import typing as npt

from ._typing import PathType

class VersionInfo(NamedTuple):
    major: int
    minor: int
    micro: int

def lib_version_info() -> VersionInfo: ...
def lib_version_str() -> str: ...

class EHeightConvDir(enum.IntEnum):
    ELLIPSOIDTOGEOID = -1
    NONE = 0
    GEOIDTOELLIPSOID = 1

class GeoidModel:
    def __init__(
        self,
        name: str | None = None,
        path: PathType = "",
        *,
        cubic: bool = True,
        threadsafe: bool = False,
    ): ...
    def cache_area(
        self, south: float, west: float, north: float, east: float
    ) -> None: ...
    def cache_all(self) -> None: ...
    def cache_clear(self) -> None: ...
    def __call__(
        self, lat: npt.ArrayLike, lon: npt.ArrayLike
    ) -> np.ndarray: ...
    def convert_height(
        self,
        lat: npt.ArrayLike,
        lon: npt.ArrayLike,
        h: npt.ArrayLike,
        direction: EHeightConvDir,
    ) -> np.ndarray: ...
    def description(self) -> str: ...
    def datetime(self) -> str: ...
    def geoid_file(self) -> str: ...
    def geoid_name(self) -> str: ...
    def geoid_directory(self) -> str: ...
    def interpolation(self) -> str: ...
    def max_error(self) -> float: ...
    def rms_error(self) -> float: ...
    def offset(self) -> float: ...
    def scale(self) -> float: ...
    def threadsafe(self) -> bool: ...
    def cache(self) -> bool: ...
    def cache_west(self) -> float: ...
    def cache_east(self) -> float: ...
    def cache_north(self) -> float: ...
    def cache_south(self) -> float: ...
    def equatorial_radius(self) -> float: ...
    def flattening(self) -> float: ...
    @staticmethod
    def default_geoid_path() -> str: ...
    @staticmethod
    def default_geoid_name() -> str: ...

class GravityModel:
    def __init__(
        self,
        name: str | None = None,
        path: PathType = "",
        max_degree: int = -1,
        max_order: int = -1,
    ): ...
    def gravity(
        self, lat: npt.ArrayLike, lon: npt.ArrayLike, h: npt.ArrayLike
    ) -> tuple[
        np.ndarray,
        np.ndarray,
        np.ndarray,
        np.ndarray,
    ]: ...
    def disturbance(
        self,
        lat: npt.ArrayLike,
        lon: npt.ArrayLike,
        h: npt.ArrayLike,
    ) -> tuple[
        np.ndarray,
        np.ndarray,
        np.ndarray,
        np.ndarray,
    ]: ...
    def geoid_height(
        self, lat: npt.ArrayLike, lon: npt.ArrayLike
    ) -> np.ndarray: ...
    def spherical_anomaly(
        self, lat: npt.ArrayLike, lon: npt.ArrayLike, h: npt.ArrayLike
    ) -> tuple[
        np.ndarray,
        np.ndarray,
        np.ndarray,
    ]: ...
    def w(
        self, lat: npt.ArrayLike, lon: npt.ArrayLike, h: npt.ArrayLike
    ) -> tuple[
        np.ndarray,
        np.ndarray,
        np.ndarray,
        np.ndarray,
    ]: ...
    def v(self, x: npt.ArrayLike, y: npt.ArrayLike, z: npt.ArrayLike) -> tuple[
        np.ndarray,
        np.ndarray,
        np.ndarray,
        np.ndarray,
    ]: ...
    def t_components(
        self, x: npt.ArrayLike, y: npt.ArrayLike, z: npt.ArrayLike
    ) -> tuple[
        np.ndarray,
        np.ndarray,
        np.ndarray,
        np.ndarray,
    ]: ...
    def t(
        self, x: npt.ArrayLike, y: npt.ArrayLike, z: npt.ArrayLike
    ) -> np.ndarray: ...
    def u(self, x: npt.ArrayLike, y: npt.ArrayLike, z: npt.ArrayLike) -> tuple[
        np.ndarray,
        np.ndarray,
        np.ndarray,
        np.ndarray,
    ]: ...
    def phi(self, x: npt.ArrayLike, y: npt.ArrayLike) -> tuple[
        np.ndarray,
        np.ndarray,
        np.ndarray,
    ]: ...
    def description(self) -> str: ...
    def datetime(self) -> str: ...
    def gravity_file(self) -> str: ...
    def gravity_model_name(self) -> str: ...
    def gravity_model_directory(self) -> str: ...
    def equatorial_radius(self) -> float: ...
    def flattening(self) -> float: ...
    def mass_constant(self) -> float: ...
    def reference_mass_constant(self) -> float: ...
    def angular_velocity(self) -> float: ...
    def degree(self) -> int: ...
    def order(self) -> int: ...
    @staticmethod
    def default_gravity_path() -> str: ...
    @staticmethod
    def default_gravity_name() -> str: ...

class MagneticFieldModel:
    def __init__(self, name: str | None = None, path: PathType = ""): ...
    def __call__(
        self,
        t: float,
        lat: npt.ArrayLike,
        lon: npt.ArrayLike,
        h: npt.ArrayLike,
        rate: bool = False,
    ) -> (
        tuple[
            np.ndarray,
            np.ndarray,
            np.ndarray,
        ]
        | tuple[
            np.ndarray,
            np.ndarray,
            np.ndarray,
            np.ndarray,
            np.ndarray,
            np.ndarray,
        ]
    ): ...
    @staticmethod
    def field_components(
        Bx: npt.ArrayLike, By: npt.ArrayLike, Bz: npt.ArrayLike
    ) -> tuple[
        np.ndarray,
        np.ndarray,
        np.ndarray,
        np.ndarray,
    ]: ...
    def description(self) -> str: ...
    def datetime(self) -> str: ...
    def magnetic_file(self) -> str: ...
    def magnetic_model_name(self) -> str: ...
    def magnetic_model_directory(self) -> str: ...
    def min_height(self) -> float: ...
    def max_height(self) -> float: ...
    def min_time(self) -> float: ...
    def max_time(self) -> float: ...
    def equatorial_radius(self) -> float: ...
    def flattening(self) -> float: ...
    def degree(self) -> int: ...
    def order(self) -> int: ...
    @staticmethod
    def default_magnetic_path() -> str: ...
    @staticmethod
    def default_magnetic_name() -> str: ...
