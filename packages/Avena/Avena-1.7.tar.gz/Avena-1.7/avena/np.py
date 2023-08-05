#!/usr/bin/env python

import numpy
import sys


_eps = 10.0 * sys.float_info.epsilon

# Map of NumPy array type strings to types
_np_dtypes = {
    'int8':     numpy.int8,
    'int16':    numpy.int16,
    'int32':    numpy.int32,
    'int64':    numpy.int64,
    'uint8':    numpy.uint8,
    'uint16':   numpy.uint16,
    'uint32':   numpy.uint32,
    'uint64':   numpy.uint64,
    'float32':  numpy.float32,
    'float64':  numpy.float64,
}


_dtype_bounds = {
    'float32':  (0.0, 1.0),
    'float64':  (0.0, 1.0),
    'uint8':    (0, 255),
}


def from_uint8(array):
    float_array = array.astype(numpy.float32)
    float_array *= 1.0 / 256.0
    return float_array


def to_uint8(array):
    float_array = numpy.around(array * 255.0)
    uint8_array = float_array.astype(numpy.uint8)
    return uint8_array


def clip(array, bounds):
    """Clip the values of an array to the given interval."""
    (min, max) = bounds
    x = array < min + _eps
    y = array > max - _eps
    array[x] = min
    array[y] = max
    return


def normalize(array):
    """Normalize an array to the interval [0,1]."""
    mu = numpy.mean(array)
    rho2 = numpy.std(array)
    min = mu - 1.5 * rho2
    max = mu + 1.5 * rho2
    array -= min
    if max - min > _eps:
        array /= max - min
    return


def peak(array):
    """Return the index of the peak value of an array."""
    return numpy.unravel_index(numpy.argmax(array), array.shape)


def _zeropad(array, size):
    m, n = array.shape
    p, q = size
    z = numpy.zeros((p, q), dtype=array.dtype)
    z[:m, :n] = array
    return z


if __name__ == '__main__':
    pass
