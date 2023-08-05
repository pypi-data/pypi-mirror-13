#!/usr/bin/env python

"""Interpolation of image arrays in the frequency domain."""


import functools
import numpy
from numpy import fft

from . import filter, map, tile


def _interp2_shape(factor, shape):
    m, n = shape
    p, q = int(m * factor), int(n * factor)
    return (p, q)


def _mirror(array):
    m, n = array.shape
    r = int(numpy.ceil(numpy.sqrt((m / 2.0) ** 2 + (n / 2.0) ** 2)))
    x = tile._tile9_periodic(array)
    f = filter._low_pass_filter(x.shape, r)
    numpy.multiply(x, f, out=x)
    i, j = (3 * m - 2 * r) // 2, (3 * n - 2 * r) // 2
    z = x[i:(i + 2 * r), j:(j + 2 * r)]
    return z


def _interp2(factor, array):
    x = _mirror(array)
    m, n = x.shape
    p, q = _interp2_shape(factor, (m, n))
    X = fft.fft2(x)
    X = fft.fftshift(X)
    Z = numpy.zeros((p, q), dtype=numpy.complex64)
    i, j = (p - m) // 2, (q - n) // 2
    Z[i:(i + m), j:(j + n)] = X[:, :]
    Z = fft.ifftshift(Z)
    z = fft.ifft2(Z, s=(p, q))
    z = numpy.real(z)
    m, n = _interp2_shape(factor, array.shape)
    i, j = int(numpy.ceil((p - m) / 2.0)), int(numpy.ceil((q - n) / 2.0))
    z = z[i:(i + m), j:(j + n)]
    return z


def interp2(img, factor, tiles=None):
    """Interpolate a 2D image array by a given factor."""
    if tiles:
        __interp2 = functools.partial(
            map._map_to_tiles,
            tiles,
            functools.partial(_interp2, factor),
        )
    else:
        __interp2 = functools.partial(_interp2, factor)
    return map.map_to_channels(__interp2, img)


if '__main__' in __name__:
    pass
