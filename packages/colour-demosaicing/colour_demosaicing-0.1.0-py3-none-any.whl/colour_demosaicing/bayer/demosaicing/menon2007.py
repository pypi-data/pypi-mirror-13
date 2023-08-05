#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
DDFAPD - Menon (2007) Bayer CFA Demosaicing
===========================================

*Bayer* CFA (Colour Filter Array) DDFAPD - Menon (2007) demosaicing.

References
----------
.. [1]  Menon, D., Andriani, S., & Calvagno, G. (2007). Demosaicing with
        directional filtering and a posteriori decision. IEEE Transactions on
        Image Processing, 16(1), 132–141. doi:10.1109/TIP.2006.884928
"""

from __future__ import division, unicode_literals

import numpy as np
from scipy.ndimage.filters import convolve, convolve1d

from colour import tsplit, tstack

from colour_demosaicing.bayer import masks_CFA_Bayer

__author__ = 'Colour Developers'
__copyright__ = 'Copyright (C) 2015 - Colour Developers'
__license__ = 'New BSD License - http://opensource.org/licenses/BSD-3-Clause'
__maintainer__ = 'Colour Developers'
__email__ = 'colour-science@googlegroups.com'
__status__ = 'Production'

__all__ = ['demosaicing_CFA_Bayer_Menon2007',
           'demosaicing_CFA_Bayer_DDFAPD',
           'refining_step_Menon2007']

_cnv_h = lambda x, y: convolve1d(x, y, mode='mirror')
"""
Helper function for horizontal convolution.

_cnv_h : lambda
"""

_cnv_v = lambda x, y: convolve1d(x, y, mode='mirror', axis=0)
"""
Helper function for vertical convolution.

_cnv_v : lambda
"""


def demosaicing_CFA_Bayer_Menon2007(CFA, pattern='RGGB', refining_step=True):
    """
    Returns the demosaiced *RGB* colourspace array from given *Bayer* CFA using
    DDFAPD - Menon (2007) demosaicing algorithm.

    Parameters
    ----------
    CFA : array_like
        *Bayer* CFA.
    pattern : unicode, optional
        **{'RGGB', 'BGGR', 'GRBG', 'GBRG'}**
        Arrangement of the colour filters on the pixel array.
    refining_step : bool
        Perform refining step.

    Returns
    -------
    ndarray
        *RGB* colourspace array.

    Examples
    --------
    >>> CFA = np.array([[ 0.30980393,  0.36078432,  0.30588236,  0.3764706 ],
    ...                 [ 0.35686275,  0.39607844,  0.36078432,  0.40000001]])
    >>> demosaicing_CFA_Bayer_Menon2007(CFA)
    array([[[ 0.30980393,  0.35686275,  0.39215687],
            [ 0.30980393,  0.36078432,  0.39607844],
            [ 0.30588236,  0.36078432,  0.39019608],
            [ 0.32156864,  0.3764706 ,  0.40000001]],
    <BLANKLINE>
           [[ 0.30980393,  0.35686275,  0.39215687],
            [ 0.30980393,  0.36078432,  0.39607844],
            [ 0.30588236,  0.36078432,  0.39019609],
            [ 0.32156864,  0.3764706 ,  0.40000001]]])
    >>> CFA = np.array([[ 0.3764706 ,  0.36078432,  0.40784314,  0.3764706 ],
    ...                 [ 0.35686275,  0.30980393,  0.36078432,  0.29803923]])
    >>> demosaicing_CFA_Bayer_Menon2007(CFA, 'BGGR')
    array([[[ 0.30588236,  0.35686275,  0.3764706 ],
            [ 0.30980393,  0.36078432,  0.39411766],
            [ 0.29607844,  0.36078432,  0.40784314],
            [ 0.29803923,  0.3764706 ,  0.42352942]],
    <BLANKLINE>
           [[ 0.30588236,  0.35686275,  0.3764706 ],
            [ 0.30980393,  0.36078432,  0.39411766],
            [ 0.29607844,  0.36078432,  0.40784314],
            [ 0.29803923,  0.3764706 ,  0.42352942]]])
    """

    CFA = np.asarray(CFA)
    R_m, G_m, B_m = masks_CFA_Bayer(CFA.shape, pattern)

    h_0 = np.array([0, 0.5, 0, 0.5, 0])
    h_1 = np.array([-0.25, 0, 0.5, 0, -0.25])

    R = CFA * R_m
    G = CFA * G_m
    B = CFA * B_m

    G_H = np.where(G == 0, _cnv_h(CFA, h_0) + _cnv_h(CFA, h_1), G)
    G_V = np.where(G == 0, _cnv_v(CFA, h_0) + _cnv_v(CFA, h_1), G)

    C_H = np.where(R_m == 1, R - G_H, 0)
    C_H = np.where(B_m == 1, B - G_H, C_H)

    C_V = np.where(R_m == 1, R - G_V, 0)
    C_V = np.where(B_m == 1, B - G_V, C_V)

    D_H = np.abs(C_H -
                 np.pad(C_H, ((0, 0), (0, 2)), mode=str('reflect'))[:, 2:])
    D_V = np.abs(C_V -
                 np.pad(C_V, ((0, 2), (0, 0)), mode=str('reflect'))[2:, :])

    k = np.array(
        [[0, 0, 1, 0, 1],
         [0, 0, 0, 1, 0],
         [0, 0, 3, 0, 3],
         [0, 0, 0, 1, 0],
         [0, 0, 1, 0, 1]])

    d_H = convolve(D_H, k, mode='constant')
    d_V = convolve(D_V, np.transpose(k), mode='constant')

    mask = d_V >= d_H
    G = np.where(mask, G_H, G_V)
    M = np.where(mask, 1, 0)

    # Red rows.
    R_r = np.transpose(np.any(R_m == 1, axis=1)[np.newaxis]) * np.ones(R.shape)
    # Blue rows.
    B_r = np.transpose(np.any(B_m == 1, axis=1)[np.newaxis]) * np.ones(B.shape)

    k_b = np.array([0.5, 0, 0.5])

    R = np.where(np.logical_and(G_m == 1, R_r == 1),
                 G + _cnv_h(R, k_b) - _cnv_h(G, k_b),
                 R)

    R = np.where(np.logical_and(G_m == 1, B_r == 1) == 1,
                 G + _cnv_v(R, k_b) - _cnv_v(G, k_b),
                 R)

    B = np.where(np.logical_and(G_m == 1, B_r == 1),
                 G + _cnv_h(B, k_b) - _cnv_h(G, k_b),
                 B)

    B = np.where(np.logical_and(G_m == 1, R_r == 1) == 1,
                 G + _cnv_v(B, k_b) - _cnv_v(G, k_b),
                 B)

    R = np.where(np.logical_and(B_r == 1, B_m == 1),
                 np.where(M == 1,
                          B + _cnv_h(R, k_b) - _cnv_h(B, k_b),
                          B + _cnv_v(R, k_b) - _cnv_v(B, k_b)),
                 R)

    B = np.where(np.logical_and(R_r == 1, R_m == 1),
                 np.where(M == 1,
                          R + _cnv_h(B, k_b) - _cnv_h(R, k_b),
                          R + _cnv_v(B, k_b) - _cnv_v(R, k_b)),
                 B)

    RGB = tstack((R, G, B))

    if refining_step:
        RGB = refining_step_Menon2007(RGB, tstack((R_m, G_m, B_m)), M)

    return RGB


demosaicing_CFA_Bayer_DDFAPD = demosaicing_CFA_Bayer_Menon2007


def refining_step_Menon2007(RGB, RGB_m, M):
    """
    Performs the refining step on given *RGB* colourspace array.

    Parameters
    ----------
    RGB : array_like
        *RGB* colourspace array.
    RGB_m : array_like
        *Bayer* CFA red, green and blue masks.
    M : array_like
        Estimation for the best directional reconstruction.

    Returns
    -------
    ndarray
        Refined *RGB* colourspace array.

    Examples
    --------
    >>> RGB = np.array([[[0.30588236, 0.35686275, 0.3764706],
    ...                  [0.30980393, 0.36078432, 0.39411766],
    ...                  [0.29607844, 0.36078432, 0.40784314],
    ...                  [0.29803923, 0.3764706, 0.42352942]],
    ...                 [[0.30588236, 0.35686275, 0.3764706],
    ...                  [0.30980393, 0.36078432, 0.39411766],
    ...                  [0.29607844, 0.36078432, 0.40784314],
    ...                  [0.29803923, 0.3764706, 0.42352942]]])
    >>> RGB_m = np.array([[[0, 0, 1],
    ...                    [0, 1, 0],
    ...                    [0, 0, 1],
    ...                    [0, 1, 0]],
    ...                   [[0, 1, 0],
    ...                    [1, 0, 0],
    ...                    [0, 1, 0],
    ...                    [1, 0, 0]]])
    >>> M = np.array([[0, 1, 0, 1],
    ...               [1, 0, 1, 0]])
    >>> refining_step_Menon2007(RGB, RGB_m, M)
    array([[[ 0.30588236,  0.35686275,  0.3764706 ],
            [ 0.30980393,  0.36078432,  0.39411765],
            [ 0.29607844,  0.36078432,  0.40784314],
            [ 0.29803923,  0.3764706 ,  0.42352942]],
    <BLANKLINE>
           [[ 0.30588236,  0.35686275,  0.3764706 ],
            [ 0.30980393,  0.36078432,  0.39411766],
            [ 0.29607844,  0.36078432,  0.40784314],
            [ 0.29803923,  0.3764706 ,  0.42352942]]])
    """

    R, G, B = tsplit(RGB)
    R_m, G_m, B_m = tsplit(RGB_m)
    M = np.asarray(M)

    # Updating of the green component.
    R_G = R - G
    B_G = B - G

    FIR = np.ones(3) / 3

    B_G_m = np.where(B_m == 1,
                     np.where(M == 1, _cnv_h(B_G, FIR), _cnv_v(B_G, FIR)), 0)
    R_G_m = np.where(R_m == 1,
                     np.where(M == 1, _cnv_h(R_G, FIR), _cnv_v(R_G, FIR)), 0)

    G = np.where(R_m == 1, R - R_G_m, G)
    G = np.where(B_m == 1, B - B_G_m, G)

    # Updating of the red and blue components in the green locations.
    # Red rows.
    R_r = np.transpose(np.any(R_m == 1, axis=1)[np.newaxis]) * np.ones(R.shape)
    # Red columns.
    R_c = np.any(R_m == 1, axis=0)[np.newaxis] * np.ones(R.shape)
    # Blue rows.
    B_r = np.transpose(np.any(B_m == 1, axis=1)[np.newaxis]) * np.ones(B.shape)
    # Blue columns
    B_c = np.any(B_m == 1, axis=0)[np.newaxis] * np.ones(B.shape)

    R_G = R - G
    B_G = B - G

    k_b = np.array([0.5, 0, 0.5])

    R_G_m = np.where(np.logical_and(G_m == 1, B_r == 1),
                     _cnv_v(R_G, k_b),
                     R_G_m)
    R = np.where(np.logical_and(G_m == 1, B_r == 1), G + R_G_m, R)
    R_G_m = np.where(np.logical_and(G_m == 1, B_c == 1),
                     _cnv_h(R_G, k_b),
                     R_G_m)
    R = np.where(np.logical_and(G_m == 1, B_c == 1), G + R_G_m, R)

    B_G_m = np.where(np.logical_and(G_m == 1, R_r == 1),
                     _cnv_v(B_G, k_b),
                     B_G_m)
    B = np.where(np.logical_and(G_m == 1, R_r == 1), G + B_G_m, B)
    B_G_m = np.where(np.logical_and(G_m == 1, R_c == 1),
                     _cnv_h(B_G, k_b),
                     B_G_m)
    B = np.where(np.logical_and(G_m == 1, R_c == 1), G + B_G_m, B)

    # Updating of the red (blue) component in the blue (red) locations.
    R_B = R - B
    R_B_m = np.where(B_m == 1,
                     np.where(M == 1, _cnv_h(R_B, FIR), _cnv_v(R_B, FIR)), 0)
    R = np.where(B_m == 1, B + R_B_m, R)

    R_B_m = np.where(R_m == 1,
                     np.where(M == 1, _cnv_h(R_B, FIR), _cnv_v(R_B, FIR)), 0)
    B = np.where(R_m == 1, R - R_B_m, B)

    return tstack((R, G, B))
