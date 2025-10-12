"""Internal utilities."""

import numpy as np


def as_contiguous_1d_llh(lat, lon, height, dtype=np.float64):
    """Return lat, lon and h as contiguous arrays of the specified data type.

    Shape consistency is checked and, in the case `h` is provided as scalar,
    a new array having the proper shape and `h` value is created and returned.

    :returns:
        lat, lon, height, shape
    """
    is_scalar = np.isscalar(lat)

    lat = np.asarray(lat)
    lon = np.asarray(lon)
    height = np.asarray(height)

    for name, param in (("lat", lat), ("lon", lon), ("h", height)):
        dt = param.dtype
        if not (
            np.issubdtype(dt, np.floating) or np.issubdtype(dt, np.integer)
        ):
            raise TypeError(f"{name}: {param!r}")

    shape = lat.shape
    if lon.shape != shape or (height.size > 1 and height.shape != shape):
        raise ValueError("lat, lon and h shall have the same shape")

    size = lat.size

    lat = np.ascontiguousarray(lat.reshape([size]), dtype=dtype)
    lon = np.ascontiguousarray(lon.reshape([size]), dtype=dtype)
    if height.size > 1:
        height = np.ascontiguousarray(height.reshape([size]), dtype=dtype)
    else:
        height = np.full([size], height.item(), dtype)

    shape = shape if not is_scalar else None

    return lat, lon, height, shape


def as_contiguous_1d_components(*args, labels=None, dtype=np.float64):
    """Return the inputs as contiguous arrays of the specified data type."""
    if labels is None:
        labels = [f"component_{i}" for i in range(len(args))]

    is_scalar = np.isscalar(args[0])

    arglist = [np.asarray(item) for item in args]

    shape: tuple | None = arglist[0].shape
    for name, param in zip(labels, arglist, strict=True):
        dt = param.dtype
        if not (
            np.issubdtype(dt, np.floating) or np.issubdtype(dt, np.integer)
        ):
            raise TypeError(f"{name}: {param!r}")

        if param.shape != shape:
            raise ValueError("not all components have the same shape")

    size = arglist[0].size
    for i in range(len(arglist)):
        arglist[i] = np.ascontiguousarray(
            arglist[i].reshape([size]), dtype=dtype
        )

    shape = shape if not is_scalar else None

    return arglist + [shape]


def reshape_components(shape, *args) -> np.ndarray | list[np.ndarray]:
    """Reshape all args to the specified shape."""
    is_scalar = shape is None

    if is_scalar:
        argslist = [item.item() for item in args]
    else:
        argslist = [item.reshape(shape) for item in args]

    if len(argslist) == 1:
        return argslist[0]

    return argslist
