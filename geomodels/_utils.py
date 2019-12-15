# -*- coding: utf-8 -*-

"""Internal utilities."""

import numpy as np


def as_contiguous_1d_llh(lat, lon, h, dtype=np.float64):
    is_scalar = np.isscalar(lat)

    lat = np.asarray(lat)
    lon = np.asarray(lon)
    h = np.asarray(h)

    for name, param in (('lat', lat), ('lon', lon), ('h', h)):
        dt = param.dtype
        if not (np.issubdtype(dt, np.floating) or
                np.issubdtype(dt, np.integer)):
            raise TypeError('{}: {!r}}'.format(name, param))

    shape = lat.shape
    if lon.shape != shape or (h.size > 1 and h.shape != shape):
        raise ValueError('lat, lon and h shall have the same shape')

    size = lat.size

    lat = np.ascontiguousarray(lat.reshape([size]), dtype=dtype)
    lon = np.ascontiguousarray(lon.reshape([size]), dtype=dtype)
    if h.size > 1:
        h = np.ascontiguousarray(h.reshape([size]), dtype=dtype)
    else:
        h = np.full([size], h, dtype)

    shape = shape if not is_scalar else None

    return lat, lon, h, shape


def as_contiguous_1d_components(*args, labels=None, dtype=np.float64):
    if labels is None:
        labels = [f'component_{i}' for i in range(len(args))]

    is_scalar = np.isscalar(args[0])

    args = list(args)
    for i in range(len(args)):
        args[i] = np.asarray(args[i])

    shape = args[0].shape
    for name, param in zip(labels, args):
        dt = param.dtype
        if not (np.issubdtype(dt, np.floating) or
                np.issubdtype(dt, np.integer)):
            raise TypeError('{}: {!r}}'.format(name, param))

        if param.shape != shape:
            raise ValueError('not all components have the same shape')

    size = args[0].size
    for i in range(len(args)):
        args[i] = np.ascontiguousarray(args[i].reshape([size]), dtype=dtype)

    shape = shape if not is_scalar else None

    return args + [shape]


def reshape_components(shape, *args):
    is_scalar = True if shape is None else False

    if is_scalar:
        args = [item.item() for item in args]
    else:
        args = [item.reshape(shape) for item in args]

    if len(args) == 1:
        args = args[0]

    return args