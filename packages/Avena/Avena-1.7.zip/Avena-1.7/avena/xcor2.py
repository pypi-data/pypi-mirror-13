#!/usr/bin/env python

"""Cross-correlation of image arrays."""


try:
    from itertools import izip as zip
except ImportError:
    pass
import numpy
from numpy import fft

from . import filter, image, np, tile


_DETREND_FACTOR = 0.10


def _detrend_filter(array):
    m, n = array.shape
    r = int(numpy.sqrt(m * n) * _DETREND_FACTOR)
    f = filter._high_pass_filter((m, n), r)
    numpy.multiply(array, f, out=array)


def _xcor2_shape(shapes):
    shape1, shape2 = shapes
    a, b = shape1
    c, d = shape2
    return (a + c, b + d)


def _center(array, shape):
    m, n = array.shape
    a, b = shape
    i, j = (m - a) // 2, (n - b) // 2
    return array[i:(i + a), j:(j + b)]


def _xcor2(array1, array2):
    x = tile.tile9_periodic(array1)
    a, b = x.shape
    y = array2[::-1, ::-1]
    c, d = y.shape
    m, n = _xcor2_shape(((a, b), (c, d)))
    x = np._zeropad(x, (m, n))
    y = np._zeropad(y, (m, n))
    X = fft.rfft2(x)
    Y = fft.rfft2(y)
    X = fft.fftshift(X)
    Y = fft.fftshift(Y)
    _detrend_filter(X)
    _detrend_filter(Y)
    numpy.multiply(X, Y, out=X)
    X = fft.ifftshift(X)
    x = fft.irfft2(X, s=(m, n))
    z = _center(x, (a // 3 + c, b // 3 + d))
    z = _center(z, (a // 3, b // 3))
    return z


def xcor2(array1, array2):
    """Compute the cross-correlation of two image arrays."""
    assert array1.dtype == array2.dtype
    z = numpy.ones(array1.shape[:2], dtype=array1.dtype)
    channel_pairs = zip(
        image.get_channels(array1),
        image.get_channels(array2),
    )
    for (xi, yi) in channel_pairs:
        xcori = _xcor2(xi, yi)
        numpy.multiply(z, xcori, out=z)
    return z


if __name__ == '__main__':
    pass
