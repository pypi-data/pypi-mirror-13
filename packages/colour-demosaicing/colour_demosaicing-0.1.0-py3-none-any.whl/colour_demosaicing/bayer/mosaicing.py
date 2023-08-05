#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Bayer CFA Mosaicing
===================

*Bayer* CFA (Colour Filter Array) data generation.
"""

from __future__ import division, unicode_literals

import numpy as np

from colour import tsplit

from colour_demosaicing.bayer import masks_CFA_Bayer

__author__ = 'Colour Developers'
__copyright__ = 'Copyright (C) 2015 - Colour Developers'
__license__ = 'New BSD License - http://opensource.org/licenses/BSD-3-Clause'
__maintainer__ = 'Colour Developers'
__email__ = 'colour-science@googlegroups.com'
__status__ = 'Production'

__all__ = ['mosaicing_CFA_Bayer']


def mosaicing_CFA_Bayer(RGB, pattern='RGGB'):
    """
    Returns the *Bayer* CFA mosaic for a given *RGB* colourspace array.

    Parameters
    ----------
    RGB : array_like
        *RGB* colourspace array.
    pattern : unicode, optional
        **{'RGGB', 'BGGR', 'GRBG', 'GBRG'}**
        Arrangement of the colour filters on the pixel array.

    Returns
    -------
    ndarray
        *Bayer* CFA mosaic.

    Examples
    --------
    >>> RGB = np.array([[[0, 1, 2],
    ...                  [0, 1, 2]],
    ...                 [[0, 1, 2],
    ...                  [0, 1, 2]]])
    >>> mosaicing_CFA_Bayer(RGB)
    array([[0, 1],
           [1, 2]])
    >>> mosaicing_CFA_Bayer(RGB, pattern='BGGR')
    array([[2, 1],
           [1, 0]])
    """

    RGB = np.asarray(RGB)

    R, G, B = tsplit(RGB)
    R_m, G_m, B_m = masks_CFA_Bayer(RGB.shape[0:2], pattern)

    CFA = R * R_m + G * G_m + B * B_m

    return CFA
