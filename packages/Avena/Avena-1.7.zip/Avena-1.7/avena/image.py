#!/usr/bin/env python

"""Read and write image files as NumPy arrays."""


import numpy
import os
from PIL import Image

from . import np, utils


_PIL_RGB = {
    'R': 0,
    'G': 1,
    'B': 2,
}


def get_channels(img):
    """Return a list of channels of an image array."""
    if utils.depth(img) == 1:
        yield img
    else:
        for i in range(utils.depth(img)):
            yield img[:, :, i]


def read(filename):
    """Read an image file as an array."""
    img = Image.open(filename)
    arr = np.from_uint8(numpy.array(img))
    utils.swap_rgb(arr, _PIL_RGB, to=utils._PREFERRED_RGB)
    return arr


def _pil_save(img, filename):
    pil_img = Image.fromarray(img)
    pil_img.save(filename)
    return


def save(img, filename, random=False, ext=None, normalize=True):
    """Save an image array and return its path."""
    if random:
        newfile = utils.rand_filename(filename, ext=ext)
    else:
        file_name, file_ext = os.path.splitext(filename)
        newfile = file_name + (ext or file_ext)
    utils.swap_rgb(img, utils._PREFERRED_RGB, to=_PIL_RGB)
    save_img = numpy.copy(img)
    if normalize:
        np.normalize(save_img)
    np.clip(save_img, np._dtype_bounds[str(save_img.dtype)])
    uint8img = np.to_uint8(save_img)
    _pil_save(uint8img, newfile)
    return newfile


if __name__ == '__main__':
    pass
